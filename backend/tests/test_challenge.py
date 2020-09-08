from challenge.models import ExprFlag
from challenge.utils import functions, eval_token_expression
from submission.models import ChallengeClear


def test_enabled(challenge, sub_challenge1, sub_challenge2):
    sub_challenge1.enabled = False
    sub_challenge1.save()
    assert challenge.enabled is True
    sub_challenge2.enabled = False
    sub_challenge2.save()
    assert challenge.enabled is False


def test_expr_flag(expr_sub_challenge, user):
    flag = f'flag{{{functions["md5"]("secret"+user.token)}}}'
    assert flag == ExprFlag.objects.get(user=user, sub_challenge=expr_sub_challenge).flag


def test_flag_update_will_update_expr_flag_table(expr_sub_challenge, user):
    expr_sub_challenge.flag = '"flag{" + token + "}"'
    expr_sub_challenge.save()

    assert ExprFlag.objects.get(user=user, sub_challenge=expr_sub_challenge).flag == f'flag{{{user.token}}}'


def test_check_correctness(user, sub_challenge1, expr_sub_challenge):
    flag = eval_token_expression(expr_sub_challenge.flag, user.token)
    assert expr_sub_challenge.check_correctness(flag, user) is True
    assert sub_challenge1.check_correctness(sub_challenge1.flag, user) is True
    assert sub_challenge1.check_correctness("wrong_answer", user) is False


def test_check_violation(expr_sub_challenge, user, another_user):
    user1_flag = eval_token_expression(expr_sub_challenge.flag, user.token)
    user2_flag = eval_token_expression(expr_sub_challenge.flag, another_user.token)
    assert expr_sub_challenge.check_violation(user1_flag, user) is None
    assert expr_sub_challenge.check_violation(user2_flag, user) == another_user


def test_challenge_api(challenge, sub_challenge1, sub_challenge2, client):
    sub_challenge1.enabled = False
    sub_challenge1.save()

    r = client.get('/api/challenge/')
    assert r.data[0]['id'] == challenge.id

    # 不应出现未启用的子题
    ids = list(map(lambda a: a['id'], r.data[0]['sub_challenge']))
    assert sub_challenge2.id in ids
    assert sub_challenge1.id not in ids

    # 不应出现未启用的题目
    sub_challenge2.enabled = False
    sub_challenge2.save()

    r = client.get('/api/challenge/')
    assert r.data == []


def test_challenge_status_change_will_update_board(client, user, challenge,
                                                   sub_challenge2, sub1_submission):
    sub_challenge2.enabled = False
    sub_challenge2.save()

    r = client.get('/api/board/firstblood/')
    assert r.data['challenges'][0]['user'] == user.id  # 只通过了第一子题的用户通过整个题目


def test_challenge_status_change_will_update_scoreboard(client, sub1_submission, sub2_submission,
                                                        sub_challenge1, sub_challenge2):
    """通过两个子题的用户只有已启用子题的分数"""
    sub_challenge1.enabled = False
    sub_challenge1.save()

    r = client.get('/api/board/score/')
    assert r.data['results'][0]['score'] == sub_challenge2.score


def test_sub_challenge_status_change_will_update_challenge_clear(
        challenge, sub1_submission, expr_submission, user, sub_challenge2
):
    assert ChallengeClear.objects.filter(challenge=challenge, user=user).exists() is False
    sub_challenge2.enabled = False
    sub_challenge2.save()
    assert ChallengeClear.objects.filter(challenge=challenge, user=user).exists() is True
