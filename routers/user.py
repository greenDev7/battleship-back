import uuid

from fastapi import APIRouter
from sqlalchemy import select, func

import db
from model.user import User

router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={404: {"description": "Not found"}},
)


# @router.get('/exists')
# def does_nickname_exist_in_db(nick_name: str):
#     """Возвращает True, если данный никнейм есть в таблице активных игроков, иначе False"""
#     with db.session_scope() as s_:
#         stmt = select(func.count(TActiveUser.id)).where(TActiveUser.dfname == nick_name)
#         count = s_.execute(stmt).scalar()
#
#         if count > 0:
#             return True
#         return False


# @router.post("/")
# # def create_user(user: User):
# #     with db.session_scope() as s_:
# #         user1 = TUser(id=uuid.uuid4(), dfname=user.dfname, dfemail=user.dfemail, dfupdated_on=user.dfupdated_on)
# #         s_.add(user1)
# #
# #     return user
