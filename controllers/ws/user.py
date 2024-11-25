import datetime
import uuid

from sqlalchemy import select, and_, desc

import db
from entities.model import TActiveUser

game_type: dict = dict({
    'RANDOM': 1,
    'FRIEND': 2,
    'COMPUTER': 3
})

active_user_state: dict = dict({
    'WAITING_FOR_ENEMY': 1,
    'SHIPS_POSITIONING': 2,
    'PLAYING': 3
})


def create_active_user(client_uuid: uuid.UUID, data_from_client: dict, client_ip: str, client_port: int):
    with db.session_scope() as s_:
        user = TActiveUser(id=client_uuid, dfname=data_from_client["nickName"],
                           dfcreated_on=datetime.datetime.now(),
                           dfgame_type=game_type[data_from_client["gameType"]],
                           dfstate=active_user_state['WAITING_FOR_ENEMY'],
                           dfclient_host_ip=client_ip,
                           dfclient_port=str(client_port))
        s_.add(user)


def get_active_user_nick_name_for_random_game(client_uuid: uuid.UUID) -> str:
    with db.session_scope() as s_:
        stmt = select(TActiveUser.dfname).where(
            and_(
                TActiveUser.id != client_uuid,
                TActiveUser.dfgame_type == game_type['RANDOM'],
                TActiveUser.dfstate == active_user_state['WAITING_FOR_ENEMY'],
            )
        ).order_by(desc(TActiveUser.dfcreated_on)).limit(1)

        nick_name = s_.execute(stmt).scalar()

        return nick_name
