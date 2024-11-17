import uuid
from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: uuid.UUID
    dfcreated_on: datetime
    dfupdated_on: datetime | None
    dfemail: str
    dfname: str