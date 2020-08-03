import pytest

from challenge.models import Challenge, SubChallenge, ExprFlag
from challenge.utils import functions, eval_token_expression


@pytest.fixture
def challenge(stage):
    c = Challenge.objects.create(
        index=1,
        name='test_challenge',
        category='test',
        detail='test_detail',
        prompt='test_prompt'
    )
    s1 = SubChallenge.objects.create(
        challenge=c,
        name='1',
        score=50,
        enabled=True,
        flag_type='expr',
        flag='"flag{"+md5("secret"+token)+"}"'
    )
    s2 = SubChallenge.objects.create(
        challenge=c,
        name='2',
        score=100,
        enabled=True,
        flag_type='text',
        flag='flag{abc}'
    )
    return c, s1, s2


def test_enabled(challenge):
    challenge, sub1, sub2 = challenge
    sub1.enabled = False
    sub1.save()
    assert challenge.enabled is True
    sub2.enabled = False
    sub2.save()
    assert challenge.enabled is False


def test_expr_flag(challenge, user):
    flag = f'flag{{{functions["md5"]("secret"+user.token)}}}'
    sub_challenge = SubChallenge.objects.get(challenge=challenge[0], name='1')
    assert flag == ExprFlag.objects.get(user=user, sub_challenge=sub_challenge).flag


def test_check_correctness(challenge, user):
    sub1 = challenge[1]
    sub2 = challenge[2]
    sub1_flag = eval_token_expression(sub1.flag, user.token)
    assert sub1.check_correctness(sub1_flag, user) is True
    assert sub2.check_correctness(sub2.flag, user) is True
    assert sub2.check_correctness("wrong_answer", user) is False


def test_check_violation(challenge, user, another_user):
    sub1 = challenge[1]
    user1_flag = eval_token_expression(sub1.flag, user.token)
    user2_flag = eval_token_expression(sub1.flag, another_user.token)
    assert sub1.check_violation(user1_flag, user) is None
    assert sub1.check_violation(user2_flag, user) == another_user


@pytest.mark.xfail  # FIXME
def test_challenge_api(challenge, client):
    challenge = challenge[0]
    r = client.get('/api/challenge/')
    assert r.data[0]['id'] == challenge.id
    enabled_sub_challenge = SubChallenge.objects.get(challenge=challenge, enabled=True)
    ids = map(lambda a: a['id'], r.data[0]['sub_challenge'])
    assert enabled_sub_challenge.id in ids

    # 不应出现未启用的子题
    disabled_sub_challenge = SubChallenge.objects.get(challenge=challenge, enabled=False)
    assert disabled_sub_challenge.id not in ids

    # 不应出现未启用的题目
    for sub in challenge.sub_challenge.all():
        sub.enabled = False
        sub.save()
    r = client.get('/api/challenge/')
    assert r.data == []
