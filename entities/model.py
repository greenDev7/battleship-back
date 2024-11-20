from datetime import datetime

from sqlalchemy import Uuid, DateTime, Integer, ForeignKey, String, SmallInteger
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    pass


class TGame(Base):
    __tablename__ = "tgame"

    id = mapped_column(Uuid, primary_key=True)
    dfstarted_on = mapped_column(DateTime, default=datetime(year=2000, month=1, day=1))
    dfduration = mapped_column(Integer, default=0)

    user_winner = mapped_column(ForeignKey("tuser.id"))
    user_loser = mapped_column(ForeignKey("tuser.id"))


class TUser(Base):
    __tablename__ = "tuser"

    id = mapped_column(Uuid, primary_key=True)
    dfcreated_on = mapped_column(DateTime, default=datetime(year=2000, month=1, day=1))
    dfupdated_on = mapped_column(DateTime, default=None)
    dfemail = mapped_column(String(50))
    dfname = mapped_column(String(50))
    dfgame_type = mapped_column(ForeignKey("tgame_type.id"))


class TGameType(Base):
    __tablename__ = "tgame_type"

    id = mapped_column(SmallInteger, primary_key=True)
    dfname = mapped_column(String(30))
