python3 -m pip install -U pip
python3 -m pip install virtualenv

cat supervisord.pid | xargs kill
git clean -dfX
# 不用 pull 因为在 push --force 的情况下会使提交树和远程不一致
git fetch --all
git reset --hard origin/refactor
virtualenv backend/.env
. backend/.env/bin/activate
python3 -m pip install -r backend/requirements.txt
python3 backend/manage.py init_dev
python3 -m pip install supervisor
supervisord -c deploy/supervisor.conf
