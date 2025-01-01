from enum import Enum


class GameState(Enum):
    WAITING_FOR_ENEMY = 1
    SHIPS_POSITIONING = 2
    PLAYING = 3
