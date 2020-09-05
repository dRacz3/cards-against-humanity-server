from rest_framework import serializers
from game_engine.models import Profile, GameRound, GameSession, GameRoundProfileData


class ProfileSerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField(read_only=True)
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"


class GameRoundSerializer(serializers.ModelSerializer):
    session = serializers.StringRelatedField(read_only=True)
    tzar = serializers.StringRelatedField(read_only=True)
    active_black_card = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GameRound
        fields = '__all__'

class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = "__all__"


class GameRoundProfileDataSerializer(serializers.ModelSerializer):
    round = serializers.StringRelatedField(read_only=True)
    user_profile = serializers.StringRelatedField(read_only=True)
    cards = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GameRoundProfileData
        fields = "__all__"