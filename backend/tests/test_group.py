import pytest
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from group.models import Group


class TestManagement:
    def test_create(self, client, user):
        r = client.post('/api/group/', {
            'name': "某大学",
            'rules': {
                'has_phone_number': True,
                'has_email': True,
                'email_suffix': "xx.edu.cn",
                'has_name': True,
                'must_be_verified_by_admin': True,
            },
            'apply_hint': "xxx",
        })
        assert r.status_code == status.HTTP_201_CREATED

        # 测试创建者在组内并为管理员
        group = Group.objects.all()[0]
        assert user in group.admin.all()
        assert group.users[0] == user

    def test_list(self, client, group):
        r = client.get('/api/group/')
        assert len(r.data['results']) == 1

    def test_retrieve(self, client, group):
        r = client.get(f'/api/group/{group.id}/')
        assert r.data['id'] == group.id
        assert r.data['rules_meet']

    def test_update(self, client, group):
        r = client.patch(f'/api/group/{group.id}/', {'rules': {'has_name': False}})
        assert r.data['rules']['has_name'] is False
        group.refresh_from_db()
        assert group.rule_has_name is False

    def test_delete(self, client, group):
        r = client.delete(f'/api/group/{group.id}/')
        assert r.status_code == status.HTTP_204_NO_CONTENT
        with pytest.raises(ObjectDoesNotExist):
            group.refresh_from_db()

    def test_permission(self, group, client_another_user):
        r = client_another_user.delete(f'/api/group/{group.id}/')
        assert r.status_code == status.HTTP_403_FORBIDDEN


class TestApplication:
    def test_apply(self, client_another_user, group):
        data = {'apply_message': "xxx"}
        r = client_another_user.post(f'/api/group/{group.id}/application/', data)
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data['status'] == 'pending'

        # 申请一个不存在的组
        r = client_another_user.post('/api/group/100/application/', data)
        assert r.status_code == status.HTTP_404_NOT_FOUND

        # 重复申请
        r = client_another_user.post(f'/api/group/{group.id}/application/', data)
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_list(self, client, application, group):
        r = client.get(f'/api/group/{group.id}/application/')
        assert r.data['results'][0]['apply_message'] == 'xxx'

        # 查看一个不存在的组
        r = client.get('/api/group/100/application/')
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_accept_update(self, client, application, group, another_user):
        client.put(f'/api/group/{group.id}/application/{application.id}/', {
            'status': 'accepted'
        })
        application.refresh_from_db()
        assert application.status == 'accepted'
        assert another_user in group.users

    def test_reject_update(self, client, application, group, another_user):
        client.put(f'/api/group/{group.id}/application/{application.id}/', {
            'status': 'rejected'
        })
        assert another_user not in group.users

    def test_permission(self, client_another_user, application, group):
        r = client_another_user.get(f'/api/group/{group.id}/application/')
        assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.fixture
def accepted_application(client, application, group):
    client.put(f'/api/group/{group.id}/application/{application.id}/', {
        'status': 'accepted'
    })
    application.refresh_from_db()
    return application


class TestMember:
    def test_view(self, client, accepted_application, group):
        r = client.get(f'/api/group/{group.id}/member/')
        assert r.data[0]['apply_message'] is not None
        assert r.data[0]['user'] is not None

    def test_delete(self, client, accepted_application, another_user, group):
        r = client.delete(f'/api/group/{group.id}/member/{another_user.id}/')
        assert r.status_code == status.HTTP_204_NO_CONTENT
        assert another_user not in group.users

    def test_permission(self, client_another_user, accepted_application, group):
        r = client_another_user.get(f'/api/group/{group.id}/member/')
        assert r.status_code == status.HTTP_403_FORBIDDEN
