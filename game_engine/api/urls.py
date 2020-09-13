from django.urls import include, path
from rest_framework.routers import DefaultRouter
from game_engine.api.views import ProfileViewSet, GameSessionViewSet, ProfileDataBasedOnSessionDataViewSet, \
    GameRoundProfileDataViewSet, GameRoundsBasedOnSessionsViewSet, CardSubmissionsRoundsViewSet, \
    SessionStateView, CheckCardsInUserHand, SubmitCard

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet)
router.register(r"sessions", GameSessionViewSet)
router.register(r"gameroundprofiledata", GameRoundProfileDataViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("session/<str:session_id>/profiles", ProfileDataBasedOnSessionDataViewSet.as_view(),
         name="session-profile-view"),
    path("session/<str:session_id>/rounds", GameRoundsBasedOnSessionsViewSet.as_view(), name="session-round-view"),
    path("session/<str:session_id>/view", SessionStateView.as_view(), name="session-overview"),
    path("session/<str:session_id>/submissions/", CardSubmissionsRoundsViewSet.as_view(), name="last-round-submissions"),
    path("session/<str:session_id>/mycards/", CheckCardsInUserHand.as_view(), name="cards-in-user-hand"),
    path("session/<str:session_id>/submit/", SubmitCard.as_view(), name="submit-card")
]
