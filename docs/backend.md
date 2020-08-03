## 用户

### 封禁
用户的封禁状态采用 auth_group 中的一个组表示. 被封禁的用户将
无法登录, 并不在排行榜中显示.

## 榜单
需要重建榜单的情形
- 用户被封禁
- 某道题的启用状态改变
- 某题新增/删除了一个子题
- 一个用户加入/退出了一个组

## TODO

- banned user
- throttling
- admin page
- Group admin 任意多个?
- auto_now_add=True 可能不利于测试?

## 其他
- 是否有必要采取类似 Service 的设计?

  想法: 对于同时适用于用户的管理员的写到 model 层,
  只适用于用户的写到 view 层