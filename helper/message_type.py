from enum import Enum


class MessageType(Enum):
    GAME_CREATION = 0
    SHIPS_ARE_ARRANGED = 1
    PLAY = 2
    FIRE_REQUEST = 3
