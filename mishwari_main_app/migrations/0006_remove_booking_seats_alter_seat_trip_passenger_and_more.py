# Generated by Django 5.0.1 on 2024-05-12 18:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mishwari_main_app', '0005_rename_subtrips_alltrips_rename_trips_maintrip_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='seats',
        ),
        migrations.AlterField(
            model_name='seat',
            name='trip',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, related_name='seats', to='mishwari_main_app.alltrips'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BookingPassenger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mishwari_main_app.booking')),
                ('seat', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mishwari_main_app.seat')),
                ('passenger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mishwari_main_app.passenger')),
            ],
        ),
        migrations.AddField(
            model_name='booking',
            name='passengers',
            field=models.ManyToManyField(through='mishwari_main_app.BookingPassenger', to='mishwari_main_app.passenger'),
        ),
    ]
