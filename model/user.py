import uuid
from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: uuid.UUID
    dfcreated_on: datetime | None = None
    dfupdated_on: datetime | None = None
    dfemail: str
    dfname: str