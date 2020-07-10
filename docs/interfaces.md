# 接口

所有 API 默认前缀为 `/api/`.

所有 API 默认 Request 和 Response 的 Content-Type 都为 `application/json`.

## 默认状态码

- 成功: 200 OK
- 成功, 操作为创建: 201 Created
- 成功, 无响应内容: 204 No Content
- 权限不足: 403 Forbidden
- 未找到: 404 Not Found

## 用户

### 获取个人资料

- Request

  - Url: `user/`
  - Method: GET

- Response

  ```json
  {
      "username": "cjc7373",
      "email": "c@ac.com",
      "phone_number": "13012345678",
      "name": null,
      "token": "1:123123"
  }
  ```

### 注册

- Request

  - Url: `user/registration/`

  - Method: POST

  - ```json
    {
        "username": "cjc7373",
        "password": "123456",
        "password_confirm": "123456"
    }
    ```


### 登录

- Request

  - Url: `user/login/`

  - Method: POST

  - ```json
    {
        "username": "cjc7373",
        "password": "123456",
        "allow_terms": true //可选
    }
    ```

- Response

  - 若用户未同意用户条款或用户条款已更新
  
    - 403 Forbidden
  
    - ```json
      {
          name: "xxxxx",
          content: "xxxx",
          date_created: "TODO"
      }
      ```

### 修改密码

### 找回密码

### 更换绑定邮箱

### 更换手机号码

## 组

### 创建组

- Request

  - Url: `group/`

  - Method: POST

  - ```json
    {
        name: "某大学"
        rule_has_phone_number: true,
        rule_has_email: true,
        rule_email_suffix: "xx.edu.cn", //可选
        rule_has_name: true,
        rule_must_be_verified_by_admin: true,
        rule_apply_hint: "xxx", //可选
        verified: true,
        verify_message: "xxx", //可选
    }
    ```
  
- Response: 组的信息, 字段同上, 多了一个id

### 查看组列表

- Request

  - Url: `group/`
  - GET

- Response

  - ```json
    [
        {...},
        {...},
    ]
    ```

  - 字段同创建, 多了一个`id`

### 查看组信息

- Request
  - Url: `group/1[id]/`
  - GET

### 修改组加入条件

- Request
  - Url: `group/1[id]/`
  - Method: PATCH
  - 格式同创建, 传入要更改的字段
- Response: 返回更新后的数据

### 删除组

- Request
  - Url: `group/1[id]/`
  - Method: DELETE

### (申请)加入组

- Request

  - Url: `group/1/application/`

  - Method: POST

  - ```json
    {
        apply_message: "xxx",
    }
    ```
  
- Response:

  - ```json
    {
        status: "pending" (若无需要管理员验证这一规则则为"accepted")
    }
    ```


### 查看加入申请

- Request

  - Url: `group/1/application/`
  - Method: GET

- Response

  - ```json
    [
        {user:{...}, apply_message: "xxx"},
        {...},
    ]
    ```

### 同意或拒绝某一申请

- Request
  - Url: `group/1/application/1[id]`

  - Method: PUT

  - ```json
    {
        status: "rejected" //拒绝, accepted 为同意
    }
    ```



### 查看成员

- Request

  - Url: `group/1/members/`
  - Method: GET

- Response

  - ```json
    [
        {...(字段和个人资料一致)},
    ]
    ```

### 删除成员

- Request
  - Url: `group/1/members/10[user_id]`
  - Method: DELETE