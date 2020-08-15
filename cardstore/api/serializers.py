from rest_framework import serializers

from cardstore.models import WhiteCard, BlackCard


class WhiteCardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    card_text = serializers.CharField()
    package = serializers.CharField()

    def create(self, validated_data):
        print(validated_data)
        return WhiteCard.objects.create(**validated_data)

    def update(self, instance: WhiteCard, validated_data):
        instance.card_text = validated_data.get('card_text', instance.card_text)
        instance.package = validated_data.get('package', instance.package)
        instance.save()
        return instance


class BlackCardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    card_text = serializers.CharField()

    def create(self, validated_data):
        print(validated_data)
        return BlackCard.objects.create(**validated_data)

    def update(self, instance: WhiteCard, validated_data):
        instance.card_text = validated_data.get('card_text', instance.card_text)
        instance.package = validated_data.get('package', instance.package)
        instance.save()
        return instance
