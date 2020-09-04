from rest_framework import serializers
from game_engine.models import Profile, GameRound, GameRoom


class ProfileSerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField(read_only=True)
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"


class GameRoundSerializer(serializers.ModelSerializer):
    room = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GameRound
        fields = '__all__'


class GameRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameRoom
        fields = "__all__"
