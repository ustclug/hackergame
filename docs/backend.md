## 开发服务器
### 本地运行
- 数据库: 安装 postgresql, 设置 hackergame 用户, 创建 hackergame 数据库, 并启动; 
    或自行更改数据库配置
- 缓存: 安装 memcached 并启动; 或自行更改缓存配置
```bash
cd backend
virtualenv .env
. .env/bin activate
pip install -r requirements.txt
python manage.py init_dev
```
#### 使用 Django 开发服务器
```bash
python manage.py runserver
```
#### 使用 gunicorn
```bash
export DJANGO_SETTINGS_MODULE='backend.dev'
gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --reload
```

## PEP 8 检查
```bash
flake8 . --statistics --exclude .env,migrations,dev.py --max-line-length 127
```

## 测试
```bash
export DJANGO_SETTINGS_MODULE=backend.test
pytest
```

## 权限
权限控制都放在了 Views 层. 也就是说管理面板拥有所有权限.

## 用户

### 封禁
用户的封禁状态采用 auth_group 中的组 banned 表示. 
被封禁的用户将无法登录, 并不在排行榜中显示.

被封禁的用户会自动登出. 这是通过一个 middleware 来实现的,
还有一种方法是直接修改 Session.

## 榜单
榜单表中将不会出现被禁用的题目/子题

需要更新榜单的情形:
- 用户被封禁
- 某道题的启用状态改变
- 某题新增/删除了一个子题
- 一个用户加入/退出了一个组

管理员默认不参与排行榜, 用 auth_group 的一个组 no_score 表示.
因为 superuser 默认拥有所有权限, 所以不能使用权限来表示是否参与排行榜

## 题目
### 对图片的处理
图片会在导入题目时被上传至一个用 uuid 命名的文件夹中. 
同时, 在后台编辑题目时能够上传新的图片.

## 打开题目
考虑到打开链接、下载源代码、下载文件这几个操作均可能有多个, 数据库中没有设置字段存放打开题目的方式,
打开题目的方式应直接写在题目描述中.

## TODO

- 后期可以考虑重新生成一下 migrations
- 第三方账号登录 (如 Microsoft, Github)
- 展示首页内容的 API
- 邮件服务配置
- 题目导入
- 测试的覆盖率报告
- 使用 CI 进行 Docker 构建

## 其他
- AuthGroup 的 no_score 和 banned 两个组的初始化在 `user/migrations/0002_init_auth_group.py` 中进行
- 以下两种情况需更新 ExprFlag 表:
    - User 创建
    - 类型为 `expr` 的 SubChallenge 的创建或 flag 字段的更新
    
## 初始化
- 在 Stage 表中新建一行
