from datetime import timedelta

from django.contrib.auth.models import Group as AuthGroup

from submission.models import Submission, SubChallengeFirstBlood, ChallengeFirstBlood, \
                            Scoreboard
from challenge.models import ExprFlag


def test_submission_api(challenge, text_sub_challenge, expr_sub_challenge, client, user):
    data = {
        'challenge': challenge.id,
        'flag': "wrong_answer"
    }
    r = client.post('/api/submission/', data)
    assert r.data['detail'] == 'wrong'

    data['flag'] = text_sub_challenge.flag
    r = client.post('/api/submission/', data)
    assert r.data['detail'] == 'correct'
    submission = Submission.objects.get(flag=text_sub_challenge.flag)
    assert submission.sub_challenge_clear == text_sub_challenge

    # 重复提交
    r = client.post('/api/submission/', data)
    assert r.data['detail'] == 'correct'

    data['flag'] = ExprFlag.objects.get(user=user, sub_challenge=expr_sub_challenge).flag
    r = client.post('/api/submission/', data)
    assert r.data['detail'] == 'correct'
    submission = Submission.objects.get(flag=data['flag'])
    assert submission.challenge_clear is True

    # 重复提交
    r = client.post('/api/submission/', data)
    assert r.data['detail'] == 'correct'


def test_board(client, submission, expr_submission, text_sub_challenge, expr_sub_challenge, challenge, group):
    score = text_sub_challenge.score + expr_sub_challenge.score
    r = client.get('/api/board/score/')
    assert r.data[0]['score'] == score

    r = client.get(f'/api/board/score/?category={challenge.category}')
    assert r.data[0]['score'] == score

    r = client.get(f'/api/board/score/?group={group.id}')
    assert r.data[0]['score'] == score

    r = client.get('/api/board/firstblood/')
    assert r.data['sub_challenges'][0]['user'] == submission.user.id
    assert r.data['challenges'][0]['user'] == submission.user.id

    r = client.get(f'/api/board/firstblood/?group={group.id}')
    assert r.data['sub_challenges'][0]['user'] == submission.user.id


def test_board_permission(submission, challenge, client_another_user, group):
    r = client_another_user.get(f'/api/board/score/?group={group.id}')
    assert r.status_code == 403


def test_group_change_will_update_board(user, another_user, challenge, application, text_sub_challenge,
                                        client, client_another_user, submission, group):
    submission2 = Submission.objects.create(user=another_user, challenge=challenge,
                                            flag=text_sub_challenge.flag)
    # submission2 的提交时间比 submission 要早
    Submission.objects.filter(id=submission2.id) \
                      .update(created_time=submission.created_time - timedelta(minutes=1))

    # 加入组
    client.put(f'/api/group/{group.id}/application/{application.id}/', {
        'status': 'accepted'
    })
    r = client.get(f'/api/board/score/?group={group.id}')
    assert another_user.id in map(lambda a: a['user'], r.data)
    r = client.get(f'/api/board/firstblood/?group={group.id}')
    assert r.data['sub_challenges'][0]['user'] == another_user.id

    # 退出组
    client.delete(f'/api/group/{group.id}/member/{another_user.id}/')
    r = client.get(f'/api/board/score/?group={group.id}')
    assert another_user.id not in map(lambda a: a['user'], r.data)
    r = client.get(f'/api/board/firstblood/?group={group.id}')
    assert r.data['sub_challenges'][0]['user'] == user.id


def test_challenge_progress_api(text_sub_challenge, submission, client):
    r = client.get('/api/challenge/clear/')
    assert r.data[0]['clear'] is False
    data = {
        "sub_challenge": text_sub_challenge.id,
        "clear": True,
    }
    assert data in r.data[0]['sub_challenges']


def test_no_board_group_does_not_participate_board(submission, user):
    no_score = AuthGroup.objects.get(name='no_score')
    user.groups.add(no_score)

    Submission.regen_board()

    assert len(Scoreboard.objects.all()) == 0
    assert len(SubChallengeFirstBlood.objects.all()) == 0
    assert len(ChallengeFirstBlood.objects.all()) == 0
