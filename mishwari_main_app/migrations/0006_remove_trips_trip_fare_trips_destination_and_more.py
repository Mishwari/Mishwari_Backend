# Generated by Django 4.2.7 on 2023-11-07 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mishwari_main_app', '0005_driver_is_charger_driver_is_wifi_tripfare_path_road_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trips',
            name='trip_fare',
        ),
        migrations.AddField(
            model_name='trips',
            name='destination',
            field=models.CharField(choices=[('SYN', 'Seiyon'), ('MKL', 'AL-Mukalla'), ('ADN', 'Aden'), ('ATQ', 'Ataq'), ('TRM', 'Tarim'), ('TAZ', 'Taiz'), ('SAN', "Sana'a"), ('QTN', 'AL-Qaten'), ('SHN', 'Shehen'), ('WDY', 'AL-Wadeiya'), ('MRB', 'Marib'), ('HDH', 'AL-Hudaidah'), ('EBB', 'Ebb'), ('BYD', 'AL-Bidaa')], default='unknown', max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trips',
            name='path_road',
            field=models.CharField(blank=True, default='unknown road', max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='trips',
            name='pickup',
            field=models.CharField(choices=[('SYN', 'Seiyon'), ('MKL', 'AL-Mukalla'), ('ADN', 'Aden'), ('ATQ', 'Ataq'), ('TRM', 'Tarim'), ('TAZ', 'Taiz'), ('SAN', "Sana'a"), ('QTN', 'AL-Qaten'), ('SHN', 'Shehen'), ('WDY', 'AL-Wadeiya'), ('MRB', 'Marib'), ('HDH', 'AL-Hudaidah'), ('EBB', 'Ebb'), ('BYD', 'AL-Bidaa')], default=0, max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trips',
            name='price',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='driver',
            name='car_type',
            field=models.CharField(choices=[('mass', 'mass bus'), ('bulka', 'bulka bus')], default='bulka', max_length=30),
        ),
        migrations.DeleteModel(
            name='TripFare',
        ),
    ]
