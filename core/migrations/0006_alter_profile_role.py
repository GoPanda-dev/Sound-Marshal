# Generated by Django 5.1 on 2024-08-12 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_curatorlabelprofile_user_alter_profile_genre_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(blank=True, choices=[('artist', 'Artist'), ('curator', 'Curator/Label')], max_length=50, null=True),
        ),
    ]
