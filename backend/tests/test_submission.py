import pytest

from tests.test_challenge import challenge
from tests.test_group import group, accepted_application, application
from submission.models import Submission, Scoreboard, SubChallengeFirstBlood, ChallengeFirstBlood
from challenge.models import ExprFlag


def test_submission_api(challenge, client, user):
    challenge, sub1, sub2 = challenge
    data = {
        'challenge': challenge.id,
        'flag': "wrong_answer"
    }
    r = client.post('/api/submission/', data)
    assert r.data['detail'] == 'wrong'

    data['flag'] = sub2.flag
    r = client.post('/api/submission/', data)
    assert r.data['detail'] == 'correct'
    submission = Submission.objects.get(flag=sub2.flag)
    assert submission.sub_challenge_clear == sub2

    data['flag'] = ExprFlag.objects.get(user=user, sub_challenge=sub1).flag
    r = client.post('/api/submission/', data)
    assert r.data['detail'] == 'correct'
    submission = Submission.objects.get(flag=data['flag'])
    assert submission.challenge_clear is True


@pytest.fixture
def submission(challenge, user):
    challenge, sub1, sub2 = challenge
    submission = Submission.objects.create(user=user, challenge=challenge, flag=sub2.flag)
    return submission


def test_board(client, submission, challenge, group):
    challenge, sub1, sub2 = challenge
    r = client.get('/api/board/score/')
    assert r.data[0]['score'] == sub2.score

    r = client.get(f'/api/board/score/?category={challenge.category}')
    assert r.data[0]['score'] == sub2.score

    r = client.get(f'/api/board/score/?group={group.id}')
    assert r.data[0]['score'] == sub2.score

    r = client.get('/api/board/firstblood/')
    assert r.data['sub_challenges'][0]['user'] == submission.user.id

    r = client.get(f'/api/board/firstblood/?group={group.id}')
    assert r.data['sub_challenges'][0]['user'] == submission.user.id


def test_board_permission(submission, challenge, client_another_user, group):
    r = client_another_user.get(f'/api/board/score/?group={group.id}')
    assert r.status_code == 403
