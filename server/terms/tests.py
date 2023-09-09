from django.test import TestCase

from ..context import Context
from .interface import Terms as TermsInterface
from .models import Terms as TermsModel


class CheckInterfaceFields(TestCase):
    def setUp(self) -> None:
        self.context = Context()
        self.terms = TermsInterface(self.context, TermsModel())
        return super().setUp()

    def test_fields(self):
        for i in self.terms.json_fields:
            self.assertIn(i, dir(self.terms))
        for i in self.terms.update_fields:
            self.assertIn(i, dir(self.terms))
