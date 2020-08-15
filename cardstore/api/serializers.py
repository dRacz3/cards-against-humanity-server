from rest_framework import serializers

from cardstore.models import WhiteCard, BlackCard


class WhiteCardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    text = serializers.CharField()
    deck = serializers.CharField()

    def create(self, validated_data):
        return WhiteCard.objects.create(**validated_data)

    def update(self, instance: WhiteCard, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.deck = validated_data.get('deck', instance.deck)
        instance.save()
        return instance


class BlackCardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    text = serializers.CharField()
    deck = serializers.CharField()

    def create(self, validated_data):
        print(validated_data)
        return BlackCard.objects.create(**validated_data)

    def update(self, instance: WhiteCard, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.deck = validated_data.get('deck', instance.deck)
        instance.save()
        return instance
