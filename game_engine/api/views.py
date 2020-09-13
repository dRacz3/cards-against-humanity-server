from typing import Union

from rest_framework import generics, mixins, viewsets, status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from cardstore.api.serializers import WhiteCardSerializer
from game_engine.api.serializers import GameSessionSerializer, ProfileSerializer, GameRoundProfileDataSerializer, \
    GameRoundSerializer, CardSubmissionSerializer, SessionPlayerListSerializer
from game_engine.models import Profile, GameSession, GameRoundProfileData, GameRound, CardSubmission


class ProfileViewSet(mixins.UpdateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["room"]


class GameSessionViewSet(mixins.UpdateModelMixin,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin,
                         viewsets.GenericViewSet):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["room_name"]


class GameRoundProfileDataViewSet(mixins.UpdateModelMixin,
                                  mixins.ListModelMixin,
                                  mixins.RetrieveModelMixin,
                                  mixins.CreateModelMixin,
                                  viewsets.GenericViewSet):
    queryset = GameRoundProfileData.objects.all()
    serializer_class = GameRoundProfileDataSerializer
    permission_classes = [IsAuthenticated]


class ProfileDataBasedOnSessionDataViewSet(generics.ListAPIView):
    serializer_class = GameRoundProfileDataSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        session_id = self.kwargs["session_id"]
        if session_id is not None:
            queryset = GameRoundProfileData.objects.filter(round__session__session_id=session_id)
            if not queryset.exists():
                return []
            return queryset
        else:
            return []


class GameRoundsBasedOnSessionsViewSet(generics.ListAPIView):
    serializer_class = GameRoundSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        session_id = self.kwargs["session_id"]
        if session_id is not None:
            queryset = GameRound.objects.filter(session__session_id=session_id)
            if not queryset.exists():
                return []
            return queryset
        else:
            return []


class CardSubmissionsRoundsViewSet(generics.ListAPIView):
    serializer_class = CardSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        session_id = self.kwargs["session_id"]
        if session_id is not None:
            round = GameRound.objects.filter(session__session_id=session_id).last()
            if round is not None:
                return CardSubmission.objects.filter(connected_game_round_profile__round=round)
        else:
            return []


class SessionStateView(APIView):
    def get(self, request, session_id):
        session: Union[GameSession, None] = GameSession.objects.filter(session_id=session_id).first()

        data = {
            'has_started': 'no',
            'last_round': [],
            'players': [],
            'submissions': []
        }

        if session:
            if session.has_started:
                data['has_started'] = 'true'
            rounds = GameRound.objects.filter(session=session).last()
            srl = GameRoundSerializer(rounds)
            data['last_round'] = srl.data
            players = session.sessionplayerlist_set.first()
            playerSerializer = SessionPlayerListSerializer(players)

            data['players'] = playerSerializer.data

        return Response(data, status=status.HTTP_200_OK)


class CheckCardsInUserHand(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        user = request.user
        profile: GameRoundProfileData = GameRoundProfileData.objects.get(user_profile__user=user,
                                                                         round__session__session_id=session_id)
        if profile:
            card_serializer = WhiteCardSerializer(profile.cards.all(), many=True)
            return Response(card_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("", status=status.HTTP_404_NOT_FOUND)


class SubmitCard(generics.UpdateAPIView):
    def post(self, request, session_id):
        serializer = WhiteCardSerializer(data=request.data)
        session = GameSession.objects.get(session_id = session_id)
        user = request.user
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)