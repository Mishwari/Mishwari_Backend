# Generated by Django 5.0.1 on 2024-02-01 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mishwari_main_app', '0012_subtrips_distance_trips_distance_alter_citylist_city_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subtrips',
            name='distance',
            field=models.FloatField(default=0.0, help_text='Distance in kilometers'),
        ),
    ]
