import pytest
from rest_framework.test import APIClient

from user.models import User, Term


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture(scope='function')
def client_without_login():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(username="test_user", password="test_password")


@pytest.fixture
def another_user():
    return User.objects.create_user(username="test_user2", password="test_password")


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
