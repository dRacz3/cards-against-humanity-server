from django.db.models import QuerySet
import logging

from cah_rules.game_round_factory import GameRoundFactory
from cardstore.deck_operations import DeckFactory
from game_engine.models import User, Profile, GameSession, SessionDeck, SessionPlayerList, GameRound, \
    GameRoundProfileData


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

    def select_winner(self, user_name: str, session: GameSession):
        last_round = GameRound.objects.filter(session=session).last()
        winner_profile_data = GameRoundProfileData.objects.filter(round=last_round,
                                                                  user_profile__user__username=user_name).first()
        last_round.winner = winner_profile_data
        last_round.save()

    def progressGame(self, session_id):
        session = GameSession.objects.filter(session_id=session_id).first()
        rf = GameRoundFactory(session)
        rounds = GameRound.objects.filter(session__session_id=session_id)
        if not rounds.exists():
            self.logger.info("Game has not been started yet! Starting it...")
            session.has_started = True
            rf.createNewRound()
        else:
            if rounds.last().winner is not None:
                self.increase_points_for_winner(rounds.last())
                rf.createNewRound()
            else:
                self.logger.info("A winner must be selected!")
        session.save()

    def increase_points_for_winner(self, last_round):
        winner_profile_data = GameRoundProfileData.objects.filter(round=last_round,
                                                                  user_profile=last_round.winner).first()
        winner_profile_data.current_points += 1
        winner_profile_data.save()


logger = logging.getLogger("GameManager")
CAHGameManager = GameManager(logger)
