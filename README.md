# 企业资产管理系统

基于 `Django + DRF` 搭建的企业资产管理系统，默认使用 `SQLite` 运行开发环境，并预留了切换到 `MySQL` 的配置入口。

## 当前已实现

- 用户登录、三级角色权限控制、部门归属与数据行级隔离
- 部门管理
- 资产分类管理
- 资产台账管理
- 资产领用与归还
- 资产调拨
- 资产维修
- 资产报废
- 仪表盘统计
- 操作日志
- REST API（`/api/v1/`）
- AI 对话面板
  - 页面右下角浮窗聊天
  - 流式输出回复
  - 结合当前用户可见资产、领用、维修数据进行问答
  - 支持通过 Django Admin 管理 `AI 配置`、`对话会话`、`对话消息`
  - 仪表盘提供 AI 管理快捷入口

## AI 助手配置

推荐直接在 Django Admin 中配置 AI，而不是手动改 `.env`：

- 后台首页：`/admin/`
- AI 分组入口：`/admin/ai/`
- AI 配置页：`/admin/ai/aiconfig/`

配置项包括：

- `API Key`
- `API Base URL`
- `模型名称`

如果未配置 `API Key`，聊天面板会提示先到后台的 `AI 配置` 页面完成设置。

## 已预留的扩展点

- `apps/core/extensions.py`
  - 用于后续接入审批流、消息通知、Webhook 或第三方系统同步
- 核心业务模型的 `extension_data`
  - 便于后续追加自定义字段
- `api/v1/`
  - 已做版本化路由，方便后续继续扩展接口
- `ASSET_APP` 配置项
  - 预留审批、通知等开关位

## 本地启动

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py seed_demo
.\.venv\Scripts\python manage.py runserver
```

## 访问地址

- 仪表盘：[http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
- 登录页：[http://127.0.0.1:8000/accounts/login/](http://127.0.0.1:8000/accounts/login/)
- Django Admin：[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- 资产 API：[http://127.0.0.1:8000/api/v1/assets/](http://127.0.0.1:8000/api/v1/assets/)

## 演示账号

- 管理员：`admin / admin123456`
- 资产管理员：`asset_manager / manager123456`
- 普通员工：`employee / employee123456`

## 当前权限范围

- 管理员
  - 可查看和管理全量数据
  - 可进入 Django Admin 管理 AI 配置与会话数据
- 资产管理员
  - 只能查看本部门资产和业务记录
  - 可在前台页面进行本部门业务操作
- 普通员工
  - 只能查看分配到本人名下的资产，以及与本人相关的领用、维修、报废记录

用户部门归属保存在 [apps/core/models.py](D:/biyechesi/biyechesi/qyglxt/apps/core/models.py:33) 的 `UserProfile` 中。

## 后续建议扩展

- Excel 导入导出
- 附件上传与资产图片
- 二维码 / 条码盘点
- 消息通知与到期提醒
- 更细粒度的数据权限
- 独立知识库与更完整的 AI 助手编排能力
