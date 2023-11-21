# Generated by Django 4.2.2 on 2023-11-17 13:12

from django.contrib.gis.geos import Point
from django.db import migrations


def forwards_func(apps, schema_editor):
    BaseSite = apps.get_model("sites", "BaseSite")
    db_alias = schema_editor.connection.alias

    sites_with_coordinates = BaseSite.objects.using(db_alias).exclude(
        longitude=None, latitude=None
    )

    for site in sites_with_coordinates:
        site.location = Point(site.longitude, site.latitude, srid=4326)

    BaseSite.objects.using(db_alias).bulk_update(sites_with_coordinates, fields=["location"])


class Migration(migrations.Migration):
    dependencies = [
        ("sites", "0003_basesite_location"),
    ]

    operations = [migrations.RunPython(forwards_func)]
