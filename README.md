# 企业资产管理系统

基于需求文档实现的普通版企业资产管理系统，使用 `Django + DRF` 搭建，开发环境默认使用 `SQLite`，并预留了 `MySQL` 切换入口。

## 当前已实现

- 用户登录与基础权限控制
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

## 已预留的扩展接口

- `apps/core/extensions.py`
  用于后续接入审批流、消息通知、Webhook 或第三方系统同步。
- 所有核心模型均带 `extension_data`
  方便后续追加自定义字段，不破坏主结构。
- `api/v1/`
  已做版本化路由，后续可以平滑扩展新接口版本。
- `ASSET_APP` 配置项
  已预留审批、通知等开关位。

## 本地启动

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py seed_demo
.\.venv\Scripts\python manage.py runserver
```

打开：

- 后台首页: [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
- 登录页: [http://127.0.0.1:8000/accounts/login/](http://127.0.0.1:8000/accounts/login/)
- 开放接口: [http://127.0.0.1:8000/api/v1/assets/](http://127.0.0.1:8000/api/v1/assets/)

## 演示账号

- 管理员: `admin / admin123456`
- 资产管理员: `asset_manager / manager123456`
- 普通员工: `employee / employee123456`

## 当前权限范围

- 管理员: 可查看和管理全部数据
- 资产管理员: 只能查看自己所属部门的资产和业务记录
- 普通员工: 只能查看分配到自己名下的资产，以及与自己相关的领用、维修、报废记录
- 管理员: 只能在系统内注册资产管理员账号
- 资产管理员: 只能在系统内注册本部门普通员工账号
- 普通员工: 不提供自助注册入口

用户部门归属保存在 [apps/core/models.py](/D:/biyechesi/qyglxt/apps/core/models.py) 的 `UserProfile` 中。

## 后续建议扩展

- 审批流和多级报废审核
- Excel 导入导出
- 附件上传与资产图片
- 二维码/条码盘点
- 消息通知和到期提醒
- 更细粒度的数据权限
