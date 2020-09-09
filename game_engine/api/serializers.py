from rest_framework import serializers

from cardstore.api.serializers import BlackCardSerializer
from game_engine.models import Profile, GameRound, GameSession, GameRoundProfileData, CardSubmission


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"


class GameRoundSerializer(serializers.ModelSerializer):
    session = serializers.StringRelatedField(read_only=True)
    tzar = serializers.PrimaryKeyRelatedField(read_only=True)
    active_black_card = BlackCardSerializer(read_only=True)

    class Meta:
        model = GameRound
        fields = '__all__'
        depth  = 5


class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = "__all__"


class GameRoundProfileDataSerializer(serializers.ModelSerializer):
    round = serializers.StringRelatedField(read_only=True)
    user_profile = serializers.StringRelatedField(read_only=True)
    cards = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = GameRoundProfileData
        fields = "__all__"


class CardSubmissionSerializer(serializers.ModelSerializer):
    submitted_white_cards = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = CardSubmission
        fields = ('submitted_white_cards', 'submission_id')
