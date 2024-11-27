import uuid
from datetime import datetime
from typing import List

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


def find_rival_couple_by_client_id(client_uuid: uuid.UUID) -> List[TRivalCouple]:
    with db.session_scope() as s_:
        stmt = select(TRivalCouple).where(
            or_(
                TRivalCouple.dfplayer1.__eq__(client_uuid),
                TRivalCouple.dfplayer2.__eq__(client_uuid)
            )
        )

        return s_.scalars(stmt).all()


async def free_rival_couple_and_notify(client_uuid: uuid.UUID, manager: ConnectionManager):
    couples: List[TRivalCouple] = find_rival_couple_by_client_id(client_uuid)
    with db.session_scope() as s_:
        for rc in couples:
            s_.delete(rc)


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
