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
        self.token = "2:BBBBBBu1qB2iBBjcpBBBwpBlBnlvryj508f3BeBs5gBaaBB5BiBBn+B4xBx/2+l+c1o81BqBcwBBBnBBpB5fBBewBBz20yw="
        return super().setUp()

    def test_expr(self):
        res = expr_flag("'flag{' + md5('secret' + token)[:16] + '}'", self.token)
        self.assertEqual(res, "flag{6a513c83d63baea4}")
        res = expr_flag("'flag{' + str(int(md5('secret' + token), 16) % 10001) + '}'", self.token)
        self.assertEqual(res, "flag{9011}")
