from django.test import TestCase

from ..context import Context
from .interface import Challenge as ChallengeInterface
from .models import Challenge as ChallengeModel


class CheckInterfaceFields(TestCase):
    def setUp(self) -> None:
        self.context = Context()
        self.challenge = ChallengeInterface(self.context, ChallengeModel())
        return super().setUp()

    def test_fields(self):
        for i in self.challenge.json_fields:
            self.assertIn(i, dir(self.challenge))
        for i in self.challenge.update_fields:
            self.assertIn(i, dir(self.challenge))
