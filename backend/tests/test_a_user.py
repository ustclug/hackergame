"""
The "a" in the filename will make this file got tested first.
"""
from rest_framework import status

from user.models import User, Term


def test_create_term():
    User.objects.create_user(username="test_user", password="test_password")
    Term.objects.create(name='term', content='test')
    assert Term.objects.enabled_term()[0].name == 'term'


def test_register(client_without_login):
    # 测试过短的密码
    data = {
        "username": "test_user",
        "password": "123456",
    }
    r = client_without_login.post('/api/user/register/', data)
    assert "too short" in r.data['password']

    data['password'] = 'test_password'
    r = client_without_login.post('/api/user/register/', data)
    user = User.objects.all()[0]
    assert user.username == "test_user"
    assert user.token

    # 测试重复的用户名
    r = client_without_login.post('/api/user/register/', data)
    assert r.status_code == 400
    assert r.data['username'][0] == 'A user with that username already exists.'


def test_login(client_without_login):
    User.objects.create_user(username="test_user", password="test_password")
    Term.objects.create(name='term', content='test')
    data = {
        "username": "test_user",
        "password": "test_password",
    }
    r = client_without_login.post('/api/user/login/', data)
    assert r.status_code == status.HTTP_403_FORBIDDEN
    assert r.data['term'][0]['name'] == 'term'

    data['allow_terms'] = True
    r = client_without_login.post('/api/user/login/', data)
    assert r.status_code == status.HTTP_204_NO_CONTENT


def test_user_profile(client):
    r = client.get('/api/user/')
    assert r.data['username'] == 'test_user'


def test_update_user_profile(client, user):
    r = client.put('/api/user/', {'name': 'another name'})
    assert r.status_code == status.HTTP_204_NO_CONTENT
    user.refresh_from_db()
    assert user.last_name == 'another name'


def test_logout(client):
    r = client.post('/api/user/logout/')
    assert r.status_code == status.HTTP_204_NO_CONTENT
    r = client.get('/api/user/')
    assert r.status_code == status.HTTP_403_FORBIDDEN
