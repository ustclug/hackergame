from datetime import datetime, timedelta

import pytz
import pytest
from rest_framework.test import APIClient

from user.models import User, Term
from group.models import Group, Application
from contest.models import Stage
from challenge.models import Challenge, SubChallenge
from submission.models import Submission


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture(scope='function')
def client_without_login():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(username="test_user", password="test_password",
                                    last_name='test_name')


@pytest.fixture
def another_user():
    return User.objects.create_user(username="test_user2", password="test_password",
                                    email='a@xx.edu.cn')


@pytest.fixture
def term():
    return Term.objects.create(name='term', content='test')


@pytest.fixture
def client(user, term):
    c = APIClient()
    c.login(username="test_user", password="test_password")
    return c


@pytest.fixture
def client_another_user(user, term, another_user):
    c = APIClient()
    c.login(username="test_user2", password="test_password")
    return c


def stage():
    start_time = datetime(2020, 7, 24, 22, 47, 0, tzinfo=pytz.utc)
    end_time = start_time + timedelta(weeks=52*100)  # 使得用到 Stage 的测试状态永远处于 underway
    practice_start_time = end_time + timedelta(days=2)
    return Stage.objects.create(start_time=start_time, end_time=end_time,
                                practice_start_time=practice_start_time)


@pytest.fixture(name="stage")
def stage_fixture():
    return stage()


@pytest.fixture
def group(user):
    group = Group.objects.create(
        name='某大学',
        admin=user,
        rule_has_phone_number=False,
        rule_has_email=True,
        rule_email_suffix='xx.edu.cn',
        rule_has_name=False,
        rule_must_be_verified_by_admin=True,
        apply_hint='Please apply.',
        verified=True,
        verify_message='This group has been verified.'
    )
    return group


@pytest.fixture
def application(group, another_user):
    return Application.objects.create(user=another_user, group=group, apply_message='xxx')


@pytest.fixture
def challenge(stage):
    challenge = Challenge.objects.create(
        index=1,
        name='test_challenge',
        category='test',
        detail='test_detail',
        prompt='test_prompt'
    )
    SubChallenge.objects.create(
        challenge=challenge,
        name='expr',
        score=50,
        enabled=True,
        flag_type='expr',
        flag='"flag{"+md5("secret"+token)+"}"'
    )
    SubChallenge.objects.create(
        challenge=challenge,
        name='text',
        score=100,
        enabled=True,
        flag_type='text',
        flag='flag{abc}'
    )
    return challenge


@pytest.fixture
def expr_sub_challenge(challenge):
    return SubChallenge.objects.get(name='expr')


@pytest.fixture
def text_sub_challenge(challenge):
    return SubChallenge.objects.get(name='text')


@pytest.fixture
def submission(challenge, text_sub_challenge, user):
    submission = Submission.objects.create(user=user, challenge=challenge, flag=text_sub_challenge.flag)
    return submission
