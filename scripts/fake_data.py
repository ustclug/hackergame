#!/usr/bin/env python3

import random
import sys

import django
from django.db.transaction import atomic

assert sys.path[0].endswith('/scripts')
sys.path[0] = sys.path[0][:-8]
django.setup()

from apps.otp.models import Device
from server.challenge.interface import Challenge
from server.submission.interface import Submission
from server.terms.interface import Terms
from server.trigger.interface import Trigger
from server.user.interface import User
from server.context import Context
from server.exceptions import NotFound


with atomic():
    root = User.create(Context(), group='console', nickname='root').user
    root.is_staff = True
    root.is_superuser = True
    root.save()
    root.refresh_from_db()
    Device.objects.create(backend='console', identity='root', user=root)

    c1 = Challenge.create(
        Context(root),
        name='签到题',
        category='checkin',
        detail='签到题描述',
        url='https://example.com/{token}',
        prompt='flag{hackergame}',
        index=-100,
        enabled=True,
        flags=[{
            'name': '',
            'score': 10,
            'type': 'text',
            'flag': 'flag{hackergame}',
        }],
    )
    Submission.submit(Context(root), root.pk, c1.pk, 'flag{hackergame}')

    for i in range(1, 11):
        Challenge.create(
            Context(root),
            name=f'复杂题 {i}',
            category='complex',
            detail='<code>flag{FLAG_INDEX}</code> 或 '
                   '<code>flag{FLAG_INDEX:USER_ID}</code>',
            url='',
            prompt='flag{...}',
            index=random.randrange(100),
            enabled=random.choice((False, True, True, True, True)),
            flags=[{
                'name': f'flag {j}',
                'score': random.randrange(100),
                'type': ('expr', 'text')[j % 2],
                'flag': (f"f'flag{{{{{j}:{{token.partition(\":\")[0]}}}}}}'",
                         f'flag{{{j}}}')[j % 2],
            } for j in range(random.randrange(1, 4))],
        )

    for i in range(1, 30):
        Challenge.create(
            Context(root),
            name=f'简单题 {i}',
            category='simple',
            detail='',
            url='',
            prompt=('flag{0}', 'flag{0:USER_ID}')[i % 2],
            index=random.randrange(100),
            enabled=random.choice((False, True, True, True, True)),
            flags=[{
                'name': '',
                'score': random.randrange(100),
                'type': ('text', 'expr')[i % 2],
                'flag': ('flag{0}',
                         "'flag{0:'+token.partition(':')[0]+'}'")[i % 2],
            }],
        )

    terms = Terms.create(Context(root), name='条款', content='1 2 3 ...',
                         enabled=True)

    Trigger.create(Context(root), time=Context(root).time, state=True)

    for i in range(1000):
        print('user', i, end='\r')
        u = User.create(
            Context(root),
            group=random.choice(list(User.groups.keys())),
            nickname=f'用户 {i}',
            name='姓名',
            sno='PB11111111',
            tel='123456789',
            email='foo@example.com',
        )
        Terms.get(Context(u.user), terms.pk).agree(u.pk)

    users = [i.pk for i in User.get_all(Context(root))]
    challenges = [i.pk for i in Challenge.get_all(Context(root))]
    for i in range(5000):
        print('submission', i, end='\r')
        try:
            u = random.choice(users)
            c = random.choice(challenges)
            fs = len(Challenge.get(Context(root), c).flags)
            Submission.submit(Context(User.get(Context(root), u).user), u, c,
                              f'flag{{{random.choice(range(fs))}:{u}}}')
            Submission.submit(Context(User.get(Context(root), u).user), u, c,
                              f'flag{{{random.choice(range(fs))}}}')
        except NotFound:
            pass

    Challenge.create(
        Context(root),
        name='难题',
        category='hard',
        detail='难题描述',
        url='https://example.com/{token}',
        prompt='flag{hackergame}',
        index=100,
        enabled=True,
        flags=[{
            'name': '',
            'score': 100,
            'type': 'text',
            'flag': 'flag{hackergame}',
        }],
    )
