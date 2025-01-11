from sqlalchemy import Uuid, DateTime, ForeignKey, String, SmallInteger
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    pass


class TRivalCouple(Base):
    __tablename__ = "trival_couple"

    id = mapped_column(Uuid, primary_key=True)
    dfplayer1 = mapped_column(Uuid)
    dfplayer1_nickname = mapped_column(String(100))
    dfplayer1_state = mapped_column(ForeignKey("tplayer_state.id"))
    dfplayer2 = mapped_column(Uuid)
    dfplayer2_nickname = mapped_column(String(100))
    dfplayer2_state = mapped_column(ForeignKey("tplayer_state.id"))
    dfgame_type = mapped_column(ForeignKey("tgame_type.id"))
    dfcreated_on = mapped_column(DateTime)
    dffinished_on = mapped_column(DateTime)


class TGameType(Base):
    __tablename__ = "tgame_type"

    id = mapped_column(SmallInteger, primary_key=True)
    dfname_en = mapped_column(String(30))
    dfname = mapped_column(String(30))


class TPlayerState(Base):
    __tablename__ = "tplayer_state"

    id = mapped_column(SmallInteger, primary_key=True)
    dfname_en = mapped_column(String(30))
    dfname = mapped_column(String(30))
