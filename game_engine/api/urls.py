from django.urls import include, path
from rest_framework.routers import DefaultRouter
from game_engine.api.views import ProfileViewSet, GameRoomViewSet

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet)
router.register(r"rooms", GameRoomViewSet)

urlpatterns = [
    path("", include(router.urls)),
]