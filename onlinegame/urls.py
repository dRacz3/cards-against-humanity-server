from django.conf.urls import url
from django.contrib import admin
from rest_framework.schemas import get_schema_view
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="CardsAgainstHumanity-Django API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('card-api/', include('cardstore.api.urls')),
    path('game_engine_api/', include('game_engine.api.urls')),
    path('game_engine/', include('game_engine.urls')),
    path("api-auth/", include("rest_framework.urls")),
    path("api/rest-auth/", include("rest_auth.urls")),
    path("api/rest-auth/registration/", include("rest_auth.registration.urls")),

    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
