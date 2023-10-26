from django.core.management import call_command
from django.test import TestCase
import os
import shutil

from server.challenge.interface import Challenge
from server.context import Context
from server.challenge.expr_flags import expr_flag


FILE1 = """---
enabled: false
name: 示例题目 1
category: general
url: files/example.txt
prompt: flag{...}
index: 0
flags:
- name: ''
  score: 0
  type: text
  flag: flag{example}
---

一段描述。
"""

FILE2 = """---
enabled: true
name: 示例题目 2
category: math
url: files/example.txt
prompt: flag{...}
index: 1
flags:
- name: '1+1=2'
  score: 1
  type: expr
  flag: f"flag{{{1+1}=2, {token}}}"
- name: '2+2=4'
  score: 2
  type: text
  flag: flag{2+2=4}
---

一段描述 2。
"""

FILE3 = """---
enabled: true
name: 示例题目 3
category: web
url: http://example.com/?token={token}
prompt: flag{...}
index: 2
check_url_clicked: true
flags:
- name: ''
  score: 0
  type: text
  flag: flag{example3}
---

一段描述 3。

```python
print("Hello, world!")
```
"""


FILES = (FILE1, FILE2, FILE3)


class ImportDataTest(TestCase):
    def setUp(self) -> None:
        # dir: /dev/shm/hackergame-django-test
        self.DIR_NAME = "/dev/shm/hackergame-django-test"
        try:
            shutil.rmtree(self.DIR_NAME)
        except FileNotFoundError:
            pass
        os.mkdir(self.DIR_NAME)
        # create some example README.md files
        for i in range(3):
            os.mkdir(f"{self.DIR_NAME}/example{i}")
            with open(f"{self.DIR_NAME}/example{i}/README.md", "w") as f:
                f.write(FILES[i])

    def tearDown(self) -> None:
        shutil.rmtree(self.DIR_NAME)

    def test_import(self):
        call_command("import_data", self.DIR_NAME)
        # See what's inside challenges
        context = Context(elevated=True)
        challenges = {i.name: i for i in Challenge.get_all(context)}
        keys = challenges.keys()
        self.assert_("示例题目 1" not in keys)
        self.assert_("示例题目 2" in keys)
        self.assert_("示例题目 3" in keys)
        c2 = challenges["示例题目 2"]
        c3 = challenges["示例题目 3"]
        self.assert_(c2.url_orig.endswith("/example.txt"))
        self.assertEqual(c3.url_orig, "http://example.com/?token={token}")
        self.assertEqual(c2.check_url_clicked, False)
        self.assertEqual(c3.check_url_clicked, True)
        self.assert_("codehilite" in c3.detail)
        flag1 = c2.flags[0]
        self.assertEqual(flag1["type"], "expr")
        self.assertEqual("flag{2=2, 1:14}", expr_flag(flag1["flag"], "1:14"))
        flag2 = c2.flags[1]
        self.assertEqual(flag2["type"], "text")
        self.assertEqual("flag{2+2=4}", flag2["flag"])
