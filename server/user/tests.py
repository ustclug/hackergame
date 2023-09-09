from django.test import TestCase

from ..context import Context
from .interface import User as UserInterface
from .models import User as UserModel


class CheckInterfaceFields(TestCase):
    def setUp(self) -> None:
        self.context = Context()
        self.user = UserInterface(self.context, UserModel())
        return super().setUp()

    def test_fields(self):
        for i in self.user.json_fields:
            self.assertIn(i, dir(self.user))
        for i in self.user.update_fields:
            self.assertIn(i, dir(self.user))
