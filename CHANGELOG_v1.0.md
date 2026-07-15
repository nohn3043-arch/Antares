# GFSIP v0.1 → v1.0 变更日志

## 冻结项
- 固定帧头冻结为 44 bytes。
- Session ID 明确由 Responder 生成。
- Sequence 明确为单方向 Session 级单调序号。
- Channel ID 使用 Initiator 奇数、Responder 偶数。
- Extension Header 固定为确定性 CBOR。
- QUIC ALPN 固定为 `gfsip/1`。
- Core 消息类型 `0x01`–`0x16` 冻结。

## 安全
- 增加握手 transcript 绑定与降级检测。
- 增加恢复令牌身份绑定、轮换和重放防护。
- 禁止 0-RTT 执行副作用操作。
- 增加凭据撤销、认证上下文过期、解压上限和共享凭据责任边界。

## 交付语义
- 区分传输确认与 APP_ACK。
- 副作用操作强制使用 idempotency_key。
- 明确去重窗口与持久化边界。
- 明确不提供通用 Exactly Once。

## Audit/1
- parent_event_ids 仅代表直接声明前驱。
- 禁止从时间先后推导因果关系。
- 增加自环、已知循环和父事件上限检查。
- 增加规范化签名与责任模糊区。

## Federation/1
- 增加 Descriptor 版本、过期和撤销规则。
- 增加多信任根。
- 增加 visited_domains 与 max_hops。
- 外部目录不再是本域通信的强依赖。

## 可验证性
- 增加机器可读状态机。
- 增加逻辑消息 JSON Schema。
- 增加稳定数值错误码注册表。
- 增加一致性测试清单。
- 增加需求追踪矩阵。

## 尚未完成
- 两个无共同代码来源的公开实现。
- 公开互操作报告。
- 独立安全审计。
- 三个独立生产试点域。
- 正式标准组织流程。
