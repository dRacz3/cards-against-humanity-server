import logging
from typing import List

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from cah_rules.GameManager import GameManager, fetch_last_round_for_session_id
from game_engine.models import GameSession, GameRound, SessionPlayerList, SessionDeck, GameRoundProfileData, \
    CardSubmission
from cardstore.models import WhiteCard, BlackCard


class GameManagerTestCase(APITestCase):

    def setUp(self):
        white_cards_data = [{
            'text': f'white_card_text_{textnum}',
            'icon': 'idontcare',
            'deck': 'couldnotcareless'
        } for textnum in range(100)]

        black_cards_data = [{
            'text': f'black_card_text_{textnum}',
            'icon': 'idontcare',
            'deck': 'couldnotcareless',
            'pick': 1
        } for textnum in range(100)]

        for wcd in white_cards_data:
            WhiteCard.objects.create(**wcd).save()

        for bcd in black_cards_data:
            BlackCard.objects.create(**bcd).save()

    def add_n_players_to_game(self, game_manager: GameManager, player_names: List[str], session_name: str):
        created_users = []
        for player in player_names:
            user: User = User.objects.create_user(username=f"test{player}", email=f"{player}@test.com",
                                                  password="somepassword")
            user.save()
            game_manager.add_user_to_session(session_name, user)
            created_users.append(user)
        return created_users

    def test_when_player_joins_session_created(self):
        gm = GameManager(logging.getLogger("testlogger"))
        session_name = 'testytestroom'

        # Creating user : Peti, and he joins the session
        peti = User.objects.create_user(username="testPeti", email="peti@test.com", password="somepassword")
        gm.add_user_to_session(session_name, peti)

        self.assertTrue(GameSession.objects.filter(session_id=session_name).exists())
        session_instance: GameSession = GameSession.objects.filter(session_id=session_name).first()
        self.assertFalse(session_instance.has_started)
        # Deck should be populated with cards..
        session_deck = SessionDeck.objects.filter(session=session_instance).first()
        self.assertIsNotNone(session_deck)
        self.assertGreater(session_deck.white_cards.count(), 5)
        self.assertGreater(session_deck.black_cards.count(), 5)

        # Session player list object should be associated with session.
        self.assertTrue(SessionPlayerList.objects.filter(session=session_instance).exists())
        session_players = SessionPlayerList.objects.filter(session=session_instance).first()
        # the user Peti should be in the session players.
        self.assertTrue(session_players.profiles.filter(user=peti).exists())

        # Adding a second user to the game.
        laci = User.objects.create_user(username="testLaci", email="laci@test.com", password="somepassword")
        gm.add_user_to_session(session_name, laci)

        # the user Laci should be in the session players as well now.
        self.assertTrue(session_players.profiles.filter(user=laci).exists())

        # First round is created immediately.
        self.assertTrue(GameRound.objects.filter(session__session_id=session_name).exists())
        gm.progress_game(session_name)

    def test_multiple_player_session_does_not_progress_until_winner_selected(self):
        gm = GameManager(logging.getLogger("testlogger"))
        session_name = 'testytestroom2'

        self.add_n_players_to_game(game_manager=gm, player_names=['Laci', 'Peti', 'Petra', 'Vivi'],
                                   session_name=session_name)
        gm.progress_game(session_name)

        session_instance = GameSession.objects.get(session_id=session_name)
        self.assertEqual(GameRound.objects.filter(session=session_instance).count(), 1)

        # No winner selected, game should not progress!
        gm.progress_game(session_name)
        self.assertEqual(GameRound.objects.filter(session=session_instance).count(), 1)

    def test_players_submit_cards_is_noticed(self):
        gm = GameManager(logging.getLogger("testlogger"))
        session_name = 'testytestroom2'
        player_names = ['Lacika', 'Petike', 'Petracska', 'Vivien']
        user_instances = self.add_n_players_to_game(game_manager=gm, player_names=player_names,
                                                    session_name=session_name)
        gm.progress_game(session_name)
        last_round = fetch_last_round_for_session_id(session_name)
        print(last_round)
        for user in user_instances:
            user_profile_for_round = GameRoundProfileData.objects.filter(user_profile__user=user,
                                                                         round=last_round).first()
            print(user_profile_for_round)
            self.assertIsNotNone(user_profile_for_round)
            # Select a card from the player's hand
            cards_for_user = user_profile_for_round.cards.all()
            submitted_card_text = cards_for_user[0].text
            gm.submit_cards(session_name, user, submitted_card_texts=[submitted_card_text])
            registered_submisson = CardSubmission.objects.filter(
                connected_game_round_profile=user_profile_for_round).first()
            self.assertEqual(submitted_card_text, registered_submisson.submitted_white_cards.first().text)

        for user in user_instances:
            currentProfileData = GameRoundProfileData.objects.filter(round__session__session_id=session_name,
                                                                     user_profile__user=user).last()
            self.assertEqual(currentProfileData.cards.all().count(), 9,
                             "Users have submitted a card each, they should have 1 less card!")

        winner_profile = GameRoundProfileData.objects.filter(user_profile__user=user_instances[0],
                                                             round=last_round).first()
        winning_submission = CardSubmission.objects.filter(connected_game_round_profile=winner_profile).first()

        gm.select_winner(submission_id=winning_submission.submission_id, session_id=session_name)
        gm.progress_game(session_name)

        last_round_profile_for_winner: GameRoundProfileData = GameRoundProfileData.objects.filter(
            user_profile__user=user_instances[0]).last()
        self.assertEqual(last_round_profile_for_winner.current_points, 1,
                         msg="Winner should have 1 point at the beginning of the new round")

        # Assert all users have their hands full
        for user in user_instances:
            currentProfileData = GameRoundProfileData.objects.filter(round__session__session_id=session_name,
                                                                     user_profile__user=user).last()
            self.assertEqual(currentProfileData.cards.all().count(), 10, "Users hands have been filled back to max")
