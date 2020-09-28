from rest_framework import serializers

from cardstore.models import WhiteCard, BlackCard, DeckMetaData


class WhiteCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhiteCard
        exclude = ['card_id']


class BlackCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlackCard
        exclude = ['card_id']

class DeckMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeckMetaData
        exclude = ['id']
