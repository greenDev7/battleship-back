import uuid
from datetime import datetime

from sqlalchemy import select, func, and_

import db
from entities.model import TRivalCouple, TGameType
from helper.game_state import GameState
from helper.game_type import GameType


def friend_couple_exists(my_uuid: uuid.UUID, friend_uuid: uuid.UUID) -> bool:
    with db.session_scope() as s_:
        stmt = select(func.count(TRivalCouple.id)).join(TGameType, TRivalCouple.dfgame_type.__eq__(TGameType.id),
                                                        isouter=True).where(
            and_(TGameType.id.__eq__(GameType.FRIEND.value), TRivalCouple.dfplayer1 == friend_uuid,
                 TRivalCouple.dfplayer2 == my_uuid))
        count = s_.execute(stmt).scalar()

        if count == 0:
            return False
        return True


def create_friend_couple(client_uuid: uuid.UUID, data_from_client: dict):
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


def find_friend_couple() -> TRivalCouple:
    pass


def join_friend_couple(rc, client_uuid, data_from_client):
    pass


def process_friend_game_creation(client_uuid: uuid.UUID, data_from_client: dict):
    if not friend_couple_exists(client_uuid, data_from_client['friendUUID']):
        create_friend_couple(client_uuid, data_from_client)
    else:
        rc: TRivalCouple = find_friend_couple()
        join_friend_couple(rc, client_uuid, data_from_client)
        # await manager.send_structured_data(rc.dfplayer1, msg_type, {'enemy_nickname': rc.dfplayer2_nickname})
        # await manager.send_structured_data(rc.dfplayer2, msg_type, {'enemy_nickname': rc.dfplayer1_nickname})
