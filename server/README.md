这里存放所有“新式”Django app，它们有明确的接口（`interface.py`），其他代码只应与接口交互，不应触及底层实现（如 `models.py`）。

绝大多数 `classmethod` 接口的第一个参数都是 `context`，其中包含当前请求的上下文信息。
