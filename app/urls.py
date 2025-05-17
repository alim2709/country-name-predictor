from django.urls import path
from .views import NameCountryAPIView, PopularNamesAPIView

urlpatterns = [
    path("names/", NameCountryAPIView.as_view(), name="names"),
    path("popular-names/", PopularNamesAPIView.as_view(), name="popular-names"),
]
