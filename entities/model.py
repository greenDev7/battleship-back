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

    user_winner = mapped_column(ForeignKey("tuser_history.id"))
    user_loser = mapped_column(ForeignKey("tuser_history.id"))


class TUserHistory(Base):
    __tablename__ = "tuser_history"

    id = mapped_column(Uuid, primary_key=True)
    dfcreated_on = mapped_column(DateTime, default=datetime(year=2000, month=1, day=1))
    dfupdated_on = mapped_column(DateTime, default=None)
    dfemail = mapped_column(String(50))
    dfname = mapped_column(String(50))
    dfclient_host_ip = mapped_column(String(20))
    dfclient_port = mapped_column(String(10))


class TRivalCouple(Base):
    __tablename__ = "trival_couple"

    id = mapped_column(Uuid, primary_key=True)
    dfplayer1 = mapped_column(Uuid)
    dfplayer1_nickname = mapped_column(String(100))
    dfplayer1_state = mapped_column(ForeignKey("tstate.id"))
    dfplayer2 = mapped_column(Uuid)
    dfplayer2_nickname = mapped_column(String(100))
    dfplayer2_state = mapped_column(ForeignKey("tstate.id"))
    dfcreated_on = mapped_column(DateTime)


class TGameType(Base):
    __tablename__ = "tgame_type"

    id = mapped_column(SmallInteger, primary_key=True)
    dfname = mapped_column(String(30))


class TState(Base):
    __tablename__ = "tstate"

    id = mapped_column(SmallInteger, primary_key=True)
    dfname = mapped_column(String(30))
