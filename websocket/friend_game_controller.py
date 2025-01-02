import uuid
from datetime import datetime
from random import randint

from sqlalchemy import select, func, and_

import db
from entities.model import TRivalCouple, TGameType
from helper.game_state import GameState
from helper.game_type import GameType
from websocket.connection_manager import ConnectionManager


def friend_couple_exists(client_uuid: uuid.UUID, friend_uuid: uuid.UUID) -> bool:
    with db.session_scope() as s_:
        stmt = select(func.count(TRivalCouple.id)).join(TGameType, TRivalCouple.dfgame_type.__eq__(TGameType.id),
                                                        isouter=True).where(
            and_(TGameType.id.__eq__(GameType.FRIEND.value), TRivalCouple.dfplayer1 == friend_uuid,
                 TRivalCouple.dfplayer2 == client_uuid))
        count = s_.execute(stmt).scalar()

        if count == 0:
            return False
        return True


async def create_friend_couple(client_uuid: uuid.UUID, data_from_client: dict):
    print('Создаем запись для игры с другом')
    with db.session_scope() as s_:
        rival_couple: TRivalCouple = TRivalCouple(
            id=uuid.uuid4(),
            dfplayer1=client_uuid,
            dfplayer1_nickname=data_from_client['nickName'],
            dfplayer1_state=GameState.WAITING_FOR_ENEMY.value,
            dfplayer2=data_from_client['friendUUID'],
            dfcreated_on=datetime.now(),
            dfgame_type=GameType.FRIEND.value
        )

        s_.add(rival_couple)


def find_friend_couple(client_uuid: uuid.UUID, friend_uuid: uuid.UUID) -> TRivalCouple:
    with db.session_scope() as s_:
        stmt = select(TRivalCouple).join(TGameType, TRivalCouple.dfgame_type.__eq__(TGameType.id),
                                         isouter=True).where(
            and_(
                TGameType.id.__eq__(GameType.FRIEND.value),
                TRivalCouple.dfplayer1.__eq__(friend_uuid),
                TRivalCouple.dfplayer2.__eq__(client_uuid)
            )
        ).limit(1)  # запись в БД с таким фильтром по-хорошему должна быть только одна

        return s_.scalar(stmt)


async def join_friend_couple(rc, nickname: str):
    print('Присоединяемся к игре')
    with db.session_scope() as s_:
        rc.dfplayer2_nickname = nickname
        rc.dfplayer1_state = GameState.PLAYING.value
        rc.dfplayer2_state = GameState.PLAYING.value

        s_.add(rc)  # add to s_.dirty for subsequent commit to DB


async def process_friend_game_creation(client_uuid: uuid.UUID, data_from_client: dict, manager: ConnectionManager):
    friend_uuid: uuid.UUID = data_from_client['friendUUID']

    if not friend_couple_exists(client_uuid, friend_uuid):
        await create_friend_couple(client_uuid, data_from_client)
    else:
        rc: TRivalCouple = find_friend_couple(client_uuid, friend_uuid)
        print('Запись для дружеской игры найдена')
        await join_friend_couple(rc, data_from_client['nickName'])

        #  определяем кто из игроков ходит первый
        turn = randint(1, 2)
        if turn == 1:
            await manager.send_structured_data(rc.dfplayer1, 'play',
                                               {'turn_to_shoot': True, 'enemy_nickname': rc.dfplayer2_nickname})
            await manager.send_structured_data(rc.dfplayer2, 'play',
                                               {'turn_to_shoot': False, 'enemy_nickname': rc.dfplayer1_nickname})
        else:
            await manager.send_structured_data(rc.dfplayer1, 'play',
                                               {'turn_to_shoot': False, 'enemy_nickname': rc.dfplayer2_nickname})
            await manager.send_structured_data(rc.dfplayer2, 'play',
                                               {'turn_to_shoot': True, 'enemy_nickname': rc.dfplayer1_nickname})
