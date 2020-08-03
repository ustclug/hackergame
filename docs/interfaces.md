# 接口

所有 API 默认前缀为 `/api/`.

所有 API 默认 Request 和 Response 的 Content-Type 都为 `application/json`.

## 默认状态码

- 成功: 200 OK
- 成功, 操作为创建: 201 Created
- 成功, 无响应内容: 204 No Content
- 传入的字段不符合规范或 Validation Error: 400 Bad Request
- 权限不足: 403 Forbidden
- 未找到: 404 Not Found

## 用户

### 注册

- Request

  - Url: `user/register/`

  - Method: POST

  - ```
    {
        "username": "cjc7373",
        "password": "123456",
    }
    ```
  
- Response: 几种 400 Bad Request 的情况

  - 用户名已存在: 

    ```
    {"username": "A user with that username already exists."}
    ```

  - 密码太短

    ```
    {"password": "Password too short."}
    ```

  - 密码不一致

    ```
    {"non_field_errors": "Passwords are not same."}
    ```


### 登录

- Request

  - Url: `user/login/`

  - Method: POST

  - ```
    {
        "username": "cjc7373",
        "password": "123456",
        "allow_terms": true //可选
    }
    ```

- Response

  - 若用户未同意用户条款或用户条款已更新
  
    - 403 Forbidden
  
    - ```
      {
          "term": [
              {
                  "name": "xxxxx",
                  "content": "xxxx",
                  "date_created": "xxx"
              }
          ]
      }
      ```

### 登出

- Request
  - Url: `user/logout/`
  - Method: POST

### 获取个人资料

- Request

  - Url: `user/`
  - Method: GET

- Response

  ```
  {
      "username": "cjc7373",
      "email": "c@ac.com",
      "phone_number": "13012345678",
      "name": null,
      "token": "1:123123"
  }
  ```

### 修改个人资料

目前只能改 name..

- Request
  - Url: `user/`

  - Method: PUT

  - ```
    {"name": "xxx"}
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

  - ```
    {
        "name": "某大学",
        "rules": {
            "has_phone_number": true,
            "has_email": true,
            "email_suffix": "xx.edu.cn", //可选
            "has_name": true,
            "must_be_verified_by_admin": true,
        },
        "apply_hint": "xxx", //可选
    }
    ```
  
- Response: 组的信息, 字段同上, 多了一个id

### 查看组列表

- Request

  - Url: `group/`
  - GET

- Response

  - ```
    [
        {...},
        {...},
    ]
    ```

  - 字段同创建, 多了`id`, `verified`, `verify_message`

### 查看组信息

- Request
  - Url: `group/1[id]/`
  - GET
  
- Response

  - ```
    {
        "name": "xxx",
        "rules": {
            "has_phone_number": true,
            "email_suffix": "xx.edu.cn",
            ...
        },
        "rules_meet": {
            "has_phone_number": true,
            "email_suffix": false,
            ...
        },
        "apply_hint": "xxx",
    }
    ```

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

  - ```
    {
        "apply_message": "xxx",
    }
    ```
  
- Response:

  - ```
    {
        "status": "pending" //若无需要管理员验证这一规则则为"accepted"
    }
    ```
    
  - 重复申请:
  
    ```
    {"non_field_errors": "The fields user, group must make a unique set."}
    ```
  
    

### 查看加入申请

- Request

  - Url: `group/1/application/`
  - Method: GET

- Response

  - ```
    [
        {"user": {...}, "apply_message": "xxx"},
        {...},
    ]
    ```

### 同意或拒绝某一申请

- Request
  - Url: `group/1/application/1[id]`

  - Method: PUT

  - ```
    {
        "status": "rejected" //拒绝, accepted 为同意
    }
    ```



### 查看成员

- Request

  - Url: `group/1/member/`
  - Method: GET

- Response

  - ```
    [
        {"apply_message": "xxx", "user": {(字段和个人资料一致)}},
    ]
    ```

### 删除成员

- Request
  - Url: `group/1/member/10[user_id]`
  - Method: DELETE
  

## 比赛

### 查看比赛的所有阶段

- Request
    - Url: `stage/`
    - Method: GET
    
- Response
    - ```
        {
            "start_time": "",
            "end_time": "",
            "practice_start_time": "",
            "pause": [
                {"start_time": "", "end_time": ""}
            ]
        }
        ```

## 查看比赛的当前阶段
- Request
    - Url: `stage/current/`
    - Method: GET
    
- Response
    - ```
        {
            "status": "not_start"
        }
        ```


## 题目

### 查看已启用的题目
- Request
    - Url: `challenge/`
    - Method: GET
    
- Response
    - ```json5
        [
            {
                "id": 1,
                "name": "test_problem",
                "category": "test",
                "detail": "test_detail",
                "prompt": "test_prompt",
                "sub_challenge": [
                    {
                        "id": 1,
                        "name": "",
                        "score": 50
                    }
                ]
            }
        ]
        ```

## 提交

### 提交一个 flag

- Request
    - Url: `/submission/`
    - Method: POST
    - ```json5
        {
            "challenge": 1,
            "flag": "flag{hello}"
        }
        ```

- Response
    - ```json5
        {
            "detail": "correct" // 或者为 wrong
        }
        ```
      
## 榜单

### 获取分数榜单

- Request
    - Url: `/borad/score/`
    - Method: GET
    - Query string: category=?&group=?(group id)
      若 category 为空则为所有分类, 若 group 为空则为所有人
      
- Response
    - ```json5
        [
            {
                "user": 1, //id
                "score": 100,
                "time": "2020-05-24T02:44:12.498Z"
            }
        ]
        ```

