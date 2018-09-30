from datetime import datetime
from random import randrange, shuffle

from ctf.models import Problem, Flag, User, Solve

flag_pk = 0
for i in range(1, 21):
    Problem(pk=f"p{i}", is_open=True, name=f"P{i}", detail=f"p{i}").save()
    for j in range(1, 6 if i < 15 else 2):
        flag_pk += 1
        Flag(problem_id=f"p{i}", name=f"P{i}F{j}", flag=f"flag{{p{i}f{j}}}", score=randrange(1, 100)).save()
flags = list(range(1, flag_pk + 1))
for i in range(1, 10001):
    User.objects.create_user(username=f"u{i}", last_name=f"g{randrange(1, 6)}", password="******")
    shuffle(flags)
    for j in flags[:randrange(len(flags))]:
        Solve(user_id=i, flag_id=j, time=datetime(2018, 9, 26, randrange(24), randrange(60), randrange(60))).save()
