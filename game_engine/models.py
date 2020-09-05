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

    def __str__(self):
        return self.session_id


class GameRound(models.Model):
    roundNumber: int = models.PositiveIntegerField(validators=[MinValueValidator(1),
                                                               MaxValueValidator(5)])
    tzar = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)
    active_black_card = models.ForeignKey(BlackCard, on_delete=models.DO_NOTHING)
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name="Round")

    def __str__(self):
        return f"Round {self.roundNumber}, Tzar: {self.tzar}"


class GameRoundProfileData(models.Model):
    user_profile: Profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    cards = models.ManyToManyField(WhiteCard)
    current_points: int = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    round: GameRound = models.ForeignKey(GameRound, on_delete=models.CASCADE, related_name="GameRoundProfileData")

    def __str__(self):
        return f"[{self.round.roundNumber}]{self.user_profile.user.username} : {self.current_points}"
