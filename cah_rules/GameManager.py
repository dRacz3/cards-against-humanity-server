from typing import List

from django.db.models import QuerySet
import logging

from cah_rules.game_round_factory import GameRoundFactory
from cardstore.deck_operations import DeckFactory
from cardstore.models import WhiteCard
from game_engine.models import User, Profile, GameSession, SessionDeck, SessionPlayerList, GameRound, \
    GameRoundProfileData, CardSubmission


def reverse_search_cards_by_text(submitted_card_texts: List[str]) -> List[WhiteCard]:
    wcs = []
    for cardtext in submitted_card_texts:
        returnedCard = WhiteCard.objects.filter(text=cardtext).first()
        if returnedCard is not None:
            wcs.append(returnedCard)
        else:
            raise ValueError(f"Could not find card with text: {cardtext}")
    return wcs


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

    def select_winner(self, card_text: str, session_id: str):
        session = GameSession.objects.filter(session_id=session_id).first()
        last_round = GameRound.objects.filter(session=session).last()
        # TODO: Select winner card by text, find the person who submitted the card ->set profile as winner
        # user_profile = Profile.objects.filter(user__username = user_name).first()
        # if last_round is not None:
        #     winner_profile_data : GameRoundProfileData = GameRoundProfileData.objects.filter(round=last_round,
        #                                                               user_profile=user_profile).first()
        #     last_round.winner = winner_profile_data.user_profile
        #     last_round.save()
        # else:
        #     self.logger.error("You cannot select a winner, as the game has not started yet!")

    def submit_cards(self, session_id, submitting_player, submitted_card_texts: List[str]):
        last_round: GameRound = GameRound.objects.filter(session__session_id=session_id).last()
        if last_round is not None:
            if last_round.active_black_card.pick == len(submitted_card_texts):
                profile_data_for_submitting_player: GameRoundProfileData = GameRoundProfileData.objects.filter(
                    round=last_round,
                    user_profile__user=submitting_player).first()
                submission = self.retrieve_submission_for_round_data(profile_data_for_submitting_player)

                submitted_cards = reverse_search_cards_by_text(submitted_card_texts)

                #Check each card
                for card in submitted_cards:
                    # It must be in the player's hand
                    if card in profile_data_for_submitting_player.cards.all():
                        print(
                            f"Player {profile_data_for_submitting_player.user_profile} has the card : {card}, submission accepted")
                        submission.submitted_white_cards.add(card)
                    else:
                        raise Exception("Trying to add card to user that is not in their hand! Abort!")
                    submission.save()
                return True
            else:
                raise ValueError("Not enough cards submitted!")
        else:
            raise ValueError("Game has not started yet")

    def retrieve_submission_for_round_data(self, profile_data_for_submitting_player):
        submission = CardSubmission.objects.filter(
            connected_game_round_profile=profile_data_for_submitting_player)
        if not submission.exists() or submission.first().submitted_white_cards.count() == 0:
            submission: CardSubmission = CardSubmission.objects.create(
                connected_game_round_profile=profile_data_for_submitting_player)
        else:
            raise Exception("Player has already submitted cards")
        return submission

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
