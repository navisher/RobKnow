# Generated by Django 2.1.5 on 2019-01-25 14:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_content_file_image_text_video'),
    ]

    operations = [
        migrations.RenameField(
            model_name='video',
            old_name='file',
            new_name='url',
        ),
    ]