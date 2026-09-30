# 一颗星 · 短视频线索分配与咨询承接系统

南京一颗星文化传媒有限公司。V0.1 是可继续开发的项目骨架，依据 2026-08-27《短视频线索分配与咨询承接系统设计方案 V1.0》。目标是用系统替代微信群抛联系方式，建立运营提交、自动分配、咨询承接、预约到院、成交与经营复盘的闭环。

## 当前交付

- 可本地启动的 Python HTTP 服务、响应式启动页、数据库健康检查。
- SQLite 初始迁移与幂等初始化脚本；用户、线索、分配、状态、回访、预约、到院、成交、审计等数据模型。
- 可执行的分配候选选择、状态流转、数据权限规则，以及针对业务边界的测试。
- 核心模块、API 合约、安全边界、指标口径与下一阶段开发清单。

**这是开发基础版本。身份认证、业务 API、加密、定时调度和工作台尚未实现，不能用于真实患者数据或直接上线。** 未实现的业务接口返回 404，不用演示接口模拟完成。

## 本地启动（Python 3.11+，无需第三方依赖）

```bash
git clone https://github.com/584640872-ai/-.git
cd -
python3 scripts/init_db.py
python3 apps/api/server.py
```

浏览器打开 http://127.0.0.1:8000 。健康检查：http://127.0.0.1:8000/health 。模块索引：http://127.0.0.1:8000/api/v1/modules 。Windows 可将 `python3` 换成 `py -3`。

```bash
python3 -m unittest discover -s tests -v
```

数据库保存在 `.data/leads.sqlite3`，不会提交 Git。重复初始化不会重复建表。停止服务使用 Ctrl+C。服务默认仅监听本机；端口可通过 `PORT` 环境变量修改。`.env.example` 是配置说明，当前服务不自动加载 `.env`。每个新 SQLite 连接必须启用 `PRAGMA foreign_keys=ON`。正式部署建议迁移 PostgreSQL，接入认证和任务调度后再开放网络访问。

## 目录

```text
apps/
  api/server.py             本地开发入口
  api/modules/assignment.py 病种、区域、值班、容量及权重规则
  api/modules/workflow.py   状态流转与必填校验
  api/modules/permissions.py 行级访问与敏感查看规则
  web/index.html            响应式启动验证页
db/migrations/001_initial.sql 数据结构
scripts/init_db.py          版本化数据库初始化
tests/                     规则与数据库约束测试
docs/architecture.md       核心模块与开发顺序
docs/database.md           表设计、约束和指标
docs/api.md                待实现 API 合约
docs/decisions.md          默认规则和待确认项
```

## 业务基线

七个核心字段：日期、序号、病种、微信、渠道、运营、区域。日期、编号、运营由服务端产生。分配先筛选启用、值班、病种、区域和容量，再按“当日已分配有效线索数 / 权重”取最小值，同分取最久未分配者。无人可接则进入待分配队列。

运营只能看自己提交的线索和脱敏结果；咨询只能看当前分配给自己的线索；接收后按需短时查看联系方式并留痕；主管按团队管理；管理员经营数据默认脱敏。转派后旧咨询立即失去访问权限。咨询备注不向运营开放。

## 下一步

优先实现认证与停用、加密及行级查询，再做线索录入/去重、事务分配、咨询状态回填，最后补齐异常队列、导入及经营驾驶舱。详见 docs/architecture.md。首版需要你确认的人员、字典、重复归属、时限和结果可见范围见 docs/decisions.md；这些不阻塞当前骨架。
