# Generated by Django 2.1.5 on 2019-01-16 07:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('translations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manifest_version', models.CharField(default='1', max_length=300)),
                ('default_language', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='default_inform_language', to='translations.Language')),
                ('enabled_languages', models.ManyToManyField(related_name='enabled_inform_languages', to='translations.Language')),
            ],
            options={
                'verbose_name': 'Site Configuration',
            },
        ),
    ]
