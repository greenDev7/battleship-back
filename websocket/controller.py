import uuid
from datetime import datetime
from random import randint

from sqlalchemy import select, func, or_, and_, ColumnElement, asc

import db
from entities.model import TRivalCouple, TGameType
from helper.game_state import GameState
from helper.game_type import GameType
from helper.message_type import MessageType
from websocket.connection_manager import ConnectionManager
from websocket.friend_game_controller import process_friend_game_creation

player_available_condition: ColumnElement[bool] = or_(
    and_(TRivalCouple.dfplayer1.__ne__(None), TRivalCouple.dfplayer2.__eq__(None)),
    and_(TRivalCouple.dfplayer1.__eq__(None), TRivalCouple.dfplayer2.__ne__(None)),
)

random_game_clause: ColumnElement[bool] = TGameType.id.__eq__(GameType.RANDOM.value)


def find_by_client_id_clause(client_uuid: uuid.UUID) -> ColumnElement[bool]:
    clause: ColumnElement[bool] = or_(
        TRivalCouple.dfplayer1.__eq__(client_uuid),
        TRivalCouple.dfplayer2.__eq__(client_uuid)
    )
    return clause


def available_random_couple_exists() -> bool:
    with db.session_scope() as s_:
        stmt = select(func.count(TRivalCouple.id)).join(TGameType, TRivalCouple.dfgame_type.__eq__(TGameType.id),
                                                        isouter=True).where(
            and_(player_available_condition, random_game_clause))
        count = s_.execute(stmt).scalar()

        if count == 0:
            return False
        return True


async def create_random_couple(client_uuid, data_from_client):
    with db.session_scope() as s_:
        rival_couple_player: TRivalCouple = TRivalCouple(
            id=uuid.uuid4(),
            dfplayer1=client_uuid,
            dfplayer1_nickname=data_from_client['nickName'],
            dfplayer1_state=GameState.SEARCHING_FOR_OPPONENT.value,
            dfcreated_on=datetime.now(),
            dfgame_type=GameType.RANDOM.value
        )

        s_.add(rival_couple_player)


def find_available_random_couple() -> TRivalCouple:
    with db.session_scope() as s_:
        stmt = select(TRivalCouple).join(TGameType, TRivalCouple.dfgame_type.__eq__(TGameType.id),
                                         isouter=True).where(player_available_condition, random_game_clause).order_by(
            asc(TRivalCouple.dfcreated_on)).limit(1)
        return s_.execute(stmt).scalar()


async def add_player_to_rival_couple(rc: TRivalCouple, client_uuid: uuid.UUID, data_from_client: dict):
    with db.session_scope() as s_:
        if not rc.dfplayer1:
            rc.dfplayer1 = client_uuid
            rc.dfplayer1_nickname = data_from_client['nickName']
            rc.dfplayer1_state = GameState.SHIPS_POSITIONING.value
            rc.dfplayer2_state = GameState.SHIPS_POSITIONING.value
        else:
            rc.dfplayer2 = client_uuid
            rc.dfplayer2_nickname = data_from_client['nickName']
            rc.dfplayer2_state = GameState.SHIPS_POSITIONING.value
            rc.dfplayer1_state = GameState.SHIPS_POSITIONING.value

        s_.add(rc)  # add to s_.dirty for subsequent commit to DB


def find_rival_couple_by_id(game_id: uuid.UUID) -> TRivalCouple:
    with db.session_scope() as s_:
        return s_.get(TRivalCouple, game_id)


def find_rival_couple_by_client_id(client_uuid: uuid.UUID) -> TRivalCouple:
    """
    Возвращает объект типа TRivalCouple по client_uuid
    :param client_uuid: уникальный идентификатор клиента (websocket-подключения)
    :return: сопернищающая пара (TRivalCouple)
    """
    with db.session_scope() as s_:
        # запись в БД с таким фильтром по-хорошему должна быть только одна
        stmt = select(TRivalCouple).where(find_by_client_id_clause(client_uuid)).limit(1)
        return s_.scalar(stmt)


async def delete_rival_couple_and_notify(client_uuid: uuid.UUID, manager: ConnectionManager):
    couple = find_rival_couple_by_client_id(client_uuid)

    if not couple:
        return

    with db.session_scope() as s_:
        if couple.dfplayer1 and couple.dfplayer2:
            if couple.dfplayer1 == client_uuid:  # если отключается player1, то оповещаем player2
                await manager.send_structured_data(couple.dfplayer2, MessageType.DISCONNECTION.value,
                                                   {'enemy_nickname': couple.dfplayer1_nickname})
            else:  # и наоборот
                await manager.send_structured_data(couple.dfplayer1, MessageType.DISCONNECTION.value,
                                                   {'enemy_nickname': couple.dfplayer2_nickname})

        s_.delete(couple)


async def process_data(client_uuid: uuid.UUID, data_from_client: dict, manager: ConnectionManager):
    msg_type = data_from_client['msg_type']

    if msg_type == MessageType.GAME_CREATION.value:
        if data_from_client['game_type'] == GameType.RANDOM.value:
            if not available_random_couple_exists():
                await create_random_couple(client_uuid, data_from_client)
            else:
                rc: TRivalCouple = find_available_random_couple()
                await add_player_to_rival_couple(rc, client_uuid, data_from_client)
                await manager.send_structured_data(rc.dfplayer1, msg_type,
                                                   {'enemy_nickname': rc.dfplayer2_nickname, 'gameId': str(rc.id)})
                await manager.send_structured_data(rc.dfplayer2, msg_type,
                                                   {'enemy_nickname': rc.dfplayer1_nickname, 'gameId': str(rc.id)})
        else:  # game_type == GameType.FRIEND.value:
            await process_friend_game_creation(client_uuid, data_from_client, manager)

    if msg_type == MessageType.SHIPS_ARE_ARRANGED.value:
        rc = find_rival_couple_by_id(data_from_client['game_id'])

        if not rc:
            return

        with db.session_scope() as s_:
            if rc.dfplayer1 == client_uuid:  # если первый игрок нажимает "Играть"
                rc.dfplayer1_state = GameState.PLAYING.value
                await manager.send_structured_data(rc.dfplayer2, msg_type, {'enemy_client_id': str(rc.dfplayer1)})
            else:
                rc.dfplayer2_state = GameState.PLAYING.value
                await manager.send_structured_data(rc.dfplayer1, msg_type, {'enemy_client_id': str(rc.dfplayer2)})

            #  Если оба игрока расставили корабли и нажали "Играть"
            #  отправляем каждому сообщение с msg_type = PLAY, сигнализирующее о начале игры
            if rc.dfplayer1_state == GameState.PLAYING.value and rc.dfplayer2_state == GameState.PLAYING.value:
                #  определяем кто из игроков ходит првым и оповещаем игроков
                turn = randint(1, 2)
                if turn == 1:
                    await manager.send_structured_data(rc.dfplayer1, MessageType.PLAY.value, {'turn_to_shoot': True})
                    await manager.send_structured_data(rc.dfplayer2, MessageType.PLAY.value, {'turn_to_shoot': False})
                else:
                    await manager.send_structured_data(rc.dfplayer1, MessageType.PLAY.value, {'turn_to_shoot': False})
                    await manager.send_structured_data(rc.dfplayer2, MessageType.PLAY.value, {'turn_to_shoot': True})

            s_.add(rc)  # и обновляем запись в БД

    if msg_type == MessageType.FIRE_REQUEST.value:
        await manager.send_structured_data(uuid.UUID(data_from_client['enemy_client_id']), msg_type,
                                           {'shot_location': data_from_client['shot_location']})

    if msg_type == MessageType.FIRE_RESPONSE.value:
        data_for_sending = {'shot_result': data_from_client['shot_result']}

        if 'sunkShip' in data_from_client:
            data_for_sending['sunkShip'] = data_from_client['sunkShip']

        await manager.send_structured_data(uuid.UUID(data_from_client['enemy_client_id']), msg_type,
                                           data_for_sending)

    if msg_type == MessageType.UNSUNK_SHIPS.value:
        await manager.send_structured_data(uuid.UUID(data_from_client['enemy_client_id']), msg_type,
                                           {'unSunkShips': data_from_client['unSunkShips']})

    if msg_type == MessageType.GAME_OVER.value:
        await manager.send_structured_data(uuid.UUID(data_from_client['enemy_client_id']), msg_type, data={})

    if msg_type == MessageType.PLAY_AGAIN.value:
        # оповестим игрока о том, что противник хочет сыграть с ним еще раз
        await manager.send_structured_data(uuid.UUID(data_from_client['enemy_client_id']), msg_type, {})
        rc = find_rival_couple_by_id(data_from_client['game_id'])

        if not rc:
            return

        with db.session_scope() as s_:
            sp: int = GameState.SHIPS_POSITIONING.value
            if rc.dfplayer1 == client_uuid:
                rc.dfplayer1_state = sp
            else:
                rc.dfplayer2_state = sp

            s_.add(rc)  # и обновляем запись в БД
