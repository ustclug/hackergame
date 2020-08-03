from tests.test_challenge import challenge
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
    # TODO: 测试一血榜
