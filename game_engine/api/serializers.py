from rest_framework import serializers

from cardstore.api.serializers import BlackCardSerializer, WhiteCardSerializer
from game_engine.models import Profile, GameRound, GameSession, GameRoundProfileData, CardSubmission, SessionPlayerList


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"




class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = "__all__"


class GameRoundProfileDataSerializer(serializers.ModelSerializer):
    round = serializers.StringRelatedField(read_only=True)
    user_profile = ProfileSerializer(read_only=True)
    cards = WhiteCardSerializer(read_only=True, many=True)

    class Meta:
        model = GameRoundProfileData
        fields = "__all__"


class CardSubmissionSerializer(serializers.ModelSerializer):
    submitted_white_cards = WhiteCardSerializer(many=True)

    class Meta:
        model = CardSubmission
        fields = ('submitted_white_cards', 'submission_id')


class GameRoundSerializer(serializers.ModelSerializer):
    session = GameSessionSerializer(read_only=True)
    tzar = ProfileSerializer(read_only=True)
    active_black_card = BlackCardSerializer(read_only=True)

    class Meta:
        model = GameRound
        fields = '__all__'
        depth  = 5


class SessionPlayerListSerializer(serializers.ModelSerializer):
    profiles = ProfileSerializer(read_only=True, many=True)
    session = GameSessionSerializer(read_only=True)

    class Meta:
        model = SessionPlayerList
        fields = '__all__'