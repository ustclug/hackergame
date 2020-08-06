from datetime import timedelta

from submission.models import Submission
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

    data['flag'] = ExprFlag.objects.get(user=user, sub_challenge=expr_sub_challenge).flag
    r = client.post('/api/submission/', data)
    assert r.data['detail'] == 'correct'
    submission = Submission.objects.get(flag=data['flag'])
    assert submission.challenge_clear is True


def test_board(client, submission, text_sub_challenge, challenge, group):
    r = client.get('/api/board/score/')
    assert r.data[0]['score'] == text_sub_challenge.score

    r = client.get(f'/api/board/score/?category={challenge.category}')
    assert r.data[0]['score'] == text_sub_challenge.score

    r = client.get(f'/api/board/score/?group={group.id}')
    assert r.data[0]['score'] == text_sub_challenge.score

    r = client.get('/api/board/firstblood/')
    assert r.data['sub_challenges'][0]['user'] == submission.user.id

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
