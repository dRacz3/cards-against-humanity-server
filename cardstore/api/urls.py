from django.urls import path
from cardstore.api.views import whitecard_list_create_api_view, whitecard_detail_api_view, \
    blackcard_list_create_api_view, blackcard_detail_api_view

urlpatterns = [
    path("whitecards/", whitecard_list_create_api_view, name="whitecards"),
    path("whitecards/<int:pk>", whitecard_detail_api_view, name="whitecard-details"),
    path("blackcards/", blackcard_list_create_api_view, name="blackcards"),
    path("blackcards/<int:pk>", blackcard_detail_api_view, name="blackcard-details"),

]
