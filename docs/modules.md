# 模块与接口开发契约

以下业务模块是设计契约，除分配策略函数外尚未实现。

| 模块 | 职责 | 后续接口 |
|---|---|---|
| 身份与权限 | 登录、账号停用、团队范围、会话版本 | POST /api/auth/login；POST /api/auth/logout |
| 运营录入 | 手工、固定格式粘贴确认、Excel 校验 | POST /api/leads；POST /api/imports |
| 线索查询 | 分页、来源、状态、范围筛选 | GET /api/leads；GET /api/leads/{id} |
| 分配引擎 | 能力、区域、值班、权重、容量、转派 | POST /api/leads/{id}/assign |
| 咨询承接 | 接收、首联、加微、回访、预约到院成交 | POST /api/leads/{id}/accept；POST /api/leads/{id}/events |
| 敏感查看 | 接收后短时授权、脱敏、审计 | POST /api/leads/{id}/contact-reveal |
| 主管异常 | 重复、接收/首联超时、回收、转派 | GET /api/exceptions；POST /api/leads/{id}/transfer |
| 经营看板 | 历史事件漏斗、来源与人员归因 | GET /api/reports/funnel |
| 系统管理 | 字典、排班、权重、停用、审计 | GET /api/audit；PATCH /api/users/{id} |

## 权限

运营只查自己提交的线索；提交后联系方式脱敏，咨询备注不可见，默认不展示单条成交金额。
咨询只查当前分配给自己的线索；接收前不解密；转派后立即撤销旧权限。
主管只查自己管理的团队；转派必须填原因。管理员默认查看聚合经营数据，敏感查看单独审计。所有权限必须在后端查询中落实，不信任前端传来的 operator_id 或 team_id。

## 分配

候选过滤：启用、值班、病种能力、区域、无严重超时阻塞、当日和同时跟进容量。
优先值 = 当日已分配有效线索数 / 权重；值相同取最久未分配者，再按 ID 稳定排序。无候选保留待分配并创建异常任务，不丢线索。
`allocation.choose` 仅完成选择。后续以 BEGIN IMMEDIATE（SQLite 开发）或行锁（生产数据库）事务重新计算计数、检查 lead.version、写入唯一活动分配、更新归属和审计。接收与回收也用版本号避免竞态。
当日按 Asia/Shanghai 划分；重复、无效是否冲减分配计数待业务确认。

## 状态

pending_assignment → pending_acceptance → accepted → wechat_added → booked → visited → converted。
accepted 可进入 followup_pending；回访成功回到 wechat_added。非终态可进入 invalid，必须有无效原因。重复进入 duplicate_review，由主管决定合并或独立保留。
转派/回收是分配事件，保留原记录，不当作成交漏斗阶段。已成交纠正走主管审计流程，不直接覆盖事件。

未加微信需原因和回访时间；预约需院区与时间；到院需实际时间；成交需项目、金额、日期及核验状态。成交金额使用整数分，禁止浮点数。

## 经营口径

漏斗用历史里程碑去重统计 lead_id，不能用当前状态枚举计数。按提交日期形成 cohort，注明观察截止日期；另提供当天发生事件指标，避免混算。
接收及时率=时限内接收/已分配；加微率=加微/接收；预约率=预约/加微；到院率=到院/预约；成交率=成交/到院。分母为 0 返回 null。
收入仅统计已核验成交净额（金额减退款）；ROI 需补渠道成本表及实际投放数据，当前不计算、不捏造收益。
