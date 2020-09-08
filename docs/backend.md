## 开发服务器
### 本地运行
```bash
virtualenv .env
. .env/bin activate
pip install -r requirements.txt
python manage.py init_dev
python manage.py runserver
```

### 测试服务器
http://sin.coherence.codes:8001/

superuser: 用户名: root, 密码: root

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

需要重建榜单的情形
- 用户被封禁
- 某道题的启用状态改变
- 某题新增/删除了一个子题
- 一个用户加入/退出了一个组

管理员默认不参与排行榜, 用 auth_group 的一个组 no_score 表示.
因为 superuser 默认拥有所有权限, 所以不能使用权限来表示是否参与排行榜

## TODO

- Superuser 是否可以无视比赛阶段的限制呢
- 后期可以考虑重新生成一下 migrations

## 其他
- AuthGroup 的 no_score 和 banned 两个组的初始化在 `user/migrations/0002_init_auth_group.py` 中进行
- 以下两种情况需更新 ExprFlag 表:
    - User 创建
    - 类型为 `expr` 的 SubChallenge 的创建或 flag 字段的更新
    
## 初始化
- 在 Stage 表中新建一行
