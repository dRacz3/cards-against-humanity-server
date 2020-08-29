from typing import List
from cardstore.models import WhiteCard

class Player:
    def __init__(self, name):
        self.name = name
        self.points = 0
        self.cards_in_hand : List[WhiteCard]  = []

    def __str__(self):
        return f"Player [{self.name}], Points: {self.points}, Currently holding cards: {self.cards_in_hand}"

