import random

from django.db.models import QuerySet, Max
import logging

from rest_framework.generics import get_object_or_404

from cardstore.models import BlackCard, WhiteCard
from game_engine.models import User, Profile, GameSession, SessionDeck, SessionPlayerList, GameRound, \
    GameRoundProfileData


class DeckFactory:
    def __init__(self):
        pass

    def get_white_cards(self, count: int):
        # TODO: select based on categories..
        items = WhiteCard.objects.all()
        random_cards = random.sample(list(items), count)
        return random_cards

    def get_black_cards(self, count: int):
        items = BlackCard.objects.all()
        random_cards = random.sample(list(items), count)
        return random_cards


class GameManager:
    def __init__(self, logger):
        self.recently_created_session_ids = []
        self.logger = logger

    def createOrRetrieveSession(self, session_id: str) -> GameSession:
        session = GameSession.objects.filter(session_id=session_id)
        if not session.exists():
            self.logger.info(f"Session with session_id:{session_id} does not exist. Creating it.")
            self.recently_created_session_ids.append(session_id)
            new_session = GameSession.objects.create(session_id=session_id)
            new_session.save()
            new_deck: SessionDeck = SessionDeck.objects.create(session=new_session)
            [new_deck.white_cards.add(card) for card in DeckFactory().get_white_cards(50)]
            [new_deck.black_cards.add(card) for card in DeckFactory().get_black_cards(50)]
            new_deck.save()
            return new_session
        else:
            return session[0:1][0]

    def retrieveUserProfile(self, user: User) -> Profile:
        return Profile.objects.filter(user=user)[0]

    def addUserToSession(self, session_id: str, user: User):
        if user.is_authenticated:
            self.logger.info(f"{user} joining {session_id}")
            session = self.createOrRetrieveSession(session_id)
            playerList: QuerySet = SessionPlayerList.objects.filter(session=session)
            if not playerList.exists():
                self.logger.info(f"Player list does not exist for session :{session_id}. Creating it.")
                session_player_list = SessionPlayerList.objects.create(session=session)
            else:
                session_player_list = playerList[0]

            if not session_player_list.profiles.filter(user=user).exists():
                self.logger.info("Userprofile is not in session player list, adding it.")
                session_player_list.profiles.add(self.retrieveUserProfile(user))
                session_player_list.save()
            else:
                self.logger.info("Userprofile is ALREADY in session player list. Will not add it twice.")
            return True
        else:
            self.logger.info("User is not authenticated")
            return False

    def progressGame(self, session_id):
        session = GameSession.objects.filter(session_id=session_id).first()
        rf = GameRoundFactory(session)
        rounds = GameRound.objects.filter(session__session_id=session_id)
        if not rounds.exists():
            self.logger.info("Game has not been started yet!")
            session.has_started = True
        newRound = rf.createNewRound()
        newRound.save()
        session.save()


class GameRoundFactory():
    def __init__(self, session):
        self.session = session
        print(f"Loaded {session} ")
        self.players = SessionPlayerList.objects.filter(session=self.session).first()
        print(f"Players: {self.players}")

    def createNewRound(self):
        rounds = GameRound.objects.filter(session=self.session).order_by('roundNumber')
        deck = SessionDeck.objects.filter(session=self.session).first()

        if not rounds.exists():
            roundNumber = 1
            tzar = random.sample(list(self.players.profiles.all()), 1)[0]
        else:
            tzar = random.sample(list(self.players.profiles.exclude(user=rounds.last().tzar.user)), 1)[0]
            roundNumber = rounds.last().roundNumber + 1
            deck.black_cards.remove(rounds.last().active_black_card)
            deck.save()

        black_card = random.sample(list(deck.black_cards.all()), 1)[0]

        newRound = GameRound.objects.create(
            session=self.session,
            roundNumber=roundNumber,
            tzar=tzar,
            active_black_card=black_card)
        active_players = self.players.profiles.exclude(user=tzar.user)

        # Fill deck for players
        for player in self.players.profiles.all():
            expected_count = 10
            #TODO: filter based on round + user -> get previous data, copy from there
            previous_player_data = GameRoundProfileData.objects.filter(round = newRound)

            if previous_player_data.exists():
                print(f"The player owned {previous_player_data.first().cards.count()} cards.")
            else:
                available = list(deck.white_cards.all())
                user_cards = random.sample(available, 10)
                [deck.white_cards.remove(card) for card in user_cards]
                deck.save()
                print(f"{player} receives : {user_cards}")
                print(f"remaining cards: {deck.white_cards.all()}")
                new_data = GameRoundProfileData.objects.create(user_profile=player,
                                                               current_points=0, round=newRound)
                for card in user_cards:
                    new_data.cards.add(card)
                new_data.save()

        return newRound


logger = logging.getLogger("GameManager")
CAHGameManager = GameManager(logger)
