import uuid
from datetime import datetime
from random import randint

from sqlalchemy import select, func, or_, and_, ColumnElement, asc

import db
from entities.model import TRivalCouple
from websocket.connection_manager import ConnectionManager

state: dict = dict({
    'WAITING_FOR_ENEMY': 1,
    'SHIPS_POSITIONING': 2,
    'PLAYING': 3
})

player_available_condition: ColumnElement[bool] = or_(
    and_(TRivalCouple.dfplayer1.__ne__(None), TRivalCouple.dfplayer2.__eq__(None)),
    and_(TRivalCouple.dfplayer1.__eq__(None), TRivalCouple.dfplayer2.__ne__(None)),
)


def available_rival_couple_exists() -> bool:
    with db.session_scope() as s_:
        stmt = select(func.count(TRivalCouple.id)).where(player_available_condition)
        count = s_.execute(stmt).scalar()

        if count == 0:
            return False
        return True


def create_rival_couple(client_uuid, data_from_client):
    with db.session_scope() as s_:
        rival_couple_player: TRivalCouple = TRivalCouple(
            id=uuid.uuid4(),
            dfplayer1=client_uuid,
            dfplayer1_nickname=data_from_client['nickName'],
            dfplayer1_state=state['WAITING_FOR_ENEMY'],
            dfcreated_on=datetime.now(),
        )

        s_.add(rival_couple_player)


def find_available_rival_couple() -> TRivalCouple:
    with db.session_scope() as s_:
        stmt = select(TRivalCouple).where(player_available_condition).order_by(asc(TRivalCouple.dfcreated_on)).limit(1)
        return s_.execute(stmt).scalar()


def add_player_to_rival_couple(rc: TRivalCouple, client_uuid: uuid.UUID, data_from_client: dict):
    with db.session_scope() as s_:
        if not rc.dfplayer1:
            rc.dfplayer1 = client_uuid
            rc.dfplayer1_nickname = data_from_client['nickName']
            rc.dfplayer1_state = state['SHIPS_POSITIONING']
            rc.dfplayer2_state = state['SHIPS_POSITIONING']
        else:
            rc.dfplayer2 = client_uuid
            rc.dfplayer2_nickname = data_from_client['nickName']
            rc.dfplayer2_state = state['SHIPS_POSITIONING']
            rc.dfplayer1_state = state['SHIPS_POSITIONING']

        s_.add(rc)  # add to s_.dirty for subsequent commit to DB


def find_rival_couple_by_client_id(client_uuid: uuid.UUID) -> TRivalCouple:
    with db.session_scope() as s_:
        stmt = select(TRivalCouple).where(
            or_(
                TRivalCouple.dfplayer1.__eq__(client_uuid),
                TRivalCouple.dfplayer2.__eq__(client_uuid)
            )
        ).limit(1)  # запись в БД с таким фильтром по-хорошему должна быть только одна

        return s_.scalar(stmt)


async def delete_rival_couple_and_notify(client_uuid: uuid.UUID, manager: ConnectionManager):
    couple = find_rival_couple_by_client_id(client_uuid)

    if not couple:
        return

    with db.session_scope() as s_:
        if couple.dfplayer1 and couple.dfplayer2:
            if couple.dfplayer1 == client_uuid:  # если отключается player1, то оповещаем player2
                await manager.send_structured_data(couple.dfplayer2, 'disconnection',
                                                   {'enemy_nickname': couple.dfplayer1_nickname})
            else:  # и наоборот
                await manager.send_structured_data(couple.dfplayer1, 'disconnection',
                                                   {'enemy_nickname': couple.dfplayer2_nickname})

        s_.delete(couple)


async def process_data(client_uuid: uuid.UUID, data_from_client: dict, manager: ConnectionManager):
    msg_type = data_from_client['msg_type']

    if msg_type == 'random_game':
        if not available_rival_couple_exists():
            create_rival_couple(client_uuid, data_from_client)
        else:
            rc: TRivalCouple = find_available_rival_couple()
            add_player_to_rival_couple(rc, client_uuid, data_from_client)
            await manager.send_structured_data(rc.dfplayer1, msg_type, {'enemy_nickname': rc.dfplayer2_nickname})
            await manager.send_structured_data(rc.dfplayer2, msg_type, {'enemy_nickname': rc.dfplayer1_nickname})

    if msg_type == 'ships_are_arranged':
        print(f'Client {client_uuid} is ready to play!')
        rc = find_rival_couple_by_client_id(client_uuid)

        if not rc:
            return

        with db.session_scope() as s_:
            if rc.dfplayer1 == client_uuid:  # если первый игрок нажимает "Играть"
                rc.dfplayer1_state = state['PLAYING']
                await manager.send_structured_data(rc.dfplayer2, msg_type, {'enemy_client_id': str(rc.dfplayer1)})
            else:
                rc.dfplayer2_state = state['PLAYING']
                await manager.send_structured_data(rc.dfplayer1, msg_type, {'enemy_client_id': str(rc.dfplayer2)})

            #  Если оба игрока расставили корабли и нажали "Играть"
            #  отправляем каждому сообщение с msg_type = 'play', сигнализирующее о начале игры
            if rc.dfplayer1_state == state['PLAYING'] and rc.dfplayer2_state == state['PLAYING']:

                #  определяем кто из игроков ходит первый
                turn = randint(1, 2)
                if turn == 1:
                    await manager.send_structured_data(rc.dfplayer1, 'play', {'turn_to_shoot': True})
                    await manager.send_structured_data(rc.dfplayer2, 'play', {'turn_to_shoot': False})
                else:
                    await manager.send_structured_data(rc.dfplayer1, 'play', {'turn_to_shoot': False})
                    await manager.send_structured_data(rc.dfplayer2, 'play', {'turn_to_shoot': True})

            s_.add(rc)  # и обновляем запись в БД

    if msg_type == 'fire_request':
        print('(fire_request) data_from_client', data_from_client)

        #  какая-то логика

        await manager.send_structured_data(uuid.UUID(data_from_client['enemy_client_id']), msg_type,
                                           {'shot_location': data_from_client['shot_location']})

    if msg_type == 'fire_response':
        print('(fire_response) data_from_client', data_from_client)

        #  какая-то логика

        await manager.send_structured_data(uuid.UUID(data_from_client['enemy_client_id']), msg_type,
                                           {'shot_result': data_from_client['shot_result'],
                                            'edgeLocs': data_from_client['edgeLocs']},)
