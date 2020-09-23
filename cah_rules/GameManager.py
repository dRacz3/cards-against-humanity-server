import random
from typing import List, Union

from django.db.models import QuerySet
import logging

from cah_rules.game_round_factory import GameRoundFactory
from cardstore.deck_operations import DeckFactory
from cardstore.models import WhiteCard, BlackCard
from game_engine.models import User, Profile, GameSession, SessionDeck, SessionPlayerList, GameRound, \
    GameRoundProfileData, CardSubmission


class UPDATE_COMMANDS:
    UPDATE = "UPDATE"
    REQUEST_PLAYER_DATA = "REQUEST_PLAYER_DATA"
    GAME_HAS_ENDED = "GAME_HAS_ENDED"


MAX_ROUND_NUMBER = 10

def reverse_search_cards_by_text(submitted_card_texts: List[str]) -> List[WhiteCard]:
    """
    Calling this function will perform reverse card text lookup for white cards.
    """
    wcs = []
    for cardtext in submitted_card_texts:
        returnedCard = WhiteCard.objects.filter(text=cardtext).first()
        if returnedCard is not None:
            wcs.append(returnedCard)
        else:
            raise ValueError(f"Could not find card with text: {cardtext}")
    return wcs

def parse_winning_submission(black_card : BlackCard, submissions : CardSubmission):
    def parse(text, submissions):
        if text.find('_') == -1:
            return f"{text} [{submissions[0]}]"
        else:
            count = 0
            while text.find("_") != -1:
                text = replace_character_at_index(text, f"{submissions[count]}")
                count = count + 1

        return text

    def replace_character_at_index(text, replacement):
        print(f"replaceing ({text}) with {replacement}")
        asd = text.replace("_", replacement, 1)
        print(asd)
        return asd

    submission_texts = [card.text for card in submissions.submitted_white_cards.all() ]
    return parse(black_card.text, submission_texts)



def fetch_last_round_for_session_id(session_id: str) -> Union[GameRound, None]:
    """
    This function will fetch the last available round for the given session.
    Note: can return None
    """
    last_round: GameRound = GameRound.objects.filter(session__session_id=session_id).last()
    return last_round


def retrieve_user_profile(user: User) -> Profile:
    """
    Retrieves the user profile associated with user.
    """
    return Profile.objects.filter(user=user)[0]


def retrieve_submission_for_round_data(profile_data_for_submitting_player: GameRoundProfileData) -> CardSubmission:
    """Retrieves submitted cards for a given player round profile"""
    submission = CardSubmission.objects.filter(
        connected_game_round_profile=profile_data_for_submitting_player)
    if not submission.exists() or submission.first().submitted_white_cards.count() == 0:
        submission: CardSubmission = CardSubmission.objects.create(
            connected_game_round_profile=profile_data_for_submitting_player)
    else:
        raise Exception("Player has already submitted cards")
    return submission


class WinnerSelectionChecker:
    def __str__(self):
        pass

    def winner_can_be_selected(self) -> bool:
        return True

    def get_error_reason(self) -> str:
        return "Return a dummy message why the winner selection is not allowed"


class GameManager:
    def __init__(self, logger):
        self.recently_created_session_ids = []
        self.logger = logger

    def create_or_retrieve_session(self, session_id: str) -> GameSession:
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

            self.logger.info(f"Creating SessionPlayerList object for session:{session_id}..")
            session_player_list = SessionPlayerList.objects.create(session=new_session)
            session_player_list.save()
            self.logger.info("Creating the first round prototype")
            GameRoundFactory(new_session).createNewRound()
            return new_session
        else:
            return session.first()

    def add_user_to_session(self, session_id: str, user: User) -> bool:
        if user.is_authenticated:
            self.logger.info(f"{user} joining {session_id}")
            session = self.create_or_retrieve_session(session_id)
            session_player_list: SessionPlayerList = SessionPlayerList.objects.get(session=session)

            if not session_player_list.profiles.filter(user=user).exists():
                self.logger.info(f"{user} is not in session player list, adding it.")
                session_player_list.profiles.add(retrieve_user_profile(user))
                session_player_list.save()
            else:
                self.logger.info(f"{user} is ALREADY in session player list. Will not add it twice.")
            return True
        else:
            self.logger.info("User is not authenticated")
            return False

    def remove_user_from_session(self, session_id: str, user: User):
        session = self.create_or_retrieve_session(session_id)
        session_player_list: SessionPlayerList = SessionPlayerList.objects.get(session=session)
        session_player_list.profiles.remove(retrieve_user_profile(user))
        session_player_list.save()


    def select_winner(self, submission_id: str, session_id: str) -> str:
        wsc = WinnerSelectionChecker()
        if wsc.winner_can_be_selected():
            last_round = fetch_last_round_for_session_id(session_id)
            submission: CardSubmission = CardSubmission.objects.get(submission_id=submission_id)
            self.logger.info(f"{submission.connected_game_round_profile.user_profile} has been selected as the winner!")
            last_round.winner = submission.connected_game_round_profile.user_profile
            last_round.save()

            winning_submission = parse_winning_submission(last_round.active_black_card, submission)
            return f"{last_round.winner.user} with <br> <h4>{winning_submission}</h4>"
        else:
            raise ValueError(wsc.get_error_reason())

    def submit_cards(self, session_id: str, submitting_player: User, submitted_card_texts: List[str]):
        last_round: GameRound = fetch_last_round_for_session_id(session_id)
        if last_round.active_black_card.pick == len(submitted_card_texts):
            profile_data_for_submitting_player: GameRoundProfileData = GameRoundProfileData.objects.filter(
                round=last_round,
                user_profile__user=submitting_player).first()
            submission = retrieve_submission_for_round_data(profile_data_for_submitting_player)
            submitted_cards = reverse_search_cards_by_text(submitted_card_texts)

            # Check each card
            for card in submitted_cards:
                # It must be in the player's hand
                if card in profile_data_for_submitting_player.cards.all():
                    self.logger.info(
                        f"Player {profile_data_for_submitting_player.user_profile} has the card : {card}, submission accepted")
                    submission.submitted_white_cards.add(card)
                    profile_data_for_submitting_player.cards.remove(card)

                else:
                    raise Exception("Trying to add card to user that is not in their hand! Abort!")
                submission.save()
                profile_data_for_submitting_player.save()
            return UPDATE_COMMANDS.UPDATE
        else:
            raise ValueError("Not enough cards submitted!")

    def progress_game(self, session_id) -> None:
        session: GameSession = GameSession.objects.get(session_id=session_id)
        rf = GameRoundFactory(session)
        rounds: QuerySet = GameRound.objects.filter(session__session_id=session_id)

        if not session.has_started:
            self.logger.info("Game has not been started yet! Starting it...")
            complete_player_list = SessionPlayerList.objects.filter(session=session).first()
            last_round = rounds.last()
            last_round.tzar = random.sample(list(complete_player_list.profiles.all()), 1)[0]
            last_round.save()
            # before the first actually starts, the player data has to be created.
            rf.create_player_data(last_round, last_round)
            session.has_started = True
        else:
            if rounds.last().winner is not None:
                self.increase_points_for_winner(rounds.last())
                if rounds.last().roundNumber == MAX_ROUND_NUMBER:
                    return UPDATE_COMMANDS.GAME_HAS_ENDED
                else:
                    rf.createNewRound()
            else:
                self.logger.info("A winner must be selected!")
        session.save()
        return UPDATE_COMMANDS.UPDATE

    def increase_points_for_winner(self, last_round) -> None:
        winner_profile_data = GameRoundProfileData.objects.filter(round=last_round,
                                                                  user_profile=last_round.winner).first()
        winner_profile_data.current_points += 1
        winner_profile_data.save()


logger = logging.getLogger("GameManager")
CAHGameManager = GameManager(logger)
