import random
import markdown.treeprocessors

from django.core.management.base import BaseCommand
from django.db.transaction import atomic
from django.utils import timezone
from django.contrib.auth import get_user_model

from server.challenge.interface import Challenge
from server.submission.interface import Submission
from server.terms.interface import Terms
from server.trigger.interface import Trigger
from server.user.interface import User
from server.context import Context
from server.exceptions import NotFound
from server.submission.interface import SlowDown
from ...models import Account


class Command(BaseCommand):
    help = '填充假数据用于测试'

    def add_arguments(self, parser):
        parser.add_argument('-C', '--fake_complex_challenges',
                            type=int, default=10)
        parser.add_argument('-c', '--fake_simple_challenges',
                            type=int, default=29)
        parser.add_argument('-U', '--fake_users',
                            type=int, default=100)
        parser.add_argument('-S', '--fake_submissions',
                            type=int, default=500)
        parser.add_argument('--game_started_seconds', '--seconds',
                            type=int, default=3600 * 24 * 7)

    @atomic
    def handle(self, fake_complex_challenges, fake_simple_challenges,
               fake_users, fake_submissions, game_started_seconds,
               **options):
        if get_user_model().objects.count() > 0:
            raise RuntimeError('数据库中已有用户，停止生成假数据。')
        root = User.create(
            Context(elevated=True),
            group='other',
        )
        # by default when can_update_profile does not exist
        # all nickname will be set to "选手" by User.create
        root._update(nickname='root')
        root = root.user
        root.is_staff = True
        root.is_superuser = True
        root.save()
        root.refresh_from_db()
        Account.objects.create(provider='debug', identity='root', user=root)

        nobody = User.create(
            Context(elevated=True),
            group='other',
        )
        nobody._update(nickname='nobody')
        nobody = nobody.user
        nobody.is_staff = False
        nobody.is_superuser = False
        nobody.save()
        nobody.refresh_from_db()
        Account.objects.create(provider='debug', identity='nobody', user=nobody)

        c1 = Challenge.create(
            Context(root),
            name='签到题',
            category='checkin',
            detail='签到题描述',
            url_orig='https://example.com/{token}',
            check_url_clicked=True,
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

        for i in range(1, fake_complex_challenges + 1):
            choice = random.choice((1, 2, 2, 3))
            if choice == 1:
                detail = """<p>众所周知，对 $x$ 求导得到的结果为 1。<code>flag{FLAG_INDEX}</code></p>
                <p>块状公式测试 <code>flag{FLAG_INDEX:USER_ID}</code></p>
                <p>$$\\frac{1}{3} = \\frac{2}{6}$$</p>
                """
            elif choice == 2:
                detail = '<code>flag{FLAG_INDEX}</code> 或 <code>flag{FLAG_INDEX:USER_ID}</code>'
            elif choice == 3:
                # test markdown code block
                detail = markdown.markdown(
                    """```python
def a():
    pass
```""", extensions=['codehilite', 'fenced_code'],
                )
            Challenge.create(
                Context(root),
                name=f'复杂题 {i}',
                category='complex',
                detail=detail,
                url_orig='',
                prompt='flag{...}',
                index=random.randrange(100),
                enabled=random.choice((False, True, True, True, True)),
                flags=[{
                    'name': f'flag {j}',
                    'score': random.randrange(100),
                    'type': ('expr', 'text')[j % 2],
                    'flag': ("f'flag{{%s:{token.partition(\":\")[0]}}}'" % j,
                             f'flag{{{j}}}')[j % 2],
                } for j in range(random.randrange(1, 4))],
            )

        for i in range(1, fake_simple_challenges + 1):
            Challenge.create(
                Context(root),
                name=f'简单题 {i}',
                category='simple',
                detail='',
                url_orig='',
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
        Terms.get(Context(nobody), terms.pk).agree(nobody.pk)

        now = timezone.now()
        timestamps = []
        for i in range(fake_submissions):
            delta = random.randrange(game_started_seconds)
            timestamps.append(now - timezone.timedelta(seconds=delta))
        timestamps.sort()

        Trigger.create(
            Context(root),
            time=min(timestamps),
            can_view_challenges=True,
            can_try=True,
            can_submit=True,
            can_update_profile=True,
        )

        groups = list(set(User.groups.keys()) - {'noscore', 'banned', 'suspicious'})
        for i in range(fake_users):
            print('user', i, end='\r')
            u = User.create(
                Context(elevated=True),
                group=random.choice(groups),
                nickname='用户 ' + str(i) + f' | foo #a{i%3} #b{i%3}',
                name='姓名',
                sno='PB11111111',
                tel='123456789',
                email='foo@example.com',
                gender=random.choice(('female', 'male')),
                qq='12345',
                website='website',
                school='foo',
                grade='1',
                major='CS',
                campus='East',
                aff='aff',
            )
            Terms.get(Context(u.user), terms.pk).agree(u.pk)
            Account.objects.create(provider='debug', identity=f'{i}',
                                   user=u.user)

        users = [i.pk for i in User.get_all(Context(root))]
        challenges = [i.pk for i in Challenge.get_all(Context(root))]

        for i in range(fake_submissions):
            print('submission', i, end='\r')
            try:
                u = random.choice(users)
                c = random.choice(challenges)
                fs = len(Challenge.get(Context(root), c).flags)
                Submission.submit(
                    Context(
                        User.get(Context(root), u).user,
                        timestamps[i]
                    ), u, c, f'flag{{{random.choice(range(fs))}:{u}}}'
                )
                Submission.submit(
                    Context(
                        User.get(Context(root), u).user,
                        timestamps[i] + timezone.timedelta(seconds=20)
                    ), u, c, f'flag{{{random.choice(range(fs))}}}'
                )
            except (NotFound, SlowDown):
                pass

        Challenge.create(
            Context(root),
            name='难题',
            category='hard',
            detail='难题描述',
            url_orig='https://example.com/{token}',
            check_url_clicked=False,
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
