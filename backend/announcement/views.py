from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView

from announcement.models import Announcement
from announcement.serializer import AnnouncementSerializer
from challenge.models import Challenge


class AnnouncementAPI(ListAPIView):
    serializer_class = AnnouncementSerializer

    def get_queryset(self):
        challenge_id = self.request.query_params.get('challenge')
        if challenge_id:
            challenge = get_object_or_404(Challenge, pk=challenge_id)
            return Announcement.objects.filter(challenge=challenge)
        else:
            return Announcement.objects.all()
