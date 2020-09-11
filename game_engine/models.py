from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User

from cardstore.models import WhiteCard, BlackCard


class Profile(models.Model):
    user: User = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=240, blank=True)
    avatar = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class GameSession(models.Model):
    session_id = models.CharField(max_length=120, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    has_started = models.BooleanField(default=False)

    def __str__(self):
        return f"<Session: {self.session_id}"


class SessionPlayerList(models.Model):
    profiles = models.ManyToManyField(Profile)
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE)

    def __str__(self):
        return f"[{self.session.session_id}] {self.profiles.all()}"


class GameRound(models.Model):
    roundNumber: int = models.PositiveIntegerField(validators=[MinValueValidator(1),
                                                               MaxValueValidator(5)])
    tzar = models.ForeignKey(Profile, on_delete=models.DO_NOTHING, related_name="Card_Tzar", blank=True, null=True)
    active_black_card = models.ForeignKey(BlackCard, on_delete=models.DO_NOTHING)
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name="Round")
    winner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, related_name="Winner")

    def __str__(self):
        return f"[{self.session.session_id}] Round {self.roundNumber}, Tzar: {self.tzar}"


class SessionDeck(models.Model):
    white_cards = models.ManyToManyField(WhiteCard)
    black_cards = models.ManyToManyField(BlackCard)
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name="deck")

    def __str__(self):
        return f"Deck for session: {self.session.session_id}"

class GameRoundProfileData(models.Model):
    user_profile: Profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    cards = models.ManyToManyField(WhiteCard, related_name="cards_held")
    current_points: int = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    round: GameRound = models.ForeignKey(GameRound, on_delete=models.CASCADE, related_name="GameRoundProfileData")

    def __str__(self):
        return f"[{self.round.session.session_id}] [{self.round.roundNumber}] {self.user_profile.user.username} : {self.current_points}"

class CardSubmission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    submitted_white_cards = models.ManyToManyField(WhiteCard, related_name= "submitted_card_set")
    connected_game_round_profile = models.OneToOneField(GameRoundProfileData, on_delete=models.CASCADE)

    def __str__(self):
        return f"<{self.submission_id}> Submission of {self.connected_game_round_profile.user_profile} : {self.submitted_white_cards.all()}"