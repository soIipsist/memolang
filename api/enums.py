from enum import Enum


class GameType(str, Enum):
    WORDS = "words"
    IMAGES = "images"
    CARDS = "cards"
    NUMBERS = "numbers"
