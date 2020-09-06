from typing import Union

from rest_framework import generics, mixins, viewsets, status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from game_engine.api.serializers import GameSessionSerializer, ProfileSerializer, GameRoundProfileDataSerializer, \
    GameRoundSerializer, CardSubmissionSerializer
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
            'last_round:': []
        }

        if session:
            if session.has_started:
                data['has_started'] = 'yes'
            rounds = GameRound.objects.filter(session=session).last()
            srl = GameRoundSerializer(rounds)
            data['last_round'] = srl.data
        return Response(data, status=status.HTTP_200_OK)


class GameSessionOperations(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, session_id):
        session = get_object_or_404(GameSession, pk=session_id)
        return session

    def get(self, request, session_id):
        session = self.get_object(session_id)
        serializer = GameSessionSerializer(session)
        return Response(serializer.data)

    def put(self, request, session_id):
        session: GameSession = self.get_object(session_id)
        if not session.has_started:
            user = request.user
            userProfile = Profile.objects.filter(user=user)[0]
            session.playerlist.profiles.add(userProfile)

        return Response(f"Added {userProfile} to {session}", status=status.HTTP_200_OK)

    def delete(self, request, session_id):
        article = self.get_object(session_id)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
