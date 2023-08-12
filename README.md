# Hackergame 比赛平台

## 开发环境部署

1. 创建 venv：`python3 -m venv .venv`。
1. 进入 venv：`. .venv/bin/activate`。
1. 安装依赖：`pip install --upgrade pip`，`pip install -r requirements.txt`。
1. 密钥配置：`cp conf/local_settings.py.example conf/local_settings.py`，编辑 `conf/local_settings.py`，其中有两条命令，需要执行并把输出贴在相应位置。
1. 设置环境变量：`export DJANGO_SETTINGS_MODULE=conf.settings.dev`。
1. 创建数据目录：`mkdir var`。
1. 数据库初始化：`./manage.py migrate`。
1. （可选）Google 与 Microsoft app secret 写入数据库：`./manage.py setup`。
1. 见下方“运行”一节。
1. 退出 venv：`deactivate`。

## 生产环境部署

生产环境中会额外用到：Nginx、uWSGI、PostgreSQL、Memcached、PgBouncer。以下流程在 Debian 12 测试过。

1. 安装依赖：`apt install python3-dev build-essential python3-venv nginx postgresql memcached pgbouncer`。
1. （建议）本地连接 PostgreSQL 无需鉴权：修改 `/etc/postgresql/15/main/pg_hba.conf`，将 `local all all peer` 一行改为 `local all all trust`，然后执行 `systemctl reload postgresql`。
1. 创建数据库：`su postgres`，`psql`，`create user hackergame; create database hackergame;`, `\c hackergame`, `grant create on schema public to hackergame;`。
1. 克隆代码：`cd /opt`，`git clone https://github.com/ustclug/hackergame.git`。
1. Media 目录：`mkdir -p /var/opt/hackergame/media`，`chown www-data: /var/opt/hackergame/media`。
1. 创建 venv：`cd /opt/hackergame`，`python3 -m venv .venv`。
1. 进入 venv：`. .venv/bin/activate`。
1. 安装依赖：`pip install --upgrade pip`，`pip install -r requirements.txt`。
1. 密钥配置：`cp conf/local_settings.py.example conf/local_settings.py`，编辑 `conf/local_settings.py`，其中有两条命令，需要执行并把输出贴在相应位置。
1. 设置环境变量：`export DJANGO_SETTINGS_MODULE=conf.settings.hackergame`。
1. 数据库初始化：`./manage.py migrate`。
1. Static 目录初始化：`./manage.py collectstatic`。
1. Google 与 Microsoft app secret 写入数据库：`./manage.py setup`。
1. 退出 venv：`deactivate`。
1. uWSGI 相关配置文件：`cp conf/systemd/hackergame@.service /etc/systemd/system/`, `cp conf/logrotate/uwsgi /etc/logrotate.d/`, `systemctl daemon-reload`, `systemctl enable --now hackergame@hackergame.service`。
1. Nginx 配置文件：`cp conf/nginx-sites/hackergame /etc/nginx/sites-available/hackergame`，`ln -s /etc/nginx/sites-available/hackergame /etc/nginx/sites-enabled/hackergame`，`systemctl reload nginx`。
1. 其他配置文件：`cp conf/pgbouncer.ini /etc/pgbouncer/`, `systemctl reload pgbouncer`。

另外我们提供 docker compose 样例，但是实际部署不使用该容器版本。

### uWSGI 运行模型

uWSGI 支持以下三种方式：

- prefork 模式，每个连接占用一个进程，进程数量由 workers 或 processes 参数控制；
  - workers 参数同时也控制了下面两者中进程的数量。
- threaded 模式，每个连接占用一个线程，线程数量由 threaded 参数控制；
- gevent 模式，每个连接占用一个 gevent 绿色线程，绿色线程数量由 gevent 参数控制。

相关参数由 `conf/uwsgi.ini` 与 `conf/uwsgi-apps/` 下对应的 ini 文件控制，由 systemd service 的参数选择使用哪个 ini 文件（例如，`hackergame@hackergame.service` 即对应 `hackergame.ini`）。

由于部分请求比较耗时（socket 相关的代码，例如 OAuth），prefork 在部分场景下无法提供足够的并发，因此 `conf/uwsgi-apps` 下默认为 gevent 模式。如果不希望使用 gevent，可将相关配置中 `gevent` 开头的配置注释，并且添加/调整其他对应的参数。

另外，如果需要使用 Debian 自带的 uWSGI 与 gevent plugin 等相关设施（包括 init 服务和 logrotate 配置，而非 pip 与本仓库的配置），需要取消注释 `plugin` 项。

#### 数据库连接池

由于 gevent 模式不支持 Django 自带的连接池特性（`CONN_MAX_AGE`，会导致 Django 开启的数据库连接一直无法释放），这里部署时采用了 PgBouncer 作为外部的连接池（或者说是数据库连接的代理）。

#### 运行情况检查

可以使用 [`uwsgitop`](https://uwsgi-docs.readthedocs.io/en/latest/StatsServer.html#uwsgitop) 来查看 uWSGI 运行情况，相关信息对于非 gevent 的 uwsgi 模式来讲很有帮助。

1. 安装 `pip install uwsgitop`。
1. 执行 `uwsgitop /run/uwsgi/app/hackergame/stats.socket` 查看。

## 运行

注：运行所有以 `./manage.py` 开头的命令都需要先进入 venv 和设置环境变量。

在开发环境中，用 `./manage.py runserver` 运行服务器。

为了方便测试，`./manage.py fake_data` 会用随机生成的数据填充数据库。在登录时选择“调试登录”，输入 `root` 可以登录这样创建的超级管理员账号，输入数字可以登录这样创建的某个用户账号。

在生产环境中，需要打开网站注册，然后看 Token 开头的数字，这是你的用户 ID。运行 `./manage.py shell` 并执行以下语句来将你设为超级管理员：
```python3
uid = 1  # 你的用户 ID
from django.contrib.auth.models import User
u = User.objects.get(pk=uid)
u.is_staff = True
u.is_superuser = True
u.save()
```

`./manage.py import_data` 可以导入题目仓库。

在罕见情况下，排行榜计算可能因为缓存逻辑而出现错误，可以用 `./manage.py regen_all` 来重新生成所有缓存。

## 代码结构说明

假设读者已经熟悉 Django app 中包含的常见内容，只列出其他需要说明的项目。

```
conf/                           各种配置文件
    local_settings.py           不应提交进 git 的密钥等信息
    local_settings.py.example   模板
    nginx-sites/                Nginx 配置文件
    settings/                   Django settings
    uwsgi-apps/                 uWSGI 配置文件
frontend/                       “前端”，和登录、HTTP、HTML 等打交道
    auth_providers/             allauth 库以外的登录方式
    adapters.py                 allauth 库登录时执行的逻辑
    utils.py                    这里写了一个每分钟最多发 5 封报错邮件的逻辑
server/                         “后端”，只处理业务和权限逻辑
    announcement/               公告
        interface.py            对外接口，只要不绕过它，业务和权限逻辑就有保证
        models.py               interface.py 内部数据，别人不应该读写
    challenge/                  题目和动态 flag
    submission/                 提交判定、成绩计算、排行榜
    terms/                      用户条款
    trigger/                    比赛时间节点
    user/                       用户、组别、个人信息
    context.py                  表示当前用户权限和时间，几乎所有操作都需要提供
    exceptions.py               异常基础设施
```

## 用户和权限相关

在 Django 原生的 auth 模块后台（/admin/auth/）可以管理（原生的）用户和组。这些原生用户的用户名会比较乱，不好找到某个用户，建议先确定用户 id，然后随便点开一个用户后，改 URL 中的数字。Django 原生的用户概念和 hackergame 的用户概念是两种不同的对象，但 id 相同。后者在这里管理 /admin/user/。

对于 Django 原生的用户和权限概念，很多是没什么意义的，代码中并没有用到，用到的有：
- “工作人员状态”（is_staff）控制这个用户会不会在首页题目列表底部看到一个“管理”链接，点击可以跳转到后台。但不影响任何权限
- “超级用户状态”（is_superuser）可以绕过一切权限检查
- 可以随便自行创建用户组，来方便给多个用户授予相同的权限集合
- 权限中，这些是比较常用的：
  - announcement | announcement | *
  - challenge | challenge | *
  - frontend | credits | *
  - frontend | page | *
  - frontend | qa | *
  - submission | submission | *
  - terms | terms | *
  - trigger | trigger | *
  - user | user | *

注意：这些权限仅仅是给用户做了一种标记，至于各种操作到底能不能成功，能看到什么结果，还取决于代码中写的条件。例如 https://github.com/ustclug/hackergame/blob/d4c7e6fac903442d27ac28138e81359e98458b7d/server/challenge/interface.py#L36-L44 如果有管理题目或查看题目权限，可以用这个接口加载任何一道题的信息。但即使没有，只要用户已登录、已同意用户条款、已填好个人信息、当前比赛处于可以看题的状态（也就是比赛中或结束后）、这道题是 enabled，这些条件全部满足，也可以加载。

## 报错邮件

发生未捕获的异常时会给管理员发报错邮件，收件人列表是 `settings.ADMINS`。代码中有专门的设计来实现邮件限速，短时间内达到报错次数上限时会丢弃之后的报错。以下报错是已知常见并且不需要在意的：
```
Internal Server Error: /accounts/microsoft/login/callback/
NoReverseMatch at /accounts/microsoft/login/callback/
Reverse for 'socialaccount_signup' not found. 'socialaccount_signup' is not a valid view function or pattern name.
```

## 常见问题

问：怎么查看某个组别/某个分类排行榜？

答：`/board/` 和 `/first/` 两个 URL 支持形如 `?group=ustc&category=web` 的参数。

问：怎么管理用户权限？

答：需要先知道用户 ID，假设为 1，在 `/admin/auth/user/1/change/` 可以管理权限。

问：怎么编辑首页？

答：需要“frontend | page | Can change page”权限，然后在 `/admin/frontend/page/` 编辑唯一一条记录。

问：怎样才能在首页看到各种管理功能（例如所有排行榜，以及题目列表底部的“管理”按钮）？

答：相应用户需要被勾选“工作人员状态”，这个选项和权限无关，仅影响界面显示。

问：“不计分”和“已封禁”两个组别有什么区别？

答：后者不能看到题目，不能做题，不能打开首页。

问：加群验证码是什么？

答：高校组别的选手会在首页上看到 QQ 群号和加群验证码，加群验证码是两个数字，前面的数字是用户 ID。管理员审核加群时，应打开 `/user/`，输入用户 ID，即可查出正确的加群验证码。需要有查看用户信息权限才能查出此项信息。

问：怎么备份数据库？

答：`pg_dump -U hackergame -f backup.sql`。

问：怎么恢复数据库？

答：`psql -U hackergame -f backup.sql`，注意只应该向刚创建的空白数据库中执行这个操作。

问：还有什么要备份的信息？

答：Media 目录，里面装着导入的题目中供选手下载的文件，在生产环境部署中位于 `/var/opt/hackergame/media`。

问：普通用户为什么可以访问后台页面 `/admin/user/`？

答：这只是一个 UI，和权限模型无关。用户能看到和修改的内容仍然受自己的权限限制。

问：为什么有的页面的 HTML 中包含了所有用户个人信息/所有题目信息？

答：每个用户能看到的内容仍然受自己的权限限制。所有用户的 ID、组别、昵称都是公开的，所有人都可以看到。如果你有特别的权限（例如查看题目 flag），你会看到更多信息，不要泄露你得到的 HTML 源代码。

问：一些特别的查询需求怎么实现？

答：只要是你有权限调用的接口，都可以自己发请求调用。打开任何一个载入了 `axios.min.js` 的页面，如 `/user/`，打开浏览器的 console，即可写类似这样的代码：
```js
axios.post('/admin/user/', {method: 'get', args: {pk: 1}}).then(v => console.log(v));
```
