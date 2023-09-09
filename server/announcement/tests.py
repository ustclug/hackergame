from django.test import TestCase

from ..context import Context
from .interface import Announcement as AnnouncementInterface
from .models import Announcement as AnnouncementModel


class CheckInterfaceFields(TestCase):
    def setUp(self) -> None:
        self.context = Context()
        self.announcement = AnnouncementInterface(self.context, AnnouncementModel())
        return super().setUp()

    def test_fields(self):
        for i in self.announcement.json_fields:
            self.assertIn(i, dir(self.announcement))
        for i in self.announcement.update_fields:
            self.assertIn(i, dir(self.announcement))
