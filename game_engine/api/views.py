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


# class ProfileViewSet(mixins.UpdateModelMixin,
#                      mixins.ListModelMixin,
#                      mixins.RetrieveModelMixin,
#                      viewsets.GenericViewSet):
#     queryset = Profile.objects.all()
#     serializer_class = ProfileSerializer
#     permission_classes = [IsAuthenticated]
#     filter_backends = [SearchFilter]
#     search_fields = ["room"]


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


class CardSubmissionsRoundsViewSet(generics.ListCreateAPIView):
    serializer_class = CardSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        session_id = self.kwargs["session_id"]
        if session_id is not None:
            round = GameRound.objects.filter(session__session_id=session_id).last()
            if round is not None:
                result = CardSubmission.objects.filter(connected_game_round_profile__round=round)
                if result is not None:
                    return result
        return []


class SessionStateView(APIView):
    def get(self, request, session_id):
        session: Union[GameSession, None] = GameSession.objects.filter(session_id=session_id).first()

        data = {
            'has_started': False,
            'last_round': [],
            'players': [],
            'submissions': []
        }

        if session:
            if session.has_started:
                data['has_started'] = True
            rounds = GameRound.objects.filter(session=session).last()
            srl = GameRoundSerializer(rounds)
            data['last_round'] = srl.data
            players = session.sessionplayerlist_set.first()
            playerSerializer = SessionPlayerListSerializer(players)

            data['players'] = playerSerializer.data

        return Response(data, status=status.HTTP_200_OK)


class FetchOwnPlayerInformations(APIView):
    #TODO: rename endpoint to respect the new name
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        user = request.user
        profile: GameRoundProfileData = GameRoundProfileData.objects.filter(user_profile__user=user,
                                                                         round__session__session_id=session_id).last()
        response = {
            'cards' : [],
            'isTzar' : False
        }
        if profile:
            card_serializer = WhiteCardSerializer(profile.cards.all(), many=True)
            response['cards'] = card_serializer.data
            response['isTzar'] = profile.round.tzar == profile.user_profile
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response("", status=status.HTTP_404_NOT_FOUND)

class HasUserSubmittedThisRound(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        user = request.user
        # Fetch the last active round, and the player data connected to it. We should not have a duplicate.. but anyway
        last_round: GameRound = GameRound.objects.filter(session__session_id=session_id).last()
        profile_query = GameRoundProfileData.objects.filter(user_profile__user=user, round = last_round)
        if(len(profile_query) > 1):
            print(f"MORE THAN 1 GameRoundProfileData for {user} in session {session_id}, just saying.. ")
        profile : GameRoundProfileData = profile_query.first()
        if profile:
            if CardSubmission.objects.filter(connected_game_round_profile=profile).exists():
                return Response(True ,status=status.HTTP_200_OK)
        return Response(False, status=status.HTTP_404_NOT_FOUND)