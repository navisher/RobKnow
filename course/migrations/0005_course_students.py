# Generated by Django 2.0.5 on 2019-01-29 11:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0004_auto_20190125_1425'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(blank=True, related_name='course_enrolled', to=settings.AUTH_USER_MODEL),
        ),
    ]
