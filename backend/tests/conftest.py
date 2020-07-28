from datetime import datetime, timedelta

import pytz
import pytest
from rest_framework.test import APIClient

from user.models import User, Term
from contest.models import Stage


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
