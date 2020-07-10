import pytest
from rest_framework.test import APIClient

from user.models import User, Term


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture(scope='function')
def client_without_login():
    return APIClient()


@pytest.fixture(scope='function')
def client():
    User.objects.create_user(username="test_user", password="test_password")
    Term.objects.create(name='term', content='test')
    c = APIClient()
    c.login(username="test_user", password="test_password")
    return c
