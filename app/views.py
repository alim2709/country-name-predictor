from datetime import timedelta
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django.db.models import Count

import httpx

from .models import Name, Country, NameCountryProbability
from .serializers import NameSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

NATIONALIZE_API_URL = "https://api.nationalize.io/"
RESTCOUNTRIES_API_URL = "https://restcountries.com/v3.1/alpha/"


class NameCountryAPIView(APIView):

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                type=str,
                location="query",
                required=True,
                description="Name to search",
            ),
        ],
        responses={200: NameSerializer},
    )
    def get(self, request):
        name_query = request.query_params.get("name")
        if not name_query:
            return Response(
                {"detail": 'Missing "name" parameter.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = self.get_or_create_name_record(name_query)
        if isinstance(result, Response):
            return result
        serializer = NameSerializer(result)
        return Response(serializer.data)

    def get_or_create_name_record(self, name_query):
        current_time = timezone.now()
        existing_name = Name.objects.filter(name__iexact=name_query).first()
        data_is_recent = (
            existing_name is not None
            and existing_name.last_accessed is not None
            and (current_time - existing_name.last_accessed) < timedelta(days=1)
        )

        if existing_name and data_is_recent:
            self.update_existing_name(existing_name, current_time)
            return existing_name
        else:
            result = self.fetch_and_create_name(name_query, current_time, existing_name)
            return result

    def update_existing_name(self, existing_name, current_time):
        existing_name.count_of_requests += 1
        existing_name.last_accessed = current_time
        existing_name.save()

    def fetch_and_create_name(self, name_query, current_time, existing_name=None):
        with httpx.Client() as client:
            nationalize_data = self.fetch_nationalize_data(client, name_query)
            if not nationalize_data:
                return Response(
                    {"detail": f"No country predictions for name '{name_query}'."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if existing_name:
                existing_name.count_of_requests += 1
                existing_name.last_accessed = current_time
                existing_name.save()
                NameCountryProbability.objects.filter(name=existing_name).delete()
            else:
                existing_name = Name.objects.create(
                    name=name_query, count_of_requests=1, last_accessed=current_time
                )

            self.process_country_predictions(nationalize_data, client, existing_name)

        return existing_name

    def fetch_nationalize_data(self, client, name_query):
        nationalize_response = client.get(
            NATIONALIZE_API_URL, params={"name": name_query}
        )
        if nationalize_response.status_code != 200:
            return None
        return nationalize_response.json().get("country")

    def process_country_predictions(self, country_predictions, client, existing_name):
        for prediction in country_predictions:
            predicted_country_code = prediction["country_id"]
            predicted_probability = prediction["probability"]

            country_record = self.get_or_create_country(client, predicted_country_code)
            if country_record:
                NameCountryProbability.objects.create(
                    name=existing_name,
                    country=country_record,
                    probability=predicted_probability,
                )

    def get_or_create_country(self, client, country_code):
        country_record = Country.objects.filter(country_code=country_code).first()

        if not country_record:
            country_response = client.get(f"{RESTCOUNTRIES_API_URL}{country_code}")
            if country_response.status_code != 200:
                return None

            try:
                country_info = country_response.json()[0]
            except Exception:
                return None

            country_record = Country.objects.create(
                country_code=country_code,
                country_name=country_info.get("name", {}).get("common", ""),
                region=country_info.get("region", ""),
                independent=country_info.get("independent", False),
                google_maps_url=country_info.get("maps", {}).get("googleMaps", ""),
                open_street_map_url=country_info.get("maps", {}).get(
                    "openStreetMaps", ""
                ),
                capital_name=(
                    country_info.get("capital", [""])[0]
                    if country_info.get("capital")
                    else ""
                ),
                capital_latitude=country_info.get("capitalInfo", {}).get(
                    "latlng", [None, None]
                )[0],
                capital_longitude=country_info.get("capitalInfo", {}).get(
                    "latlng", [None, None]
                )[1],
                flag_png=country_info.get("flags", {}).get("png", ""),
                flag_svg=country_info.get("flags", {}).get("svg", ""),
                flag_alt=country_info.get("flags", {}).get("alt", ""),
                coat_of_arms_png=country_info.get("coatOfArms", {}).get("png", ""),
                coat_of_arms_svg=country_info.get("coatOfArms", {}).get("svg", ""),
                borders_with=country_info.get("borders", []),
            )

        return country_record


class PopularNamesAPIView(APIView):

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="country",
                type=str,
                location="query",
                required=True,
                description="Country code (e.g. US, UA)",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "country": {"type": "string"},
                        "top_names": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "count_of_requests": {"type": "integer"},
                                },
                            },
                        },
                    },
                },
                description="Top 5 most frequent names for a given country",
            )
        },
    )
    def get(self, request):
        country_code = request.query_params.get("country")
        if not country_code:
            return Response(
                {"detail": 'Missing "country" parameter.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        country = Country.objects.filter(country_code=country_code).first()
        if not country:
            return Response(
                {"detail": f"Country '{country_code}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        top_names = (
            NameCountryProbability.objects.filter(country=country)
            .annotate(name_count=Count("name__count_of_requests"))
            .order_by("-name__count_of_requests")[:5]
        )

        if not top_names:
            return Response(
                {"detail": f"No names available for country '{country_code}'."},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_data = [
            {"name": item.name.name, "count_of_requests": item.name.count_of_requests}
            for item in top_names
        ]

        return Response({"country": country_code, "top_names": response_data})
