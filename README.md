# 一颗星短视频线索分配与咨询承接系统

南京一颗星文化传媒有限公司 · V0.1 项目骨架

## 当前状态

2026-09-30 检查：仓库默认分支 main，原提交 `7846c7a`，仅有 3 字节 README.md；未检索到 issue。以 2026-08-27《短视频线索分配与咨询承接系统设计方案 V1.0》为基础。

本版交付可运行的本地健康检查、首页占位、SQLite 建表、分配策略函数及测试。它是继续开发的基础，不是可直接接收患者信息的完整业务系统。

## 目标

替代微信群公开抛联系方式：运营提交 → 去重 → 病种/区域/值班筛选 → 权重与容量分配 → 咨询接收 → 加微信 → 预约 → 到院 → 成交。

7 个核心字段：日期、序号、病种、微信、渠道、运营、区域。其中日期、序号、运营由服务端生成。咨询备注对运营隐藏，敏感联系方式加密且查看留痕。

## 本地启动

Python 3.11+，当前骨架仅使用标准库，无需安装第三方依赖。

```bash
git clone https://github.com/584640872-ai/-.git lead-system
cd lead-system
# 若本版还在 PR 分支，请先切换：git checkout scaffold/v0.1
python -m backend.db
python -m unittest discover -s tests -v
python -m backend.server
```

macOS/Linux 可将 python 替换为 python3；Windows 可使用 py -3。
打开 http://127.0.0.1:8000，健康检查 http://127.0.0.1:8000/api/health。Ctrl+C 停止。开发数据库保存在 `var/development.sqlite3`，可删除后重新初始化（会清除本地开发数据）。不包含样例患者或真实凭据。端口固定 8000，占用时先停止其他服务。

## 目录

| 路径 | 用途 |
|---|---|
| backend/server.py | 本地 HTTP 入口，仅首页和健康检查 |
| backend/db.py | 数据库连接和初始化 |
| backend/modules/allocation.py | 能力过滤、加权优先和容量保护 |
| frontend/index.html | 响应式占位首页 |
| database/schema.sql | 首版可执行表结构 |
| docs/modules.md | 模块、权限、状态及接口开发契约 |
| docs/database.md | 表说明、约束与迁移要求 |
| docs/next-steps.md | 开发顺序、待确认信息与验收标准 |
| tests/ | 分配策略及建表测试 |
| .github/workflows/check.yml | Python 标准库测试 |

## 实现边界

已实现：本地启动、建表、健康检查、纯函数分配策略、基础测试。
待实现：账号登录、服务端行权限、加密与 HMAC 去重、业务 CRUD、分配事务、咨询回填、导入、异常任务、审计写入、驾驶舱、生产部署和平台接口。业务接口当前返回未实现，不开放敏感录入。

默认值仅供开发：权重 1、每日容量 20、同时跟进 50、接收 5 分钟、首联 15 分钟；未确认即不可当作真实业务规则。详细说明见 docs。

生产前必须建立真实认证、字段加密、团队隔离、会话撤销、审计、备份和恢复流程。不要提交 `.env`、数据库、患者聊天记录或联系方式。当前仓库公开。
