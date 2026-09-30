# API 合约草案

只有 GET /health、GET /api/v1/modules 和 GET / 已实现。以下接口均待开发，统一前缀 /api/v1；用户与团队从已验证会话取得。

| 方法/路径 | 功能 | 权限/约束 |
|---|---|---|
| POST /auth/login；POST /auth/logout | 登录/退出 | 哈希密码与限流 |
| GET /me | 身份与角色 | 启用会话 |
| GET /dictionaries | 字典 | 启用用户 |
| POST /leads | 提交线索 | 运营；disease_id/wechat/channel_id/region_id必填 |
| GET /leads；GET /leads/{id} | 列表与详情 | 行级筛选；脱敏；分页 |
| POST /leads/{id}/assign | 分配/转派 | 主管团队范围；原因、expected_version |
| POST /leads/{id}/accept | 接收 | 当前咨询；本次分配有效 |
| POST /leads/{id}/contact/reveal | 限时联系方式 | 当前咨询已接收；审计先写成功 |
| POST /leads/{id}/events | 状态回填 | 当前咨询；to_status/result/expected_version |
| POST /leads/{id}/notes | 咨询备注 | 当前咨询；加密存储 |
| POST /imports；GET /imports/{id} | 导入及错误行 | 运营只归属自己；幂等键 |
| GET /exceptions | 异常中心 | 主管团队范围 |
| GET /dashboard | 维度漏斗 | 运营个人汇总、主管团队、管理员全局 |
| PATCH /consultants/{id}/profile | 权重、值班、容量 | 主管团队范围 |
| PATCH /users/{id}/enabled | 停用与撤销 | 管理员 |
| GET /audit | 日志 | 授权管理员；禁止患者明文 |

分页 page/page_size，默认20、上限100。写入支持 Idempotency-Key；冲突409、未登录401、越权/不存在统一404或403策略、校验422。不得在错误中泄露重复联系方式或他人线索。请求ID贯穿业务事件与审计。示例录入：

```json
{"disease_id":1,"wechat":"fictional_demo_only","channel_id":2,"region_id":3,"nickname":"虚构测试"}
```

接收、查看、回填和转派都在服务端重新鉴权；前端不传 created_by、assigned_to、role 等可信字段。导出第一阶段不开接口，审批后另行实现。通知首版站内，不自动向微信或患者发送消息。
