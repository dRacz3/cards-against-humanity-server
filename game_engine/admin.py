from django.contrib import admin
from game_engine.models import GameRound, GameSession, Profile, GameRoundProfileData

admin.site.register(GameRound)
admin.site.register(Profile)
admin.site.register(GameRoundProfileData)

class GameSessionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['session_id',]}),
    ]
    list_display = ('session_id', 'created_at', 'updated_at')
    list_filter = ['session_id']

admin.site.register(GameSession, GameSessionAdmin)
