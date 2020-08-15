from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from cardstore.models import WhiteCard, BlackCard
from cardstore.api.serializers import WhiteCardSerializer, BlackCardSerializer


@api_view(["GET", "POST"])
def whitecard_list_create_api_view(request):
    if request.method == "GET":
        whitecards = WhiteCard.objects.all()
        serializer = WhiteCardSerializer(whitecards, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = WhiteCardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
def blackcard_list_create_api_view(request):
    if request.method == "GET":
        blackcards = BlackCard.objects.all()
        serializer = BlackCardSerializer(blackcards, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = BlackCardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def whitecard_detail_api_view(request, pk):
    try:
        card = WhiteCard.objects.get(pk=pk)
    except WhiteCard.DoesNotExist:
        return Response({'error': {
            'code': 404,
            'message': 'White card not found'
        }}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = WhiteCardSerializer(card)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = WhiteCardSerializer(card, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        card.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["GET", "PUT", "DELETE"])
def blackcard_detail_api_view(request, pk):
    try:
        card = BlackCard.objects.get(pk=pk)
    except BlackCard.DoesNotExist:
        return Response({'error': {
            'code': 404,
            'message': 'White card not found'
        }}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BlackCardSerializer(card)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = BlackCardSerializer(card, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        card.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)