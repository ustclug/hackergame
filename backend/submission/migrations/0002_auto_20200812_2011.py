# Generated by Django 3.1 on 2020-08-12 12:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('challenge', '0002_auto_20200812_2011'),
        ('group', '0002_auto_20200812_2011'),
        ('submission', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='submission',
            name='violation_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='violation_submission', to=settings.AUTH_USER_MODEL, verbose_name='和该用户的某一 flag 重复'),
        ),
        migrations.AddField(
            model_name='subchallengefirstblood',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='group.group'),
        ),
        migrations.AddField(
            model_name='subchallengefirstblood',
            name='sub_challenge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='challenge.subchallenge'),
        ),
        migrations.AddField(
            model_name='subchallengefirstblood',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='scoreboard',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='challengefirstblood',
            name='challenge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='challenge.challenge'),
        ),
        migrations.AddField(
            model_name='challengefirstblood',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='group.group'),
        ),
        migrations.AddField(
            model_name='challengefirstblood',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='submission',
            constraint=models.UniqueConstraint(fields=('user', 'sub_challenge_clear'), name='unique_sub_challenge_clear'),
        ),
        migrations.AddConstraint(
            model_name='subchallengefirstblood',
            constraint=models.UniqueConstraint(fields=('sub_challenge', 'group'), name='unique_sub_challenge_first'),
        ),
        migrations.AddConstraint(
            model_name='scoreboard',
            constraint=models.UniqueConstraint(fields=('user', 'category'), name='unique_score_category'),
        ),
        migrations.AddConstraint(
            model_name='challengefirstblood',
            constraint=models.UniqueConstraint(fields=('challenge', 'group'), name='unique_challenge_first'),
        ),
    ]