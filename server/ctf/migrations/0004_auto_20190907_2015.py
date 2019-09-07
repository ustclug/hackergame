# Generated by Django 2.1.12 on 2019-09-07 12:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ctf', '0003_problem_prompt'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserFlagCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flag_text', models.TextField(db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserFlagViolation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flag', models.TextField()),
                ('time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterField(
            model_name='flag',
            name='flag',
            field=models.TextField(help_text="如果为静态 flag，请直接填入 flag。如果 flag 为 <code>'flag{' + hashlib.sha256(b'secret' + token.encode()).hexdigest()[:16] + '}'</code>，请填入 <code>flag{' + hashlib.sha256(b'secret' + token.encode()).hexdigest()[:16] + '}</code>（去掉最外侧的引号）。"),
        ),
        migrations.AddField(
            model_name='userflagviolation',
            name='match_flag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ctf.Flag'),
        ),
        migrations.AddField(
            model_name='userflagviolation',
            name='match_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='userflagviolated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userflagviolation',
            name='problem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ctf.Problem'),
        ),
        migrations.AddField(
            model_name='userflagviolation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userflagcache',
            name='flag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ctf.Flag'),
        ),
        migrations.AddField(
            model_name='userflagcache',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
