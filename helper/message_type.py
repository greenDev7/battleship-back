from enum import Enum


class MessageType(Enum):
    GAME_CREATION = 0
    SHIPS_ARE_ARRANGED = 1
    PLAY = 2
    FIRE_REQUEST = 3
    FIRE_RESPONSE = 4
    UNSUNK_SHIPS = 5
    GAME_OVER = 6
    DISCONNECTION = 7
