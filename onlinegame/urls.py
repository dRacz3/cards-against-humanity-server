from django.contrib import admin
from rest_framework.schemas import get_schema_view
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('cardstore.api.urls')),
    path('game_engine_api/', include('game_engine.api.urls')),
    path('game_engine/', include('game_engine.urls')),
    path("api-auth/", include("rest_framework.urls")),
    path("api/rest-auth/", include("rest_auth.urls")),
    path("api/rest-auth/registration/", include("rest_auth.registration.urls")),
    path('openapi', get_schema_view(
        title="Cards Agains Humanity DRF API",
        description="API for all things …",
        version="0.0.1"
    ), name='openapi-schema'),
]
