from rest_framework import status

from user.models import User, Term


def test_create_term():
    User.objects.create_user(username="test_user", password="test_password")
    Term.objects.create(name='term', content='test')
    assert Term.objects.enabled_term().name == 'term'


def test_register(client_without_login):
    client_without_login.post('/api/user/register/', {
        "username": "test_user",
        "password": "test_password",
        "password_confirm": "test_password"
    })
    user = User.objects.all()[0]
    assert user.username == "test_user"
    assert user.token is not None


def test_login(client_without_login):
    User.objects.create_user(username="test_user", password="test_password")
    Term.objects.create(name='term', content='test')
    data = {
        "username": "test_user",
        "password": "test_password",
    }
    r = client_without_login.post('/api/user/login/', data)
    assert r.status_code == status.HTTP_403_FORBIDDEN
    assert r.data['term']['name'] == 'term'

    data['allow_terms'] = True
    r = client_without_login.post('/api/user/login/', data)
    assert r.status_code == status.HTTP_204_NO_CONTENT


def test_user_profile(client):
    r = client.get('/api/user/')
    assert r.data['username'] == 'test_user'


def test_logout(client):
    r = client.post('/api/user/logout/')
    assert r.status_code == status.HTTP_204_NO_CONTENT
    r = client.get('/api/user/')
    assert r.status_code == status.HTTP_403_FORBIDDEN
