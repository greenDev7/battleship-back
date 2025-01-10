from enum import Enum


class GameState(Enum):
    SEARCHING_FOR_OPPONENT = 1
    SHIPS_POSITIONING = 2
    PLAYING = 3
