from typing import Union

from django.contrib.auth.models import User

from game_engine.models import GameRound, Profile, GameRoundProfileData, CardSubmission


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
    return Profile.objects.get(user=user)

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