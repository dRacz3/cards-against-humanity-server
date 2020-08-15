from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from cardstore.models import WhiteCard, BlackCard
from cardstore.api.serializers import WhiteCardSerializer, BlackCardSerializer


class WhiteCardListCreateApiView(APIView):
    def get(self, request):
        whitecards = WhiteCard.objects.all()
        serializer = WhiteCardSerializer(whitecards, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WhiteCardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class BlackCardListCreateApiView(APIView):
    def get(self, request):
        whitecards = BlackCard.objects.all()
        serializer = BlackCardSerializer(whitecards, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BlackCardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class WhiteCardDetailsApiView(APIView):
    def getObject(self, pk):
        return get_object_or_404(WhiteCard.objects.get(pk=pk))

    def get(self, request, pk):
        card = self.getObject(pk)
        serializer = WhiteCardSerializer(card)
        return Response(serializer.data)

    def put(self, request, pk):
        card = self.getObject(pk)
        serializer = WhiteCardSerializer(card, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        card = self.getObject(pk)
        card.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BlackCardDetailsApiView(APIView):
    def getObject(self, pk):
        return get_object_or_404(BlackCard.objects.get(pk=pk))

    def get(self, request, pk):
        card = self.getObject(pk)
        serializer = BlackCardSerializer(card)
        return Response(serializer.data)

    def put(self, request, pk):
        card = self.getObject(pk)
        serializer = BlackCardSerializer(card, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        card = self.getObject(pk)
        card.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
