# Generated by Django 2.2.3 on 2019-07-09 14:34

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('translations', '0001_initial'),
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='password_renewal_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='password_renewal_template', to='home.EmailTemplate'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='verify_email_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='verify_email_template', to='home.EmailTemplate'),
        ),
        migrations.CreateModel(
            name='EmailTemplateTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', ckeditor.fields.RichTextField()),
                ('subject', models.CharField(max_length=100)),
                ('language', models.ForeignKey(default='lt', on_delete=django.db.models.deletion.CASCADE, to='translations.Language')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_template_translations', to='home.EmailTemplate')),
            ],
            options={
                'unique_together': {('template', 'language')},
            },
        ),
    ]