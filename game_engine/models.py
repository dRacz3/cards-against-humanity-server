from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User

from cardstore.models import WhiteCard, BlackCard


class GameRoom(models.Model):
    room_name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.room_name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=240, blank=True)
    avatar = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class GameRoundProfileData(models.Model):
    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    cards = models.ManyToManyField(WhiteCard)
    round = models.ForeignKey(GameRoom, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.user_profile.user.username}'s round profile"

class GameRound(models.Model):
    roundNumber = models.PositiveIntegerField(validators=[MinValueValidator(1),
                                                          MaxValueValidator(5)])
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE, related_name="round")
    players = models.ManyToManyField(GameRoundProfileData)
    tzar = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)
    active_black_card = models.ForeignKey(BlackCard, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"Room : {self.room} , round {self.roundNumber}, Tzar: {self.tzar} with players: {self.players}"
