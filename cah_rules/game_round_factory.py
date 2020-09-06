import random

from cardstore.deck_operations import get_white_cards_from_deck
from game_engine.models import SessionPlayerList, GameRound, SessionDeck, GameRoundProfileData


class GameRoundFactory:
    def __init__(self, session):
        self.session = session
        self.players = SessionPlayerList.objects.filter(session=self.session).first()

    def createNewRound(self):
        rounds = GameRound.objects.filter(session=self.session).order_by('roundNumber')
        deck = SessionDeck.objects.filter(session=self.session).first()
        last_round = rounds.last()
        if not rounds.exists():
            roundNumber = 1
            tzar = random.sample(list(self.players.profiles.all()), 1)[0]
        else:
            tzar = random.sample(list(self.players.profiles.exclude(user=last_round.tzar.user)), 1)[0]
            roundNumber = last_round.roundNumber + 1
            deck.black_cards.remove(last_round.active_black_card)
            deck.save()

        black_card = random.sample(list(deck.black_cards.all()), 1)[0]

        newRound = GameRound.objects.create(
            session=self.session,
            roundNumber=roundNumber,
            tzar=tzar,
            active_black_card=black_card)

        newRound.save()

        for player in self.players.profiles.all():
            expected_count = 10
            previous_player_data: GameRoundProfileData = GameRoundProfileData.objects.filter(round=last_round,
                                                                                             user_profile=player).first()
            if previous_player_data is not None:
                self.create_player_data_from_previous_round(deck, expected_count, previous_player_data)
            else:
                self.create_new_player_data(deck, expected_count, newRound, player)

        return newRound

    def create_player_data_from_previous_round(self, deck, expected_count, previous_player_data):
        new_player_data = previous_player_data
        new_player_data.pk = None
        cards_in_hand_count = previous_player_data.cards.count()
        user_cards = get_white_cards_from_deck(deck, expected_count - cards_in_hand_count)
        for card in user_cards:
            new_player_data.cards.add(card)
        new_player_data.save()

    def create_new_player_data(self, deck, expected_count, newRound, player):
        user_cards = get_white_cards_from_deck(deck, expected_count)
        new_data = GameRoundProfileData.objects.create(user_profile=player,
                                                       current_points=0,
                                                       round=newRound)
        for card in user_cards:
            new_data.cards.add(card)
        new_data.save()