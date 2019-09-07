# Generated by Django 2.1.2 on 2018-10-13 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UstcFirstBlood',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('problem', models.TextField(db_column='name')),
                ('user', models.TextField(db_column='first_blood')),
            ],
            options={
                'db_table': 'ustc_first_blood',
                'managed': False,
            },
        ),
    ]