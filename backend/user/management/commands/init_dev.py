import random
from datetime import datetime, timedelta

import pytz
from django.core.management.base import BaseCommand
from django.core import management
from django.db import IntegrityError

from user.models import User, Term
from challenge.models import Challenge, SubChallenge
from submission.models import Submission
from contest.models import Stage
from group.models import Group, Application


class Command(BaseCommand):
    help = 'Create dev environments.'

    def add_arguments(self, parser):
        parser.add_argument('-C', '--complex-challenges',
                            type=int, default=10)
        parser.add_argument('-c', '--simple-challenges',
                            type=int, default=20)
        parser.add_argument('-U', '--users',
                            type=int, default=30)
        parser.add_argument('-G', '--groups',
                            type=int, default=10)
        parser.add_argument('-S', '--submissions',
                            type=int, default=200)

    # @transaction.atomic
    def handle(self, **options):
        management.call_command('migrate')

        start_time = datetime(2020, 7, 24, 22, 47, 0, tzinfo=pytz.utc)
        end_time = start_time + timedelta(weeks=52 * 100)
        practice_start_time = end_time + timedelta(days=2)
        Stage.objects.create(start_time=start_time, end_time=end_time,
                             practice_start_time=practice_start_time)

        root = User.objects.create_superuser(username='root', password='root')

        Term.objects.create(name='term', content='test')

        c1 = Challenge.objects.create(
            name='签到题',
            category='checkin',
            detail='签到题描述',
            prompt='flag{hackergame}',
            index=-100,
        )
        SubChallenge.objects.create(
            challenge=c1,
            name='',
            score=50,
            flag_type='text',
            flag='flag{hackergame}'
        )
        Submission.objects.create(user=root, challenge=c1, flag='flag{hackergame}')

        for i in range(1, options['complex_challenges'] + 1):
            c = Challenge.objects.create(
                name=f'复杂题 {i}',
                category='complex',
                detail='<code>flag{FLAG_INDEX}</code> 或 '
                       '<code>flag{FLAG_INDEX:USER_TOKEN}</code>',
                prompt='flag{...}',
                index=random.randrange(100),
            )
            for j in range(random.randrange(1, 4)):
                SubChallenge.objects.create(
                    challenge=c,
                    name=f'flag {j}',
                    score=random.randrange(100),
                    flag_type=('expr', 'text')[j % 2],
                    enabled=random.choice((False, True, True, True, True)),
                    flag=(
                        "f'flag{{%s:{token}}}'" % j,
                        f'flag{{{j}}}'
                    )[j % 2]
                )

        for i in range(1, options['simple_challenges'] + 1):
            c = Challenge.objects.create(
                name=f'简单题 {i}',
                category='simple',
                detail='',
                prompt=('flag{0}', 'flag{0:USER_TOKEN}')[i % 2],
                index=random.randrange(100),
            )
            SubChallenge.objects.create(
                challenge=c,
                name='',
                score=random.randrange(100),
                flag_type=('text', 'expr')[i % 2],
                enabled=random.choice((False, True, True, True, True)),
                flag=(
                    'flag{0}',
                    "'flag{0:'+token+'}'"
                )[i % 2]
            )

        users = []
        for i in range(1, options['users'] + 1):
            print(f'User {i}')
            users.append(User.objects.create_user(
                username=f'user{i}',
                password=f'user{i}',
                phone_number='123456789',
                email='foo@bar.com',
                term_agreed=True
            ))

        groups = []
        for i in range(1, options['groups'] + 1):
            print(f'Group {i}')
            groups.append(Group.objects.create(
                name=f'Group {i}',
                admin=random.choice(users),
                rule_has_phone_number=False,
                rule_has_email=True,
                rule_email_suffix='xx.edu.cn',
                rule_has_name=False,
                rule_must_be_verified_by_admin=True,
            ))

        for user in users:
            for i in range(random.randrange(10)):
                try:
                    group = random.choice(groups)
                    Application.objects.create(
                        user=user,
                        group=group,
                        status='accepted',
                        apply_message=f'apply for {group.name}'
                    )
                # 可能会加入重复的组
                except IntegrityError:
                    pass

        challenges = list(Challenge.objects.all())
        accumulated_time = timedelta(seconds=10)
        for i in range(options['submissions']):
            user = random.choice(users)
            challenge = random.choice(challenges)
            sub_challenges = list(challenge.sub_challenge.all())
            time = start_time + accumulated_time
            accumulated_time += timedelta(seconds=random.randrange(3600))
            s1 = Submission.objects.create(
                user=user,
                challenge=challenge,
                flag=f'flag{{{random.randrange(len(sub_challenges))}}}',
                created_time=time
            )
            print(s1)
            s2 = Submission.objects.create(
                user=user,
                challenge=challenge,
                flag=f'flag{{{random.randrange(len(sub_challenges))}:{user.token}}}',
                created_time=time
            )
            print(s2)
        print('Done.')
