from rest_framework import status, mixins, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

import random
from cardstore.models import WhiteCard, BlackCard
from cardstore.api.serializers import WhiteCardSerializer, BlackCardSerializer


class WhiteCardViewSet(mixins.UpdateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = WhiteCard.objects.all()
    serializer_class = WhiteCardSerializer
    filter_backends = [SearchFilter]
    search_fields = ["text"]

class BlackCardViewSet(mixins.UpdateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = BlackCard.objects.all()
    serializer_class = BlackCardSerializer
    filter_backends = [SearchFilter]
    search_fields = ["text"]

class DrawNWhiteCardsApiView(APIView):
    def get(self, request, amount):
        #TODO: select based on categories..
        items = WhiteCard.objects.all()
        random_cards = random.sample(list(items), amount)
        serializer = WhiteCardSerializer(random_cards, many=True)
        return Response(serializer.data)