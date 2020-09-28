from django.urls import path, include
from cardstore.api.views import WhiteCardViewSet, BlackCardViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"white_cards", WhiteCardViewSet)
router.register(r'black_cards', BlackCardViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
