from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from .models import Name, Country, NameCountryProbability

User = get_user_model()


class NameCountryAuthTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("names")

        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "testuser", "password": "testpass123"},
        )
        self.access_token = response.data["access"]

    def test_unauthenticated_access_denied(self):
        response = self.client.get(self.url, {"name": "John"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("app.views.httpx.Client")
    def test_authenticated_access_success(self, mock_httpx_client):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        mock_client_instance = MagicMock()
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.get.side_effect = [
            MagicMock(
                status_code=200,
                json=lambda: {
                    "country": [
                        {"country_id": "US", "probability": 0.7},
                    ]
                },
            ),
            MagicMock(
                status_code=200,
                json=lambda: [
                    {
                        "name": {"common": "United States"},
                        "region": "Americas",
                        "independent": True,
                        "maps": {"googleMaps": "url1", "openStreetMaps": "url2"},
                        "capital": ["Washington"],
                        "capitalInfo": {"latlng": [1.0, 2.0]},
                        "flags": {"png": "flag_png", "svg": "flag_svg", "alt": "alt"},
                        "coatOfArms": {"png": "coa_png", "svg": "coa_svg"},
                        "borders": ["CAN", "MEX"],
                    }
                ],
            ),
        ]

        response = self.client.get(self.url, {"name": "John"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "John")
        self.assertTrue("countries" in response.data)


class PopularNamesAuthTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("popular-names")
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "testuser", "password": "testpass123"},
        )
        self.access_token = response.data["access"]

        self.country = Country.objects.create(
            country_code="US", country_name="United States", region="Americas"
        )
        self.name1 = Name.objects.create(name="John", count_of_requests=5)
        self.name2 = Name.objects.create(name="Mike", count_of_requests=3)
        NameCountryProbability.objects.create(
            name=self.name1, country=self.country, probability=0.7
        )
        NameCountryProbability.objects.create(
            name=self.name2, country=self.country, probability=0.2
        )

    def test_unauthenticated_access_denied(self):
        response = self.client.get(self.url, {"country": "US"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_access_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.url, {"country": "US"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["country"], "US")
        self.assertEqual(len(response.data["top_names"]), 2)
        self.assertEqual(response.data["top_names"][0]["name"], "John")
