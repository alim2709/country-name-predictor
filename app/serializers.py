from rest_framework import serializers
from .models import Name, Country, NameCountryProbability


class CountryProbabilitySerializer(serializers.ModelSerializer):
    country_code = serializers.CharField(source="country.country_code")
    country_name = serializers.CharField(source="country.country_name")
    region = serializers.CharField(source="country.region")
    independent = serializers.BooleanField(source="country.independent")
    google_maps_url = serializers.CharField(source="country.google_maps_url")
    open_street_map_url = serializers.CharField(source="country.open_street_map_url")
    capital_name = serializers.CharField(source="country.capital_name")
    capital_latitude = serializers.FloatField(source="country.capital_latitude")
    capital_longitude = serializers.FloatField(source="country.capital_longitude")
    flag_png = serializers.CharField(source="country.flag_png")
    flag_svg = serializers.CharField(source="country.flag_svg")
    flag_alt = serializers.CharField(source="country.flag_alt")
    coat_of_arms_png = serializers.CharField(source="country.coat_of_arms_png")
    coat_of_arms_svg = serializers.CharField(source="country.coat_of_arms_svg")
    borders_with = serializers.JSONField(source="country.borders_with")

    probability = serializers.FloatField()

    class Meta:
        model = NameCountryProbability
        fields = [
            "country_code",
            "country_name",
            "region",
            "independent",
            "google_maps_url",
            "open_street_map_url",
            "capital_name",
            "capital_latitude",
            "capital_longitude",
            "flag_png",
            "flag_svg",
            "flag_alt",
            "coat_of_arms_png",
            "coat_of_arms_svg",
            "borders_with",
            "probability",
        ]


class NameSerializer(serializers.ModelSerializer):
    countries = serializers.SerializerMethodField()

    class Meta:
        model = Name
        fields = ["name", "count_of_requests", "last_accessed", "countries"]

    def get_countries(self, obj):
        name_countries = NameCountryProbability.objects.filter(name=obj)
        return CountryProbabilitySerializer(name_countries, many=True).data
