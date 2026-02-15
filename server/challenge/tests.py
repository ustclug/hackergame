from django.test import TestCase

from ..context import Context
from .interface import Challenge as ChallengeInterface
from .models import Challenge as ChallengeModel
from .expr_flags import expr_flag


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


class TestExprFlags(TestCase):
    def setUp(self) -> None:
        # a nonsense token
        self.token = "ea7cc653e0838e229a31a10f98f3191daacb8e251c4b06827786e2b69ef6695b50786731c04e159f6b4e6a790a99f0d1ac5dc8099fefcbe50411953afc35920831"
        return super().setUp()

    def test_expr(self):
        res = expr_flag("'flag{' + md5('secret' + token)[:16] + '}'", self.token)
        self.assertEqual(res, "flag{6f6814f00964b0ab}")
        res = expr_flag("'flag{' + str(int(md5('secret' + token), 16) % 10001) + '}'", self.token)
        self.assertEqual(res, "flag{7148}")
