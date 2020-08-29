import random
from typing import List, Dict
from cardstore.models import WhiteCard, BlackCard
from cah_rules.models import Player
import logging
class CAH_GameSession:

    def __init__(self, session_id):
        #TODO :pass addiotional game data... if needed.
        self.logger = logging.getLogger(session_id)
        logging.basicConfig(
            level=logging.INFO,
            format='[%(name)s][%(asctime)s][%(levelname)s][%(funcName)s] %(message)s')

        self.logger.info(f"A game session with id: {session_id} has been created!")
        self.logger.setLevel(logging.DEBUG)
        self.session_id = session_id
        self.number_of_turns = 3
        self.is_started = False
        self.current_card_tzar = None
        self.session_player_data : Dict[str, Player]= {}

        self.white_card_deck : List[WhiteCard] = []
        self.black_card_deck : List[BlackCard] = []

    def addNewUser(self, player: str):
        self.logger.info(f"Added new player: {player}")
        self.session_player_data[player] = Player(player)

        newCards = WhiteCard.objects.all()
        random_cards = random.sample(list(newCards), 10)
        for card in random_cards:
            self.white_card_deck.append(card)


    def removeUser(self, player_name):
        del self.session_player_data[player_name]

    def populatePlayerHandsWithCards(self):
        for name, player in self.session_player_data.items():
            self.logger.info(f" ==== Processing : {player} ====")
            while (len(player.cards_in_hand) <10):
                newCard = self.white_card_deck.pop()
                self.logger.debug(f"Moving card {newCard} to {name}")
                player.cards_in_hand.append(newCard)


CAH_GAME_SESSIONS : Dict[str, CAH_GameSession] = {}