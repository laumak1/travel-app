# Generated by Django 4.2.2 on 2023-11-08 11:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("locations", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BaseSite",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("longitude", models.FloatField()),
                ("latitude", models.FloatField()),
                ("title", models.CharField(max_length=255)),
                ("city", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="locations.city")),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Site",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("overview", models.TextField()),
                ("language", models.CharField(max_length=3)),
                ("source", models.CharField(max_length=255)),
                ("is_approved", models.BooleanField(default=False)),
                (
                    "author",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
                    ),
                ),
                ("base_site", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="sites.basesite")),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SiteTag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=50)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SiteImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("image", models.ImageField(upload_to="media/site_images/")),
                ("thumbnail", models.ImageField(upload_to="media/site_thumbnails/")),
                ("source", models.CharField(max_length=255)),
                ("base_site", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="sites.basesite")),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SiteAudio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("url", models.FileField(upload_to="media/site_audio/")),
                ("duration", models.PositiveIntegerField()),
                ("language", models.CharField(max_length=3)),
                ("source", models.CharField(max_length=255)),
                ("site", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="sites.site")),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="site",
            name="tags",
            field=models.ManyToManyField(related_name="tags", to="sites.sitetag"),
        ),
    ]