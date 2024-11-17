import uuid

from fastapi import APIRouter

import db
from entities.model import TUser
from model.user import User

router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
def create_user(user: User):
    # with Session(db.engine) as session, session.begin():
    with db.session_scope() as s_:
        user1 = TUser(id=uuid.uuid4(), dfname=user.dfname, dfemail=user.dfemail, dfupdated_on=user.dfupdated_on)
        s_.add(user1)

    return user
