from django.test import TestCase

from ..context import Context
from .interface import Trigger as TriggerInterface
from .models import Trigger as TriggerModel


class CheckInterfaceFields(TestCase):
    def setUp(self) -> None:
        self.context = Context()
        self.trigger = TriggerInterface(self.context, TriggerModel())
        return super().setUp()

    def test_fields(self):
        for i in self.trigger.json_fields:
            self.assertIn(i, dir(self.trigger))
        for i in self.trigger.update_fields:
            self.assertIn(i, dir(self.trigger))
