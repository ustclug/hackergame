# Generated by Django 3.1 on 2020-08-14 13:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('announcement', '0002_announcement_challenge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='created_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]