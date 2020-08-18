from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from group.models import Group, Application
from group.serializer import GroupSerializer, GroupApplicationSerializer, \
    GroupApplicationUpdateSerializer, ProfileSerializer
from group.permissions import IsGroupAdminOrReadOnly, IsGroupAdmin


def generate_rules_meet(rules, user):
    rules_meet = {
        "has_phone_number": user.phone_number != "" if rules['has_phone_number'] else True,
        "has_email": user.email != "" if rules['has_email'] else True,
        "has_name": user.last_name != "" if rules['has_name'] else True,
        "email_suffix": user.email.endswith(rules['email_suffix'])
        if rules['email_suffix'] != "" else True
    }
    return rules_meet


class GroupAPI(ModelViewSet):
    # TODO: 分页
    # TODO: Verified Group
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = ModelViewSet.permission_classes + [IsGroupAdminOrReadOnly]

    def perform_create(self, serializer):
        user = serializer.context['request'].user
        serializer.validated_data['admin'] = user
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        rtn = serializer.data
        rtn['rules_meet'] = generate_rules_meet(serializer.data['rules'], request.user)
        return Response(rtn)


class GroupApplicationAPI(GenericAPIView, ListModelMixin, CreateModelMixin):
    serializer_class = GroupApplicationSerializer
    permission_classes = GenericAPIView.permission_classes + [IsGroupAdmin]
    lookup_url_kwarg = 'application_id'

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.request.method == 'PUT':
            serializer_class = GroupApplicationUpdateSerializer

        return serializer_class

    def get_group(self):
        group_id = self.kwargs['group_id']
        return get_object_or_404(Group, id=group_id)

    def get_queryset(self):
        self.check_object_permissions(self.request, self.get_group())
        return Application.objects.filter(group=self.get_group(), status='pending')

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, group_id, **kwargs):
        # 根据rules字段validate
        group = get_object_or_404(Group, id=group_id)
        serializer = GroupSerializer(group)
        rules_meet = generate_rules_meet(serializer.data['rules'], request.user)
        for rule in rules_meet.values():
            if not rule:
                raise ValidationError('不符合加入条件')

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
        if serializer.validated_data['status'] == 'rejected':
            application.delete()
        else:
            application.status = 'accepted'
            application.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupMemberAPI(GenericAPIView):
    queryset = Group.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = GenericAPIView.permission_classes + [IsGroupAdmin]
    lookup_url_kwarg = 'group_id'

    def get(self, request, group_id):
        group = self.get_object()
        queryset = Application.objects.filter(status='accepted', group=group)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def delete(self, request, group_id, user_id):
        group = self.get_object()
        application = get_object_or_404(Application, group=group, user__id=user_id, status='accepted')
        application.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
