from rest_framework import viewsets, generics
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated

from user.models import User
from group.models import Group, Application
from group.serializer import GroupSerializer, GroupApplicationSerializer


class GroupAPI(viewsets.ModelViewSet):
    # TODO: 分页
    # TODO: Verified Group
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]


class GroupApplicationAPI(generics.GenericAPIView, CreateModelMixin, UpdateModelMixin):
    queryset = Application.objects.all()
    serializer_class = GroupApplicationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data['user'] = request.user.pk
        return self.create(request)

    def perform_create(self, serializer):
        group = Group.objects.get(serializer.data['group'])
        if not group.rule_must_be_verified_by_admin:
            user = User.objects.get(serializer.data['user'])
            group.users.add(user)
            serializer.data['status'] = 'accepted'
        serializer.save()

    def put(self, request):
        self.partial_update(request)

    def perform_update(self, serializer):
        group = Group.objects.get(serializer.data['group'])
        user = User.objects.get(serializer.data['user'])
        group.users.add(user)
        serializer.save()
