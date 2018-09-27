from random import randrange, shuffle


def main():
    with open('load_test_data.py', 'w') as f:
        f.write('from datetime import datetime\n')
        f.write('from ctf.models import Problem, Flag, User, Solve\n')
        flag_pk = 0
        for i in range(1, 21):
            f.write(f'Problem(pk="p{i}", is_open=True, name="P{i}", detail="p{i}").save()\n')
            for j in range(1, 6 if i < 15 else 2):
                flag_pk += 1
                f.write(f'Flag(problem_id="p{i}", name="P{i}F{j}", flag="flag{{p{i}f{j}}}", score={randrange(1, 100)}).save()\n')
        flags = list(range(1, flag_pk + 1))
        for i in range(1, 10001):
            f.write(f'User.objects.create_user(username="u{i}", last_name="g{randrange(1, 6)}", password="******")\n')
            shuffle(flags)
            for j in flags[:randrange(len(flags))]:
                f.write(f'Solve(user_id={i}, flag_id={j}, time=datetime(2018, 9, 26, {randrange(24)}, {randrange(60)}, {randrange(60)})).save()\n')


if __name__ == '__main__':
    main()
