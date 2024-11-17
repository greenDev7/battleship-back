import uuid
from datetime import datetime

from pydantic import BaseModel


class Game(BaseModel):
    id: uuid.UUID
    dfstarted_on: datetime | None
    dfduration: int | None

    # user_winner = mapped_column(ForeignKey("tuser.id"))
    # user_loser = mapped_column(ForeignKey("tuser.id"))
