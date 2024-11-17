import datetime
import uuid

from fastapi import APIRouter

import db
from entities.model import TGame, TUser
from model.game import Game

router = APIRouter(
    prefix="/game",
    tags=["Game"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
def create_game(game: Game):
    # with Session(db.engine) as session, session.begin():
    with db.session_scope() as s_:
        user1 = TUser(id=uuid.uuid4(), dfname='andrey_zelenyy', dfemail='test123@mail.com', dfupdated_on=datetime.datetime.now())
        s_.add(user1)
        s_.commit()
        game1 = TGame(id=uuid.uuid4(), dfstarted_on=game.dfstarted_on, dfduration=34, user_winner=user1.id)
        s_.add(game1)

    return game1
