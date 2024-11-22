import datetime
import uuid

import db
from entities.model import TUser

game_type: dict = dict({
    'RANDOM': 1,
    'FRIEND': 2,
    'COMPUTER': 3
})


def create_user(user_body: dict):
    with db.session_scope() as s_:
        user = TUser(id=uuid.uuid4(), dfname=user_body["nickName"],
                     dfcreated_on=datetime.datetime.now(),
                     dfgame_type=game_type[user_body["gameType"]])
        s_.add(user)