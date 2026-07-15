# GFSIP/1.0：全球联邦稳定互操作协议
## Global Federated Stable Interoperability Protocol

- **版本**：1.0
- **状态**：实现就绪候选规范
- **发布日期**：2026-07-16
- **基线承载**：QUIC
- **可选承载**：TCP + TLS 1.3
- **QUIC ALPN**：`gfsip/1`

> “1.0”表示本规范内部接口已冻结，不表示已获标准组织批准，也不表示已经完成外部专家验证。

## 1. 目标

GFSIP/1.0 允许独立组织、网络域、设备、服务和 AI Agent 在保持自治的前提下：

1. 建立加密、双向认证的 Session；
2. 在一个 Session 内创建多个 Channel；
3. 在网络切换后恢复 Session；
4. 对副作用操作执行有限窗口去重；
5. 交换结构化错误和能力信息；
6. 可选记录签名因果事件；
7. 通过多信任根实现跨域互操作；
8. 隔离单域故障。

## 2. 非目标

GFSIP/1.0：

- 不替代 IP、BGP、DNS、QUIC 或 TLS；
- 不提供全球唯一控制权；
- 不承诺零故障；
- 不提供无物理路径通信；
- 不提供无限时间的 Exactly Once；
- 不自动确定法律责任；
- 不把时间先后自动解释为因果关系；
- 不要求全球唯一身份根或目录。

## 3. 规范关键词

- **MUST / MUST NOT**：强制要求。
- **SHOULD / SHOULD NOT**：存在记录化理由时允许偏离。
- **MAY**：可选行为。
- **Fatal Error**：终止 Session。
- **Operation Error**：终止当前操作或 Channel。

## 4. Profiles

### 4.1 Core/1

所有兼容实现 MUST 支持：

- QUIC 与 ALPN `gfsip/1`；
- 版本协商；
- 双向认证接口；
- Session 与 Channel；
- DATA 与 APP_ACK；
- Message ID 与幂等键；
- 会话恢复；
- PING / PONG；
- GOAWAY；
- 结构化 ERROR；
- 资源上限协商；
- 未知可选扩展的安全忽略。

### 4.2 Audit/1

在 Core/1 上增加：

- EVENT；
- 直接因果前驱；
- 执行者、规则版本和状态摘要；
- 规范化事件签名；
- 因果自环和已知循环拒绝。

### 4.3 Federation/1

在 Core/1 上增加：

- Domain Descriptor；
- 多信任根；
- 跨域路由查询；
- 描述符有效期、撤销和故障隔离。

## 5. 实体

| 实体 | 定义 |
|---|---|
| Node | 实现 GFSIP 的设备、服务、网关或 Agent |
| Domain | 由单一治理主体管理的自治域 |
| Gateway | 连接两个或多个 Domain 的 Node |
| Session | 两个 Node 之间可恢复的逻辑会话 |
| Channel | Session 内独立的双向通信单元 |
| Event | 带直接因果前驱的审计记录 |
| Domain Descriptor | 描述入口、能力和信任锚的签名对象 |

Initiator 创建奇数 Channel ID；Responder 创建偶数 Channel ID；`0` 永久保留为控制通道。已关闭的 Channel ID 不得复用。

## 6. 承载

### 6.1 QUIC

实现 MUST：

1. 使用 ALPN `gfsip/1`；
2. 使用 QUIC 加密；
3. 将控制通道映射到双向 Stream；
4. 将 Channel 映射到独立 Stream，或使用可证明公平的共享调度；
5. 使用 QUIC 流量控制与拥塞控制；
6. 不实现与 QUIC 冲突的包级重传；
7. 禁止 0-RTT 执行副作用操作。

### 6.2 TCP + TLS

可选实现 MUST：

- 使用 TLS 1.3；
- 使用固定帧头分帧；
- 分配 Payload 缓冲区前验证长度；
- 防止单 Channel 永久阻塞其他 Channel。

跨主机明文承载 MUST NOT 使用。

## 7. 编码

- 固定宽度整数使用 big-endian。
- Extension Header 使用确定性 CBOR。
- Map 键为 UTF-8 文本。
- 不允许无限长度字符串或容器。
- 拒绝重复 Map 键。
- 数值使用最短编码。
- 签名对规范化 CBOR 字节计算。
- JSON 只用于本文示例。

## 8. 固定帧头

固定帧头长度：**44 bytes**。

```text
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Magic = "GFS1"                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Major | Minor | Type          | Flags                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Header Length                 | Reserved                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                         Payload Length                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
|                         Session ID (128)                      |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          Sequence (64)                        |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          Channel ID                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                 Extension Header (variable)                  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                         Payload (variable)                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

| 字段 | 长度 | 规则 |
|---|---:|---|
| Magic | 4 | ASCII `GFS1` |
| Major | 1 | `1` |
| Minor | 1 | `0` |
| Type | 1 | 消息类型 |
| Flags | 1 | 帧标志 |
| Header Length | 2 | Extension Header 长度 |
| Reserved | 2 | 发送为 0 |
| Payload Length | 4 | Payload 长度 |
| Session ID | 16 | 建立前全零 |
| Sequence | 8 | 单方向 Session 序号 |
| Channel ID | 4 | 控制消息为 0 |

```text
frame_length = 44 + header_length + payload_length
```

接收端 MUST 在内存分配前验证长度和整数溢出。

### 8.1 Session ID

- 由 Responder 在 SESSION_READY 时生成；
- 128-bit 随机值；
- 至少 122 bits 不可预测性；
- 仅为标识，不是认证凭据；
- 恢复时保持不变。

### 8.2 Sequence

- SESSION_READY 后，两端发送方向各自从 1 开始；
- 每帧递增 1；
- 不因 Channel 改变而重置；
- 恢复后继续原序号；
- 重复或过旧序号触发 `SEQUENCE_REPLAY`；
- 溢出前必须新建 Session。

### 8.3 Flags

| 位 | 名称 |
|---:|---|
| 0 | ACK_REQUIRED |
| 1 | AUDIT_PRESENT |
| 2 | END_CHANNEL |
| 3 | IDEMPOTENT |
| 4 | COMPRESSED |
| 5 | EARLY_DATA |
| 6–7 | RESERVED |

## 9. 消息类型

| Type | 名称 | Channel |
|---:|---|---:|
| `0x01` | CLIENT_HELLO | 0 |
| `0x02` | SERVER_HELLO | 0 |
| `0x03` | AUTH | 0 |
| `0x04` | AUTH_RESULT | 0 |
| `0x05` | SESSION_READY | 0 |
| `0x06` | RESUME | 0 |
| `0x07` | RESUME_RESULT | 0 |
| `0x08` | OPEN_CHANNEL | 0 |
| `0x09` | CHANNEL_READY | 0 |
| `0x0A` | CLOSE_CHANNEL | 0 |
| `0x0B` | DATA | 非 0 |
| `0x0C` | APP_ACK | 对应 Channel |
| `0x0D` | EVENT | audit Channel |
| `0x0E` | PING | 0 |
| `0x0F` | PONG | 0 |
| `0x10` | CAPABILITY_UPDATE | 0 |
| `0x11` | GOAWAY | 0 |
| `0x12` | ERROR | 0 或相关 Channel |
| `0x13` | DOMAIN_DESCRIPTOR | federation Channel |
| `0x14` | ROUTE_QUERY | federation Channel |
| `0x15` | ROUTE_RESULT | federation Channel |
| `0x16` | STATE_SYNC | state-sync Channel |
| `0x17`–`0x7F` | 标准保留 | — |
| `0x80`–`0xFF` | 私有实验 | — |

未知强制扩展触发 `UNSUPPORTED_CRITICAL_EXTENSION`。

## 10. Session 状态机

```text
NEW
  ↓ CLIENT_HELLO
NEGOTIATING
  ↓ SERVER_HELLO
AUTHENTICATING
  ↓ 双向认证成功
ESTABLISHED
  ↘ 传输路径失效
   DEGRADED
     ↓ RESUME
   RESUMING
     ↓ 成功或安全的部分恢复
   ESTABLISHED
  ↓ GOAWAY
DRAINING
  ↓ 所有 Channel 关闭
CLOSED
```

强制不变量：

1. ESTABLISHED 前不得处理 DATA、EVENT、ROUTE_QUERY；
2. AUTHENTICATING 只允许控制消息；
3. Channel 必须先打开；
4. GOAWAY 后不得创建新 Channel；
5. CLOSED 不得处理协议输入；
6. 同一幂等键在有效窗口内不得重复产生副作用；
7. EVENT 不得以自身为父事件；
8. 已知因果图必须无环；
9. 恢复不得提升权限。

## 11. 握手

```text
Initiator                               Responder
   |--- CLIENT_HELLO --------------------->|
   |<-- SERVER_HELLO ----------------------|
   |--- AUTH ----------------------------->|
   |<-- AUTH ------------------------------|
   |<-- AUTH_RESULT -----------------------|
   |--- AUTH_RESULT ---------------------->|
   |<-- SESSION_READY ---------------------|
```

CLIENT_HELLO：

```json
{
  "versions": ["1.0"],
  "profiles": ["core/1", "audit/1", "federation/1"],
  "compressions": ["none", "zstd"],
  "auth_methods": ["mtls", "signed-token"],
  "node_id": "urn:gfsip:node:client.example",
  "domain_id": "urn:gfsip:domain:example-a",
  "max_header": 65535,
  "max_frame": 1048576,
  "max_channels": 128,
  "dedupe_window_seconds": 3600,
  "nonce": "32-byte-random-value"
}
```

SERVER_HELLO：

```json
{
  "selected_version": "1.0",
  "selected_profiles": ["core/1", "audit/1"],
  "selected_compression": "none",
  "selected_auth_method": "mtls",
  "node_id": "urn:gfsip:node:server.example",
  "domain_id": "urn:gfsip:domain:example-b",
  "max_header": 32768,
  "max_frame": 524288,
  "max_channels": 64,
  "dedupe_window_seconds": 1800,
  "nonce": "32-byte-random-value"
}
```

有效上限采用双方较小值。服务端选择最高共同版本；选择低于共同最高版本必须触发降级检测。双方 nonce、版本、Profile、Node ID、Domain ID 和传输绑定信息必须被认证证明覆盖。

## 12. 认证与授权

Node ID 推荐格式：

```text
urn:gfsip:node:<domain-controlled-identifier>
```

Node ID 必须绑定凭据，但不得单独作为授权依据。

Core/1 至少实现一种：

- `mtls`
- `signed-token`
- `psk`（仅封闭域）
- `hardware-attested`

AUTH：

```json
{
  "method": "signed-token",
  "credential": "opaque-or-detached-reference",
  "proof": "signature-over-transcript",
  "key_id": "urn:gfsip:key:client.example:2026-01",
  "expires_at": "2026-07-16T11:00:00Z"
}
```

授权至少输入：

```text
authenticated_node_id
authenticated_domain_id
auth_context_id
channel_type
operation
resource
profile
session_security_level
```

凭据必须有有效期和撤销机制。认证上下文过期前必须重新认证。撤销后恢复令牌必须失效。

## 13. SESSION_READY

```json
{
  "session_id": "128-bit-value",
  "resume_token": "opaque-token",
  "resume_expires_at": "2026-07-16T11:00:00Z",
  "auth_context_id": "opaque-auth-context",
  "effective_limits": {
    "max_header": 32768,
    "max_frame": 524288,
    "max_channels": 64,
    "dedupe_window_seconds": 1800
  }
}
```

恢复令牌必须绑定 Session、双方 Node ID、认证上下文、到期时间、协议版本和 Profile 集。

## 14. Channel

OPEN_CHANNEL：

```json
{
  "channel_id": 17,
  "channel_type": "task",
  "ordered": true,
  "delivery": "application_ack",
  "priority": 20,
  "max_inflight": 64,
  "content_types": ["application/json"],
  "metadata": {"service": "inventory.reserve"}
}
```

生命周期：

```text
IDLE → OPENING → OPEN → HALF_CLOSED → CLOSED
```

规则：

- Initiator 使用奇数 ID；
- Responder 使用偶数 ID；
- ID 不复用；
- ordered=true 时按 Channel 顺序交付；
- priority 范围 0..255，值越小越高；
- 调度不得使低优先级永久饥饿；
- 超出 max_inflight 返回 `FLOW_CONTROL_LIMIT`。

## 15. DATA 与交付语义

DATA：

```json
{
  "message_id": "018f2f86-7a36-7c9e-a6cd-a7c7508048b4",
  "idempotency_key": "order-8842-reserve-v1",
  "operation": "inventory.reserve",
  "content_type": "application/json",
  "deadline_ms": 5000
}
```

- Message ID 用于关联，不提供去重保证；
- 副作用操作 MUST 带 idempotency_key；
- 同一 key 已完成时不得重复执行；
- 同一 key 正在处理时返回 `IN_PROGRESS`；
- key 过期后不得假定仍受保护。

APP_ACK：

```json
{
  "message_id": "018f2f86-7a36-7c9e-a6cd-a7c7508048b4",
  "idempotency_key": "order-8842-reserve-v1",
  "status": "accepted",
  "result_hash": "sha256:...",
  "processed_at": "2026-07-16T10:00:00Z"
}
```

GFSIP 提供传输可靠性、应用确认和有限窗口去重；不提供跨永久存储丢失的全局 Exactly Once。

## 16. 会话恢复

RESUME：

```json
{
  "session_id": "2f952c2d-7f80-4b3c-a61a-57d413ad39c9",
  "resume_token": "opaque-token",
  "last_received_sequence": 9821,
  "last_sent_sequence": 7760,
  "open_channels": [3, 8, 17],
  "state_digest": "sha256:...",
  "resume_nonce": "32-byte-random-value"
}
```

状态：

- `resumed`
- `partial`
- `new_session_required`
- `rejected`

规则：

1. 重新完成传输安全握手；
2. 当前认证 Node ID 必须匹配令牌；
3. 令牌必须单次使用或轮换；
4. 成功后旧令牌立即失效；
5. Sequence 从协商下一值继续；
6. 冲突 Channel 必须关闭；
7. 未确认副作用使用原幂等键重试；
8. 权限不得提升；
9. Auth Context 撤销时恢复失败。

## 17. Audit/1

EVENT：

```json
{
  "event_id": "018f2f89-bfd6-7fd4-b839-1123237c2cf9",
  "parent_event_ids": ["018f2f86-7a36-7c9e-a6cd-a7c7508048b4"],
  "actor_node_id": "urn:gfsip:node:inventory-service",
  "actor_domain_id": "urn:gfsip:domain:warehouse-a",
  "event_type": "operation.result",
  "rule_id": "inventory.reserve",
  "rule_version": "4.2.1",
  "state_before_hash": "sha256:...",
  "state_after_hash": "sha256:...",
  "evidence_hash": "sha256:...",
  "result_code": "RESERVED",
  "observed_at": "2026-07-16T10:00:00Z",
  "logical_clock": 8821
}
```

`parent_event_ids` 只表示直接声明的业务前驱：

- 时间更早不自动构成父事件；
- 网络先到不自动构成父事件；
- Trace ID 相同不自动构成父事件；
- 缺失父事件必须标记 unresolved；
- 自环和已知循环必须拒绝；
- 默认最大父事件数为 8。

签名覆盖：

```text
protocol_version
session_id
event_header_without_signature
payload_hash
```

签名有效只证明某密钥签署了该字节表示，不证明现实事件真实。

## 18. Federation/1

Domain Descriptor：

```json
{
  "domain_id": "urn:gfsip:domain:example-a",
  "descriptor_version": 12,
  "valid_from": "2026-07-16T00:00:00Z",
  "valid_until": "2026-07-23T00:00:00Z",
  "gateways": [{
    "uri": "gfsip://gateway.example-a.test:443",
    "transport": "quic",
    "priority": 10,
    "profiles": ["core/1", "audit/1", "federation/1"]
  }],
  "services": ["urn:gfsip:service:task-routing"],
  "trust_anchors": [{
    "key_id": "urn:gfsip:key:example-a:root-2026",
    "algorithm": "ed25519",
    "public_key": "base64url-public-key"
  }],
  "revocation_endpoints": [
    "https://example-a.test/.well-known/gfsip-revocations"
  ],
  "signature_algorithm": "ed25519",
  "signature": "base64url-signature"
}
```

规则：

- descriptor_version 单调递增；
- 过期描述符不得用于新信任；
- 描述符必须验签；
- 不规定全球唯一信任根；
- 单一公共目录不得成为本域通信前置条件；
- 跨域路由必须携带 visited_domains 和 max_hops；
- 检测到自身已在 visited_domains 中返回 `ROUTE_LOOP`；
- max_hops=0 返回 `ROUTE_HOP_LIMIT`。

## 19. PING、超时与关闭

- PONG 必须回显 probe_id；
- 超时只表示窗口内未响应，不等于永久故障；
- 副作用操作超时后重试保留原幂等键；
- GOAWAY 后不得创建新 Channel；
- 已有 Channel 可在 drain deadline 前完成。

## 20. 错误

ERROR：

```json
{
  "code": 1004,
  "name": "AUTH_FAILED",
  "scope": "session",
  "fatal": true,
  "retryable": false,
  "detail": "credential rejected"
}
```

- 数值 code 是线路稳定标识；
- name 仅用于诊断；
- Fatal Error 后必须关闭；
- detail 不得泄露密钥、令牌、凭据或敏感拓扑；
- 完整错误码见 `gfsip-error-registry.json`。

## 21. 默认资源限制

| 参数 | 默认 | 最大协商 |
|---|---:|---:|
| max_header | 32 KiB | 64 KiB |
| max_frame | 1 MiB | 16 MiB |
| max_channels | 128 | 65535 |
| max_inflight/channel | 64 | 4096 |
| max_parent_events | 8 | 64 |
| unauthenticated_lifetime | 10 s | 30 s |
| descriptor_size | 64 KiB | 1 MiB |
| route_max_hops | 8 | 32 |

实现必须限制未认证并发、签名验证预算、解压展开比例、路由结果数量和错误回复速率。

## 22. 压缩

- Core/1 必须支持 `none`；
- `zstd` 可选；
- 凭据、秘密令牌与攻击者可控文本不得共享压缩上下文；
- 超出展开限制返回 `DECOMPRESSION_LIMIT`。

## 23. 安全

攻击者被假定能够观察、延迟、重放、丢弃数据，建立恶意 Node，提交畸形帧、重复副作用操作、盗用过期令牌、诱导降级、构造路由循环和虚假审计事件。

实现 MUST：

- 使用批准的 TLS/QUIC 配置；
- 验证握手 transcript；
- 防止降级；
- 验证恢复令牌绑定、过期和轮换；
- 拒绝重复 Sequence；
- 执行副作用去重；
- 限制解析资源；
- 验证 Descriptor 签名和有效期；
- 不把签名有效等同于事实真实。

EARLY_DATA 只允许 PING 和明确可重放安全的只读查询。其他操作返回 `EARLY_DATA_REJECTED`。

## 24. 隐私

- EVENT 默认不记录 Payload 原文；
- 只记录最小必要元数据；
- 不把现实身份强制写入全局字段；
- Gateway 不得读取端到端加密业务载荷；
- 日志不得记录恢复令牌、凭据或私钥；
- 共享凭据只能锚定到凭据，不能锚定具体自然人。

## 25. 扩展与版本

1.x Minor 版本只能增加可忽略字段、协商后启用消息、可选 Profile 和错误码。

以下修改必须升级 Major：

- 改变 44-byte 帧头；
- 删除强制字段；
- 改变已有字段语义；
- 改变 Channel ID 规则；
- 改变 Sequence 语义；
- 改变签名规范化规则。

未知 `critical=true` 扩展触发 `UNSUPPORTED_CRITICAL_EXTENSION`。

## 26. 可观测性

建议指标：

```text
session_open_total
session_resume_total
session_resume_failed_total
channel_open_total
app_ack_latency_ms
duplicate_operation_total
auth_failed_total
protocol_error_total
route_loop_total
event_signature_failed_total
```

日志关联字段：

```text
session_id channel_id message_id event_id node_id domain_id error_code
```

## 27. 一致性声明

宣称 `GFSIP/1.0 Core Conformant` 必须：

1. 实现固定帧头；
2. 实现确定性 CBOR；
3. 支持 QUIC + `gfsip/1`；
4. 通过全部 Core Mandatory 测试；
5. 发布实现版本、配置摘要和测试报告；
6. 不存在已知未修复的 Critical 安全问题。

Audit/1 与 Federation/1 必须独立声明。

## 28. 最小测试向量

- 无共同版本 → `VERSION_UNSUPPORTED`；
- Initiator 创建偶数 Channel → `INVALID_CHANNEL_ID`；
- 相同幂等键提交两次 → 副作用计数为 1；
- 恢复令牌跨 Node 使用 → `RESUME_IDENTITY_MISMATCH`；
- 重复 Sequence → `SEQUENCE_REPLAY`；
- EVENT 以自身为父事件 → `CAUSAL_CYCLE`；
- 0-RTT 执行副作用 → `EARLY_DATA_REJECTED`；
- Descriptor 过期 → `DESCRIPTOR_EXPIRED`；
- visited_domains 已含本域 → `ROUTE_LOOP`。

完整测试见 `gfsip-conformance-checklist.csv`。

## 29. SPL 映射

| SPL | GFSIP 工程对象 |
|---|---|
| `E1 → E2` | 状态转换 |
| 因果机制 | Guard + Action |
| `Hᵢ` | 前置条件或不变量 |
| `若非 Hᵢ` | 负向测试 |
| 脆弱变量 A | 强制依赖 |
| `ΔD` | 可观测指标变化 |
| 责任单元 | 规范、代码、参数或测试签署者 |
| 信息黑洞 | 阻断发布的缺失输入 |

追踪链：

```text
设计理由 → 规范条款 → 状态机 → 字段 → 实现 → 测试 → 责任记录
```

## 30. 责任闭环

正式实现必须记录：

| 决策 | 最小责任单元 |
|---|---|
| 协议目标 | 签署目标声明者 |
| Wire Format | 批准帧头者 |
| 状态机 | 批准转换表者 |
| 安全配置 | 批准认证和参数者 |
| 默认限制 | 批准默认值者 |
| 参考实现 | 合并核心代码者 |
| 安全结论 | 签署安全报告者 |
| 一致性结论 | 签署测试报告者 |
| 发布 | 签署版本冻结者 |

无法区分时：

```text
[责任模糊区：集合{候选节点}内无法进一步区分]
```

## 31. v1.0 冻结项

1.x 中冻结：

- 44-byte 固定帧头；
- Session ID 语义；
- Sequence 语义；
- Channel 奇偶规则；
- 确定性 CBOR；
- `0x01`–`0x16` 消息语义；
- 恢复令牌身份绑定；
- 幂等去重规则；
- EVENT 直接父事件语义。

## 32. 已知限制

1. 双方都丢失持久状态时原 Session 不可恢复。
2. 去重受窗口和持久化可靠性限制。
3. 签名 EVENT 不证明现实事件真实。
4. 多信任根仍需域间信任政策。
5. Gateway 可拒绝互联。
6. 无替代物理路径时连接中断。
7. 共享凭据产生责任模糊区。
8. 尚无正式标准组织批准。
9. 尚无两个独立实现的公开互操作结果。
10. v1.0 表示规范冻结，不表示生态成熟。

## 33. 实施顺序

```text
Frame Codec
→ Session State Machine
→ QUIC Adapter
→ Authentication
→ Channel Manager
→ DATA / APP_ACK / Dedupe Store
→ Resume Service
→ Core Conformance
→ 第二独立实现
→ Audit/1
→ Federation/1
→ 安全审计与生产试点
```

## 34. 判定

```text
GFSIP/1.0 能实现：
跨域互操作、加密会话、多通道、会话恢复、
有限窗口去重、可选因果审计、多信任根、单域故障隔离。

GFSIP/1.0 不能实现：
全球单一控制、绝对零故障、无物理路径通信、
自动法律归责、无限时间 Exactly Once。
```
