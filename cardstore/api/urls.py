from django.urls import path
from cardstore.api.views import BlackCardDetailsApiView, \
    BlackCardListCreateApiView, WhiteCardDetailsApiView, WhiteCardListCreateApiView, DrawNWhiteCardsApiVeiw

urlpatterns = [
    path("whitecards/", WhiteCardListCreateApiView.as_view(), name="whitecards"),
    path("whitecards/<int:pk>", WhiteCardDetailsApiView.as_view(), name="whitecard-details"),
    path("whitecards/draw/<int:amount>", DrawNWhiteCardsApiVeiw.as_view(), name="draw-n-white-cards"),
    path("blackcards/", BlackCardListCreateApiView.as_view(), name="blackcards"),
    path("blackcards/<int:pk>", BlackCardDetailsApiView.as_view(), name="blackcard-details"),

]
