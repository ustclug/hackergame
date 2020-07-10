from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, \
                                    ListModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.models import User
from user.serializer import PublicProfileSerializer
from group.models import Group, Application
from group.serializer import GroupSerializer, GroupApplicationSerializer
from group.permissions import IsAdmin


class GroupAPI(viewsets.ModelViewSet):
    # TODO: 分页
    # TODO: Verified Group
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()
        # TODO 添加管理员


class GroupApplicationAPI(generics.GenericAPIView, ListModelMixin,
                          CreateModelMixin, UpdateModelMixin):
    serializer_class = GroupApplicationSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'application_id'

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return Application.objects.filter(group__id=group_id)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, group_id, **kwargs):
        request.data['group'] = group_id
        request.data['user'] = request.user.pk
        return self.create(request)

    def perform_create(self, serializer):
        group = Group.objects.get(serializer.data['group'])
        if not group.rule_must_be_verified_by_admin:
            user = User.objects.get(serializer.data['user'])
            group.users.add(user)
            serializer.data['status'] = 'accepted'
        serializer.save()

    def put(self, request, **kwargs):
        # FIXME: 只允许status字段更新
        return self.partial_update(request)

    def perform_update(self, serializer):
        group = Group.objects.get(serializer.data['group'])
        user = User.objects.get(serializer.data['user'])
        group.users.add(user)
        serializer.save()


class GroupMemberAPI(generics.GenericAPIView):
    queryset = Group.objects.all()
    serializer_class = PublicProfileSerializer
    permission_classes = [IsAdmin]
    lookup_url_kwarg = 'group_id'

    def get(self, request, group_id):
        group = self.get_object()
        serializer = self.get_serializer(group.users, many=True)
        return Response(serializer.data)

    def delete(self, request, group_id, user_id):
        group = self.get_object()
        group.users.remove(user_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
