import logging
from typing import List, Dict
from cardstore.models import WhiteCard, BlackCard


class Player:

    def __init__(self, name):
        self.name = name
        self.points = 0
        self.cards_in_hand: List[WhiteCard] = []

    def __str__(self):
        cards_tablestr = ''.join([str(card) + '\n' for card in self.cards_in_hand])
        return f"Player [{self.name}], Points: {self.points}, Currently holding cards ({len(self.cards_in_hand)})\n{cards_tablestr}"

    def __repr__(self):
        return self.__str__()


class SingleRound:
    def __init__(self, session_name: str, round_num: int, players: List[Player], tzar: Player,
                 active_black_card: BlackCard):
        # Save players, remove tzar from players as he is not submittind anything.
        self.round_id = f"{session_name}-{round_num}"
        self.logger = logging.getLogger(self.round_id)
        self.players = players
        self.players.remove(tzar)
        self.tzar = tzar
        self.active_black_card = active_black_card
        self.winner: Player = None
        self.submissions: Dict[Player, List[WhiteCard]] = {}
        for player in self.players:
            self.submissions[player] = []

    def player_submit(self, player: Player, cards: List[WhiteCard]):
        self.logger.info(f"{player.name} has submitted: {cards}")
        self.submissions[player] = cards

    def has_everyone_submitted(self):
        for player, submission in self.submissions.items():
            if len(submission) == 0:
                return False
        return True

    def select_winner(self, player: Player):
        self.winner = player

    def remove_player(self, player : Player):
        if player in self.players:
            self.players.remove(player)
        elif self.tzar == player:
            self.logger.warning(f"Tzar ({player}) has disconnected")
            self.tzar = None

    def winning_text(self):
        winner_submission = self.submissions[self.winner]
        # TODO... parse it
        return f"Winner name is {self.winner.name}. Result : {self.active_black_card.text}, with submitted White cards: {winner_submission}"
