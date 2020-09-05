from rest_framework import generics, mixins, viewsets, status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from game_engine.api.serializers import GameSessionSerializer, ProfileSerializer, GameRoundProfileDataSerializer, \
    GameRoundSerializer
from game_engine.models import Profile, GameSession, GameRoundProfileData, GameRound


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


class GameSessionOperations(APIView):

    def get_object(self, pk):
        session = get_object_or_404(GameSession, pk=pk)
        return session

    def get(self, request, pk):
        session = self.get_object(pk)
        serializer = GameSessionSerializer(session)
        return Response(serializer.data)

    def put(self, request, pk):
        session: GameSession = self.get_object(pk)
        user = request.user
        userProfile = Profile.objects.filter(user=user)[0]
        session.players.add(userProfile)
        session.save()
        return Response(f"Added {userProfile} to {session}", status=status.HTTP_200_OK)

    def delete(self, request, pk):
        article = self.get_object(pk)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
