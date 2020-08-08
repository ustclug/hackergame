from challenge.models import ExprFlag
from challenge.utils import functions, eval_token_expression


def test_enabled(challenge, text_sub_challenge, expr_sub_challenge):
    text_sub_challenge.enabled = False
    text_sub_challenge.save()
    assert challenge.enabled is True
    expr_sub_challenge.enabled = False
    expr_sub_challenge.save()
    assert challenge.enabled is False


def test_expr_flag(expr_sub_challenge, user):
    flag = f'flag{{{functions["md5"]("secret"+user.token)}}}'
    assert flag == ExprFlag.objects.get(user=user, sub_challenge=expr_sub_challenge).flag


def test_check_correctness(user, text_sub_challenge, expr_sub_challenge):
    flag = eval_token_expression(expr_sub_challenge.flag, user.token)
    assert expr_sub_challenge.check_correctness(flag, user) is True
    assert text_sub_challenge.check_correctness(text_sub_challenge.flag, user) is True
    assert text_sub_challenge.check_correctness("wrong_answer", user) is False


def test_check_violation(expr_sub_challenge, user, another_user):
    user1_flag = eval_token_expression(expr_sub_challenge.flag, user.token)
    user2_flag = eval_token_expression(expr_sub_challenge.flag, another_user.token)
    assert expr_sub_challenge.check_violation(user1_flag, user) is None
    assert expr_sub_challenge.check_violation(user2_flag, user) == another_user


def test_challenge_api(challenge, expr_sub_challenge, text_sub_challenge, client):
    text_sub_challenge.enabled = False
    text_sub_challenge.save()

    r = client.get('/api/challenge/')
    assert r.data[0]['id'] == challenge.id

    ids = list(map(lambda a: a['id'], r.data[0]['sub_challenge']))
    assert expr_sub_challenge.id in ids
    assert text_sub_challenge.id not in ids

    # 不应出现未启用的题目
    expr_sub_challenge.enabled = False
    expr_sub_challenge.save()

    r = client.get('/api/challenge/')
    assert r.data == []


def test_challenge_status_change_will_update_first_blood(client, user, challenge,
                                                         expr_sub_challenge, submission):
    expr_sub_challenge.enabled = False
    expr_sub_challenge.save()

    r = client.get('/api/board/firstblood/')
    assert r.data['challenges'][0]['user'] == user.id


def test_challenge_status_change_will_update_scoreboard(client, submission, expr_submission,
                                                        expr_sub_challenge, text_sub_challenge):
    expr_sub_challenge.enabled = False
    expr_sub_challenge.save()

    r = client.get('/api/board/score/')
    assert r.data[0]['score'] == text_sub_challenge.score
