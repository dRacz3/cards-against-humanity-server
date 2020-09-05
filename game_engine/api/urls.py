from django.urls import include, path
from rest_framework.routers import DefaultRouter
from game_engine.api.views import ProfileViewSet, GameSessionViewSet, ProfileDataBasedOnSessionDataViewSet, \
    GameRoundProfileDataViewSet, GameSessionOperations, GameRoundsBasedOnSessionsViewSet

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet)
router.register(r"sessions", GameSessionViewSet)
router.register(r"gameroundprofiledata", GameRoundProfileDataViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("session/<int:session_id>/profiles", ProfileDataBasedOnSessionDataViewSet.as_view(),
         name="session-profile-view"),
    path("session/<int:session_id>/rounds", GameRoundsBasedOnSessionsViewSet.as_view(), name="session-round-view"),
    path("session/<int:session_id>/ops/", GameSessionOperations.as_view(), name="session_ops")
]
