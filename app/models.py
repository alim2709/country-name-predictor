from django.db import models


class Name(models.Model):
    name = models.CharField(max_length=255, unique=True)
    count_of_requests = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Country(models.Model):
    country_code = models.CharField(max_length=10, unique=True)
    country_name = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    independent = models.BooleanField(default=False)
    google_maps_url = models.URLField(max_length=500, blank=True)
    open_street_map_url = models.URLField(max_length=500, blank=True)
    capital_name = models.CharField(max_length=255, blank=True)
    capital_latitude = models.FloatField(null=True, blank=True)
    capital_longitude = models.FloatField(null=True, blank=True)
    flag_png = models.URLField(max_length=500, blank=True)
    flag_svg = models.URLField(max_length=500, blank=True)
    flag_alt = models.CharField(max_length=255, blank=True)
    coat_of_arms_png = models.URLField(max_length=500, blank=True)
    coat_of_arms_svg = models.URLField(max_length=500, blank=True)
    borders_with = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.country_name


class NameCountryProbability(models.Model):
    name = models.ForeignKey(Name, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    probability = models.FloatField()

    class Meta:
        unique_together = ("name", "country")

    def __str__(self):
        return f"{self.name} - {self.country}: {self.probability}"
