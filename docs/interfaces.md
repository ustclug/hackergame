# 接口

所有 API 默认前缀为 `/api/`.

所有 API 默认 Request 和 Response 的 Content-Type 都为 `application/json`.

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
      ""
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

### 修改密码

### 找回密码

### 同意用户条款

### 绑定邮箱

### 更换绑定邮箱

## 组

### 创建组

### 获取加入条件

### 修改加入条件

### (申请)加入组

### 查看成员

### 删除成员

### 管理加入申请

