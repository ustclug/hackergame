## 用户

### 封禁
用户的封禁状态采用 auth_group 中的组 banned 表示. 
被封禁的用户将无法登录, 并不在排行榜中显示.

被封禁的用户会自动登出. 这是通过一个 middleware 来实现的,
还有一种方法是直接修改 Session.

## 榜单
需要重建榜单的情形
- 用户被封禁
- 某道题的启用状态改变
- 某题新增/删除了一个子题
- 一个用户加入/退出了一个组

管理员默认不参与排行榜, 用 auth_group 的一个组 no_score 表示.
因为 superuser 默认拥有所有权限, 所以不能使用权限来表示是否参与排行榜

## TODO

- throttling
- Group admin 任意多个?

## 其他
- AuthGroup 的两个组的初始化在 user 的 migrations 中进行
