import pytest

from challenge.models import Challenge, SubChallenge, ExprFlag


@pytest.fixture
def challenge(user, stage):
    # user 能保证 ExprFlag 有表有条目
    c = Challenge.objects.create(
        index=1,
        name='test_challenge',
        category='test',
        detail='test_detail',
        prompt='test_prompt'
    )
    SubChallenge.objects.create(
        challenge=c,
        name='1',
        score=50,
        enabled=True,
        flag_type='expr',
        flag='"flag{"+md5("secret"+token)+"}"'
    )
    SubChallenge.objects.create(
        challenge=c,
        name='2',
        score=100,
        enabled=False,
        flag_type='text',
        flag='flag{abc}'
    )
    return c


def test_enabled(challenge):
    assert challenge.enabled is True
    for sub in challenge.sub_challenge.all():
        sub.enabled = False
        sub.save()
    assert challenge.enabled is False


def test_expr_flag(challenge, user):
    from challenge.utils import functions
    flag = f'flag{{{functions["md5"]("secret"+user.token)}}}'
    sub_challenge = SubChallenge.objects.get(challenge=challenge, name='1')
    assert flag == ExprFlag.objects.get(user=user, sub_challenge=sub_challenge).flag


def test_challenge_api(challenge, client):
    r = client.get('/api/challenge/')
    assert r.data[0]['id'] == challenge.id
    sub_challenge = SubChallenge.objects.get(challenge=challenge, name='1')
    assert r.data[0]['sub_challenge'][0]['id'] == sub_challenge.id
