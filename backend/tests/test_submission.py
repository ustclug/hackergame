from datetime import timedelta

from django.contrib.auth.models import Group as AuthGroup
from rest_framework import status

from submission.models import Submission, SubChallengeFirstBlood, ChallengeFirstBlood, \
                            Scoreboard, ChallengeClear
from challenge.models import ExprFlag
from tests.utils import join_group, leave_group


def test_submission_api(challenge, sub_challenge1, sub_challenge2, expr_sub_challenge, client, user):
    data = {
        'challenge': challenge.id,
        'flag': "wrong_answer"
    }
    r = client.post('/api/submission/', data)
    assert r.data['detail'] == 'wrong'

    data['flag'] = sub_challenge1.flag
    r = client.post('/api/submission/', data)
    assert r.data['detail'] == 'correct'
    submission = Submission.objects.get(flag=sub_challenge1.flag)
    assert submission.sub_challenge_clear == sub_challenge1

    data['flag'] = sub_challenge2.flag
    client.post('/api/submission/', data)

    # 重复提交
    r = client.post('/api/submission/', data)
    assert r.data['detail'] == 'correct'

    data['flag'] = ExprFlag.objects.get(user=user, sub_challenge=expr_sub_challenge).flag
    r = client.post('/api/submission/', data)
    assert r.data['detail'] == 'correct'
    assert ChallengeClear.objects.filter(user=user, challenge=challenge).exists()

    # 重复提交
    r = client.post('/api/submission/', data)
    assert r.data['detail'] == 'correct'


def test_board(client, sub1_submission, sub2_submission, sub_challenge1, sub_challenge2, challenge, group, user):
    score = sub_challenge1.score + sub_challenge2.score
    r = client.get('/api/board/score/')
    rank = r.data['results'][0]
    assert rank['score'] == score
    for c in rank['challenge_clear']:
        if c['challenge'] == challenge.id:
            assert c['clear_status'] == 'clear'
            subs = list(map(lambda a: a['sub_challenge'], c['sub_challenge_clear']))
            assert sub_challenge1.id in subs
            assert sub_challenge2.id in subs

    r = client.get(f'/api/board/score/?category={challenge.category}')
    assert r.data['results'][0]['score'] == score

    r = client.get(f'/api/board/score/?group={group.id}')
    assert r.data['results'][0]['score'] == score

    r = client.get('/api/board/firstblood/')
    assert r.data['sub_challenges'][0]['user'] == user.id
    assert r.data['challenges'][0]['user'] == user.id

    r = client.get(f'/api/board/firstblood/?group={group.id}')
    assert r.data['sub_challenges'][0]['user'] == user.id


def test_board_permission(sub1_submission, challenge, client_another_user, group):
    """不属于该组的用户无法访问该组的排行榜"""
    r = client_another_user.get(f'/api/board/score/?group={group.id}')
    assert r.status_code == 403


def test_group_change_will_update_board(user, another_user, challenge, sub_challenge1,
                                        client, client_another_user, sub1_submission, group):
    submission2 = Submission.objects.create(user=another_user, challenge=challenge,
                                            flag=sub_challenge1.flag)
    # submission2 的提交时间比 sub1_submission 要早
    Submission.objects.filter(id=submission2.id) \
                      .update(created_time=sub1_submission.created_time - timedelta(minutes=1))

    # 加入组后排行榜上有该用户
    join_group(another_user, group)
    r = client.get(f'/api/board/score/?group={group.id}')
    assert another_user.id in map(lambda a: a['user'], r.data['results'])
    r = client.get(f'/api/board/firstblood/?group={group.id}')
    assert r.data['sub_challenges'][0]['user'] == another_user.id

    # 退出组后排行榜上无该用户
    leave_group(another_user, group)
    r = client.get(f'/api/board/score/?group={group.id}')
    assert another_user.id not in map(lambda a: a['user'], r.data['results'])
    r = client.get(f'/api/board/firstblood/?group={group.id}')
    assert r.data['sub_challenges'][0]['user'] == user.id

    # 该题被禁用后排行榜上无此题
    sub_challenge1.enabled = False
    sub_challenge1.save()

    join_group(another_user, group)
    assert not SubChallengeFirstBlood.objects.filter(group=group).exists()
    leave_group(another_user, group)
    assert not SubChallengeFirstBlood.objects.filter(group=group).exists()


def test_challenge_progress_api(sub_challenge1, sub1_submission, client):
    r = client.get('/api/challenge/clear/')
    assert r.data[0]['clear_status'] == 'partly'
    data = {
        "sub_challenge": sub_challenge1.id,
        "time": sub1_submission.created_time,
    }
    assert data in r.data[0]['sub_challenge_clear']


def test_no_board_group_does_not_participate_board(sub1_submission, user):
    no_score = AuthGroup.objects.get(name='no_score')
    user.groups.add(no_score)

    Submission.objects.regen_board()

    assert len(Scoreboard.objects.all()) == 0
    assert len(SubChallengeFirstBlood.objects.all()) == 0
    assert len(ChallengeFirstBlood.objects.all()) == 0


def test_submission_throttling(challenge, client):
    data = {
        'challenge': challenge.id,
        'flag': "wrong_answer"
    }
    for i in range(15):
        client.post('/api/submission/', data)
    r = client.post('/api/submission/', data)
    assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS


def test_score_history(user, sub1_submission, sub2_submission, client):
    r = client.get(f'/api/board/history/{user.id}/')
    assert len(r.data) == 2
    assert r.data[-1]['score'] == Scoreboard.objects.get(user=user, category='').score
