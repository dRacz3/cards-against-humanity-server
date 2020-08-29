import random
from typing import List, Dict
from cardstore.models import WhiteCard, BlackCard
from cah_rules.models import Player, SingleRound
import logging


class CAH_GameSession:

    def __init__(self, session_id):
        # TODO :pass addiotional game data... if needed.
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
        self.session_player_data: Dict[str, Player] = {}

        self.white_card_deck: List[WhiteCard] = []
        self.black_card_deck: List[BlackCard] = []

        self.round_history: List[SingleRound] = []
        self.current_round: SingleRound = None

    def startGame(self):
        self.black_card_deck = random.sample(list(BlackCard.objects.all()), self.number_of_turns)
        self.populatePlayerHandsWithCards()
        current_tzar = self.session_player_data[random.sample(list(self.session_player_data.keys()), 1)[0]]
        self.current_card_tzar = current_tzar
        self.logger.info(f"==== GAME HAS STARTED, current TZAR is : {self.current_card_tzar}")
        if self.current_round is not None:
            self.logger.warning("A whole new game has started!")
            self.round_history = []
        self.startNextRound()

    def addNewUser(self, player: str):
        self.logger.info(f"Added new player: {player}")
        self.session_player_data[player] = Player(player)

        newCards = WhiteCard.objects.all()
        random_cards = random.sample(list(newCards), 10)
        for card in random_cards:
            self.white_card_deck.append(card)

    def removeUser(self, player_name):
        del self.session_player_data[player_name]

    def get_currently_active_player_count(self):
        return len(self.session_player_data.keys())

    def populatePlayerHandsWithCards(self):
        for name, player in self.session_player_data.items():
            self.logger.info(f" ==== Processing : {player} ====")
            while (len(player.cards_in_hand) < 10):
                newCard = self.white_card_deck.pop()
                self.logger.debug(f"Moving card {newCard} to {name}")
                player.cards_in_hand.append(newCard)

    def submit_user_card(self, player_name, cards: List[str]):
        if self.current_round is None:
            self.logger.error("Cannot submit cards, as there is no active round!")
            return
        # TODO : map cards somehow back..
        submitted_white_cards : List[WhiteCard]= []
        self.logger.info(f"Mapping card text to cards.. List of texts: [{cards}]")
        for card_text in cards:
            submitted_white_cards.append(WhiteCard.objects.filter(text=card_text))
        self.current_round.player_submit(self.session_player_data[player_name], submitted_white_cards)
        if (self.current_round.has_everyone_submitted()):
            self.startTzarVoting()

    def selectWinner(self, player: Player):
        self.logger.info("The TZAR has selected the best!")
        self.current_round.select_winner(player)
        self.endRound()

    def startTzarVoting(self):
        pass

    def startNextRound(self):
        if self.current_round is not None:
            self.logger.info("Archived current round...")
            self.round_history.append(self.current_round)
        flopped_black_card = self.black_card_deck.pop()
        self.current_round = SingleRound(self.session_id, len(self.round_history),
                                         players=list(self.session_player_data.values()),
                                         tzar=self.current_card_tzar,
                                         active_black_card=flopped_black_card)
        self.logger.info("Next round is started!")

    def endRound(self):
        self.session_player_data[self.current_round.winner.name].points += 1
        #TODO: remove submitted cards..
        for player, submissions in self.current_round.submissions.items():
            for submitted_card in submissions:
                self.logger.info(f"Removing sumbitted card : {submitted_card} from {player}")
                self.session_player_data[player.name].cards_in_hand.remove(submitted_card)

        self.current_card_tzar = self.session_player_data[self.current_round.winner.name]


CAH_GAME_SESSIONS: Dict[str, CAH_GameSession] = {}
