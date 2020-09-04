from django.contrib import admin
from game_engine.models import GameRound,  GameRoom, Profile, GameRoundProfileData

admin.site.register(GameRoom)
admin.site.register(GameRound)
admin.site.register(Profile)
admin.site.register(GameRoundProfileData)