from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, \
                                    ListModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.models import User
from user.serializer import PublicProfileSerializer
from group.models import Group, Application
from group.serializer import GroupSerializer, GroupApplicationSerializer, \
                                GroupApplicationUpdateSerializer, ProfileSerializer
from group.permissions import IsGroupAdminOrReadOnly, IsGroupAdmin


class GroupAPI(viewsets.ModelViewSet):
    # TODO: 分页
    # TODO: Verified Group
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsGroupAdminOrReadOnly]

    def perform_create(self, serializer):
        user = serializer.context['request'].user
        serializer.validated_data['admin'] = user
        serializer.validated_data['users'] = [user]
        serializer.save()
        # TODO 添加管理员


class GroupApplicationAPI(generics.GenericAPIView, ListModelMixin,
                          CreateModelMixin, UpdateModelMixin):
    serializer_class = GroupApplicationSerializer
    permission_classes = [IsAuthenticated, IsGroupAdmin]
    lookup_url_kwarg = 'application_id'

    def get_group(self):
        group_id = self.kwargs['group_id']
        return get_object_or_404(Group, id=group_id)

    def get_queryset(self):
        return Application.objects.filter(group=self.get_group(), status='pending')

    def get(self, request, *args, **kwargs):
        response = self.list(request, *args, **kwargs)
        self.check_object_permissions(request, self.get_group())
        return response

    def post(self, request, group_id, **kwargs):
        # TODO: 根据rules字段validate
        request.data['group'] = group_id
        request.data['user'] = request.user.pk
        return self.create(request)

    def perform_create(self, serializer):
        group = serializer.validated_data['group']
        if not group.rule_must_be_verified_by_admin:
            serializer.validated_data['status'] = 'accepted'
        serializer.save()

    def put(self, request, group_id, application_id):
        application = self.get_object()
        serializer = GroupApplicationUpdateSerializer(application, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class GroupMemberAPI(generics.GenericAPIView):
    queryset = Group.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsGroupAdmin]
    lookup_url_kwarg = 'group_id'

    def get(self, request, group_id):
        group = self.get_object()
        queryset = Application.objects.filter(status='accepted', group=group)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def delete(self, request, group_id, user_id):
        group = self.get_object()
        application = get_object_or_404(Application, group=group, user__id=user_id)
        application.status = 'deleted'
        application.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
