# Generated by Django 5.0.1 on 2024-02-01 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mishwari_main_app', '0014_alter_subtrips_arrival_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trips',
            name='arrival_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trips',
            name='distance',
            field=models.FloatField(default=0.0, help_text='Distance in kilometers'),
        ),
    ]
