# GFSIP：全球联邦稳定互操作协议
## Global Federated Stable Interoperability Protocol
### 协议草案 v0.1

- **状态**：实验性草案
- **协议层级**：应用层 / 会话层
- **基线承载**：QUIC
- **可选承载**：TCP + TLS 1.3、WebSocket + TLS 1.3
- **目标**：让不同组织、网络域、设备、服务和 AI Agent 在保持自治的前提下，实现可靠通信、会话恢复、去重执行、跨域验证和可选因果审计。
- **非目标**：替代 IP、统一全球控制权、承诺绝对不掉线、创造不存在的物理链路、提供通用“恰好一次”执行保证。

---

## 1. 规范语言

本规范中的 **MUST、MUST NOT、SHOULD、SHOULD NOT、MAY** 表示强制性等级：

- **MUST / MUST NOT**：实现必须遵守，否则不符合本规范。
- **SHOULD / SHOULD NOT**：实现只有在记录明确理由时才能偏离。
- **MAY**：实现可选能力。

---

## 2. 核心设计原则

1. **联邦而非中心化**  
   每个网络域独立管理身份、路由、服务和策略。协议不要求全球唯一控制机构。

2. **端到端增量部署**  
   核心协议运行在现有传输协议之上，不要求互联网中间设备原生识别 GFSIP。

3. **故障域隔离**  
   单个网络域、网关或信任根失效不得阻止其他网络域内部通信。

4. **明确状态机**  
   相同输入、相同状态和相同配置必须产生相同协议动作。

5. **应用级去重**  
   每个可产生副作用的操作必须携带幂等键。协议不宣称通用“恰好一次”。

6. **安全默认开启**  
   所有跨主机通信必须使用加密传输。禁止明文认证凭据。

7. **因果审计可选**  
   基础通信不强制携带完整因果图；高责任场景可启用审计配置。

---

## 3. 系统模型

### 3.1 实体

| 实体 | 定义 |
|---|---|
| Node | 实现 GFSIP 的设备、服务或 Agent |
| Domain | 由单一治理主体管理的自治网络域 |
| Gateway | 执行跨域发现、认证桥接和策略检查的节点 |
| Session | 两个节点之间可恢复的逻辑会话 |
| Channel | Session 内独立的逻辑通信流 |
| Event | 具有唯一标识、可选因果前驱和可验证结果的操作记录 |
| Domain Descriptor | 描述域标识、入口、能力、信任信息和有效期的签名文档 |

### 3.2 信任边界

```text
域 A 内部节点
    ↓ 本域认证
域 A 网关
    ↓ 跨域认证与策略检查
域 B 网关
    ↓ 本域授权
域 B 内部节点
```

GFSIP 不要求域 A 信任域 B 的全部身份体系。双方只需建立可验证的跨域信任桥。

---

## 4. 协议配置

### 4.1 Core Profile

所有兼容实现 MUST 支持：

- QUIC 承载
- 版本协商
- 双向身份认证接口
- 会话恢复
- 逻辑通道
- 消息标识与去重
- 心跳和优雅关闭
- 结构化错误
- 能力协商

### 4.2 Audit Profile

Audit Profile 在 Core Profile 上增加：

- 事件唯一标识
- 因果前驱引用
- 执行者身份
- 规则版本
- 操作前后状态摘要
- 证据摘要
- 审计记录签名

### 4.3 Federation Profile

Federation Profile 在 Core Profile 上增加：

- Domain Descriptor
- 跨域网关发现
- 多信任根
- 路由与服务策略
- 域级故障隔离
- 离线运行和恢复同步

---

## 5. 承载映射

### 5.1 QUIC

QUIC 是强制基线承载。

实现 MUST：

- 使用加密连接；
- 将 GFSIP 控制通道映射到单独的双向 QUIC stream；
- 将每个 GFSIP Channel 映射到一个或多个 QUIC stream；
- 使用 QUIC 原生流量控制和拥塞控制；
- 不自行实现与 QUIC 冲突的包级重传。

### 5.2 TCP + TLS

TCP + TLS 是可选兼容承载。

实现 MUST：

- 使用 TLS 1.3 或后续明确批准版本；
- 在单一字节流上使用本规范的长度前缀帧；
- 防止大帧导致内存耗尽；
- 实现通道级公平调度，降低队头阻塞影响。

### 5.3 WebSocket

WebSocket 映射仅用于受限环境。

每个 WebSocket 二进制消息 MUST 包含一个完整 GFSIP Frame，或使用长度前缀明确分隔多个 Frame。

---

## 6. 线路格式

### 6.1 字节序

所有整数使用网络字节序（big-endian）。

### 6.2 基础帧头

```text
0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                 Magic = "GFS1"                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Version Major | Version Minor | Type          | Flags         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Header Length                 | Payload Length                |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Payload Length (cont.)                  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
|                       Session ID (128 bit)                    |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                         Sequence (64 bit)                     |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                   Extension Header (variable)                 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                         Payload (variable)                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### 6.3 字段定义

| 字段 | 长度 | 规则 |
|---|---:|---|
| Magic | 4 bytes | 必须为 ASCII `GFS1` |
| Version Major | 1 byte | 破坏性版本 |
| Version Minor | 1 byte | 向后兼容版本 |
| Type | 1 byte | 消息类型 |
| Flags | 1 byte | 帧标志 |
| Header Length | 2 bytes | 扩展头长度，最大 65535 |
| Payload Length | 4 bytes | 载荷长度 |
| Session ID | 16 bytes | 会话标识；握手前全零 |
| Sequence | 8 bytes | 会话内单调递增序号 |
| Extension Header | variable | 规范化 CBOR Map |
| Payload | variable | 由消息类型定义 |

### 6.4 帧大小

- Core Profile 默认最大帧长：1 MiB。
- 实现 MUST 支持更低的本地限制。
- 对端发送超过协商限制的帧时，接收端 MUST 返回 `FRAME_TOO_LARGE` 并关闭相关通道。
- 文件和大型对象 MUST 分块发送。

### 6.5 Flags

| 位 | 名称 | 含义 |
|---:|---|---|
| 0 | ACK_REQUIRED | 需要应用级确认 |
| 1 | AUDIT_PRESENT | 扩展头包含审计字段 |
| 2 | END_CHANNEL | 发送方结束该通道 |
| 3 | IDEMPOTENT | 相同幂等键可安全重放 |
| 4 | COMPRESSED | 载荷已按协商算法压缩 |
| 5–7 | RESERVED | 必须为 0；接收端忽略未知保留位 |

---

## 7. 消息类型

| Type | 名称 | 用途 |
|---:|---|---|
| `0x01` | CLIENT_HELLO | 客户端版本和能力 |
| `0x02` | SERVER_HELLO | 服务端选择结果 |
| `0x03` | AUTH | 身份证明 |
| `0x04` | SESSION_READY | 会话建立完成 |
| `0x05` | RESUME | 请求恢复旧会话 |
| `0x06` | RESUME_RESULT | 恢复结果 |
| `0x07` | OPEN_CHANNEL | 创建逻辑通道 |
| `0x08` | CHANNEL_READY | 通道建立完成 |
| `0x09` | DATA | 传输业务数据 |
| `0x0A` | APP_ACK | 应用已接受处理 |
| `0x0B` | EVENT | 因果事件 |
| `0x0C` | PING | 活性探测 |
| `0x0D` | PONG | 活性响应 |
| `0x0E` | CAPABILITY_UPDATE | 能力变化 |
| `0x0F` | GOAWAY | 优雅停止接收新操作 |
| `0x10` | ERROR | 结构化错误 |
| `0x11` | DOMAIN_DESCRIPTOR | 域描述 |
| `0x12` | ROUTE_QUERY | 跨域服务查询 |
| `0x13` | ROUTE_RESULT | 路由查询结果 |
| `0x14` | STATE_SYNC | 恢复后的状态同步 |

---

## 8. 状态机

### 8.1 会话状态

```text
NEW
  ↓ CLIENT_HELLO / SERVER_HELLO
NEGOTIATING
  ↓ AUTH 成功
AUTHENTICATING
  ↓ SESSION_READY
ESTABLISHED
  ↘ 路径失效
   DEGRADED
     ↓ RESUME
   RESUMING
     ↓ RESUME_RESULT(success)
   ESTABLISHED
  ↓ GOAWAY
DRAINING
  ↓ 所有通道关闭
CLOSED
```

### 8.2 状态转换规则

| 当前状态 | 输入 | 条件 | 动作 | 下一状态 |
|---|---|---|---|---|
| NEW | CLIENT_HELLO | 格式有效 | 选择共同版本 | NEGOTIATING |
| NEGOTIATING | 无共同版本 | — | ERROR: VERSION_UNSUPPORTED | CLOSED |
| NEGOTIATING | AUTH | 版本已选择 | 验证身份 | AUTHENTICATING |
| AUTHENTICATING | 身份有效 | 授权通过 | SESSION_READY | ESTABLISHED |
| AUTHENTICATING | 身份无效 | — | ERROR: AUTH_FAILED | CLOSED |
| ESTABLISHED | 路径失效 | 恢复令牌存在 | 启动恢复 | DEGRADED |
| DEGRADED | RESUME | 令牌有效 | 对齐序号和状态摘要 | RESUMING |
| RESUMING | 同步完成 | 状态一致 | 恢复通道 | ESTABLISHED |
| 任意非 CLOSED | 致命协议错误 | — | ERROR | CLOSED |

### 8.3 强制不变量

1. 未进入 `ESTABLISHED` 前不得处理业务 `DATA`。
2. `Sequence` 在同一发送方向和同一 Session 内 MUST 单调递增。
3. 已接受的 `message_id` 在去重窗口内不得再次产生业务副作用。
4. 未认证节点不得打开需要授权的 Channel。
5. `GOAWAY` 后不得创建新 Channel。
6. `CLOSED` 状态不得处理除诊断日志外的任何输入。

---

## 9. 握手流程

```text
Client                                  Server
  |                                       |
  |--- CLIENT_HELLO --------------------->|
  |<-- SERVER_HELLO ----------------------|
  |--- AUTH ----------------------------->|
  |<-- AUTH ------------------------------|
  |<-- SESSION_READY ---------------------|
  |--- OPEN_CHANNEL --------------------->|
  |<-- CHANNEL_READY ---------------------|
  |--- DATA ----------------------------->|
```

### 9.1 CLIENT_HELLO 扩展头

```json
{
  "versions": ["1.0"],
  "profiles": ["core", "audit", "federation"],
  "transports": ["quic"],
  "compressions": ["none", "zstd"],
  "node_id": "urn:gfsip:node:example-client",
  "domain_id": "urn:gfsip:domain:example-a",
  "max_frame_size": 1048576,
  "max_channels": 128,
  "nonce": "base64url-random-32-bytes"
}
```

### 9.2 SERVER_HELLO 扩展头

```json
{
  "selected_version": "1.0",
  "selected_profiles": ["core", "audit"],
  "selected_compression": "none",
  "node_id": "urn:gfsip:node:example-server",
  "domain_id": "urn:gfsip:domain:example-b",
  "max_frame_size": 524288,
  "max_channels": 64,
  "nonce": "base64url-random-32-bytes"
}
```

### 9.3 版本选择

服务端 MUST 选择双方共同支持的最高 Major 版本及最高兼容 Minor 版本。

没有共同 Major 版本时，服务端 MUST 返回：

```json
{
  "code": "VERSION_UNSUPPORTED",
  "supported_versions": ["1.0"]
}
```

---

## 10. 身份与授权

### 10.1 节点身份

每个节点 MUST 拥有稳定的 `node_id`。推荐格式：

```text
urn:gfsip:node:<domain-controlled-identifier>
```

`node_id` 不是全球法律身份。它只表示由某一域或凭据签发者控制的协议身份。

### 10.2 支持的认证方式

Core Profile 实现 MUST 至少支持一种双向认证方式：

- 双向 TLS 证书；
- 基于外部身份系统的签名令牌；
- 预共享密钥，仅限封闭部署；
- 硬件身份凭据。

### 10.3 授权

认证成功不等于授权成功。

每个 `OPEN_CHANNEL` 和产生副作用的 `DATA` / `EVENT` 操作 MUST 经过策略检查。策略至少输入：

```text
node_id
domain_id
channel_type
operation
resource
session_security_level
```

---

## 11. Channel

### 11.1 OPEN_CHANNEL

```json
{
  "channel_id": 17,
  "channel_type": "task",
  "ordered": true,
  "delivery": "application_ack",
  "priority": 20,
  "max_inflight": 64,
  "metadata": {
    "service": "inventory.reserve"
  }
}
```

### 11.2 通道类型

预定义通道：

| 类型 | 用途 |
|---|---|
| `control` | 会话控制 |
| `message` | 普通消息 |
| `stream` | 连续数据 |
| `task` | 任务请求和结果 |
| `audit` | 审计事件 |
| `state-sync` | 恢复同步 |

自定义类型必须使用反向域名或 URN 命名，避免冲突。

---

## 12. 数据消息与去重

### 12.1 DATA 扩展头

```json
{
  "channel_id": 17,
  "message_id": "018f2f86-7a36-7c9e-a6cd-a7c7508048b4",
  "idempotency_key": "order-8842-reserve-v1",
  "content_type": "application/json",
  "deadline_ms": 5000
}
```

### 12.2 去重规则

1. 产生副作用的操作 MUST 携带 `idempotency_key`。
2. 接收方 MUST 在协商的去重窗口内保存结果。
3. 收到重复键时，接收方 MUST：
   - 不重复执行副作用；
   - 返回先前结果，或返回 `DUPLICATE_ACCEPTED`。
4. 去重窗口过期后，发送方不得假定旧键仍有效。
5. 实现不得对外宣称跨任意故障边界的通用“恰好一次”。

### 12.3 APP_ACK

```json
{
  "message_id": "018f2f86-7a36-7c9e-a6cd-a7c7508048b4",
  "status": "accepted",
  "result_hash": "sha256:...",
  "processed_at": "2026-07-16T10:00:00Z"
}
```

传输层确认只代表字节到达。`APP_ACK` 表示应用已接受该操作。

---

## 13. 会话恢复

### 13.1 恢复令牌

`SESSION_READY` 应返回不可伪造、短期有效的恢复令牌：

```json
{
  "session_id": "2f952c2d-7f80-4b3c-a61a-57d413ad39c9",
  "resume_token": "opaque-base64url-token",
  "expires_at": "2026-07-16T11:00:00Z",
  "dedupe_window_seconds": 3600
}
```

### 13.2 RESUME

```json
{
  "session_id": "2f952c2d-7f80-4b3c-a61a-57d413ad39c9",
  "resume_token": "opaque-base64url-token",
  "last_received_sequence": 9821,
  "open_channels": [3, 8, 17],
  "state_digest": "sha256:..."
}
```

### 13.3 恢复结果

| 结果 | 含义 |
|---|---|
| `resumed` | 原会话恢复 |
| `partial` | 部分通道需重新建立 |
| `new_session_required` | 恢复令牌失效或状态不可对齐 |
| `rejected` | 身份或策略拒绝 |

域或节点必须能够拒绝过期、重放或跨身份使用的恢复令牌。

---

## 14. 因果审计扩展

### 14.1 EVENT

Audit Profile 的 EVENT 扩展头：

```json
{
  "event_id": "018f2f89-bfd6-7fd4-b839-1123237c2cf9",
  "parent_event_ids": [
    "018f2f86-7a36-7c9e-a6cd-a7c7508048b4"
  ],
  "actor_node_id": "urn:gfsip:node:inventory-service",
  "actor_domain_id": "urn:gfsip:domain:warehouse-a",
  "rule_id": "inventory.reserve",
  "rule_version": "4.2.1",
  "state_before_hash": "sha256:...",
  "state_after_hash": "sha256:...",
  "evidence_hash": "sha256:...",
  "result_code": "RESERVED",
  "timestamp": "2026-07-16T10:00:00Z"
}
```

### 14.2 因果语义

- `parent_event_ids` 表示该事件在业务语义上直接依赖的前驱事件。
- 空数组表示没有已声明的业务前驱，不表示事件没有任何现实原因。
- 一个实现 MUST NOT 自动把时间先后关系当作因果关系。
- 审计记录必须区分：
  - 输入触发；
  - 授权决策；
  - 规则执行；
  - 外部副作用；
  - 结果确认。

### 14.3 状态摘要

状态摘要只证明某一字节表示的哈希值一致，不自动证明状态内容真实、完整或合法。

### 14.4 审计签名

高责任部署 SHOULD 对 EVENT 的规范化表示签名。签名字段：

```json
{
  "signature_algorithm": "profile-defined",
  "key_id": "urn:gfsip:key:inventory-service:2026-01",
  "signature": "base64url-signature"
}
```

---

## 15. 联邦网络

### 15.1 Domain Descriptor

```json
{
  "domain_id": "urn:gfsip:domain:example-a",
  "descriptor_version": 12,
  "valid_from": "2026-07-16T00:00:00Z",
  "valid_until": "2026-07-23T00:00:00Z",
  "gateways": [
    {
      "uri": "gfsip://gateway.example-a.test:443",
      "transport": "quic",
      "priority": 10
    }
  ],
  "services": [
    "urn:gfsip:service:task-routing",
    "urn:gfsip:service:audit-query"
  ],
  "trust_anchors": [
    {
      "key_id": "urn:gfsip:key:example-a:root-2026",
      "algorithm": "profile-defined",
      "public_key": "base64url-public-key"
    }
  ],
  "policy_uri": "https://example-a.test/.well-known/gfsip-policy",
  "signature": "base64url-signature"
}
```

### 15.2 多信任根

- GFSIP MUST NOT 规定全球唯一信任根。
- 每个域 MUST 明确配置接受的信任锚。
- 两个域之间可通过直接信任、桥接域或离线配置建立信任。
- 信任关系必须有有效期和撤销机制。

### 15.3 跨域路由

ROUTE_QUERY：

```json
{
  "target_service": "urn:gfsip:service:inventory.reserve",
  "required_profiles": ["core", "audit"],
  "source_domain": "urn:gfsip:domain:example-a",
  "constraints": {
    "region": "ap-northeast",
    "max_hops": 4
  }
}
```

ROUTE_RESULT：

```json
{
  "routes": [
    {
      "gateway_uri": "gfsip://gw.example-b.test:443",
      "target_domain": "urn:gfsip:domain:example-b",
      "profiles": ["core", "audit"],
      "expires_at": "2026-07-16T10:05:00Z"
    }
  ]
}
```

### 15.4 故障隔离

1. 跨域服务失效不得阻止本域服务发现。
2. 域必须能在外部目录不可用时使用缓存描述符。
3. 缓存过期后，域可按本地策略继续只读或离线运行。
4. 不得让单一全局目录成为所有通信的强制前置条件。

---

## 16. 活性、超时与优雅关闭

### 16.1 PING / PONG

PING：

```json
{
  "probe_id": "b193e635-8d84-4638-82c7-52d17ef5b279",
  "sent_at_monotonic_ns": 883928300
}
```

PONG 必须回显 `probe_id`。

### 16.2 超时

- 超时值必须通过配置或能力协商确定。
- 超时只表示在指定时间窗口内未获得所需响应。
- 超时不得自动被解释为对端永久故障。
- 产生副作用的操作在超时后重试时仍必须使用原幂等键。

### 16.3 GOAWAY

```json
{
  "last_accepted_channel_id": 88,
  "reason": "maintenance",
  "retry_after_ms": 30000
}
```

接收 GOAWAY 后：

- 不得创建更高编号的新 Channel；
- 已有 Channel 可继续到本地截止时间；
- 完成后关闭 Session。

---

## 17. 错误模型

### 17.1 错误结构

```json
{
  "code": "AUTH_FAILED",
  "scope": "session",
  "fatal": true,
  "related_message_id": null,
  "detail": "credential rejected",
  "retryable": false
}
```

### 17.2 核心错误码

| 错误码 | 范围 | 致命 | 含义 |
|---|---|---:|---|
| `MALFORMED_FRAME` | session | 是 | 帧无法解析 |
| `VERSION_UNSUPPORTED` | session | 是 | 无共同版本 |
| `AUTH_REQUIRED` | operation | 否 | 操作需要认证 |
| `AUTH_FAILED` | session | 是 | 身份验证失败 |
| `NOT_AUTHORIZED` | operation | 否 | 无操作权限 |
| `FRAME_TOO_LARGE` | channel | 可选 | 超出帧限制 |
| `CHANNEL_LIMIT` | session | 否 | 通道数达到上限 |
| `DUPLICATE_ACCEPTED` | operation | 否 | 重复操作已返回旧结果 |
| `STATE_CONFLICT` | session | 可选 | 恢复状态不一致 |
| `RESUME_EXPIRED` | session | 是 | 恢复令牌过期 |
| `RATE_LIMITED` | operation | 否 | 触发限流 |
| `INTERNAL_ERROR` | scope-defined | 可选 | 未分类内部错误 |
| `POLICY_REJECTED` | operation | 否 | 本地或跨域策略拒绝 |

错误文本不得包含密钥、访问令牌、完整凭据或敏感内部拓扑。

---

## 18. 资源与拒绝服务防护

实现 MUST：

- 限制握手并发数；
- 限制未认证会话寿命；
- 限制最大帧、最大通道和最大父事件数量；
- 在解析完整载荷前验证长度；
- 对审计签名验证设置计算预算；
- 对 ROUTE_QUERY 设置跳数和结果数上限；
- 对重复认证失败执行退避；
- 避免基于未验证输入执行无界内存分配。

建议默认值：

| 参数 | 默认值 |
|---|---:|
| 最大帧 | 1 MiB |
| 最大通道 | 128 |
| 最大父事件数 | 8 |
| 未认证会话寿命 | 10 秒 |
| Domain Descriptor 最大尺寸 | 64 KiB |
| 路由最大跳数 | 8 |
| 单次查询最大路由结果 | 32 |

---

## 19. 隐私

1. Audit Profile 不得默认记录业务载荷原文。
2. 应优先记录摘要、事件类型和最小必要元数据。
3. 跨域转发节点不得获得端到端加密业务载荷。
4. 日志保留时间必须由域策略明确规定。
5. 节点身份与现实自然人的映射必须由外部治理系统管理。
6. 协议不得把不可撤销的个人标识强制写入全局可见字段。

---

## 20. 版本与扩展

### 20.1 版本规则

- Major 版本变化可破坏兼容性。
- Minor 版本只允许增加可忽略字段、消息和能力。
- 接收方 MUST 忽略未知的可选扩展。
- 未知的强制扩展必须触发 `VERSION_UNSUPPORTED` 或专用扩展错误。

### 20.2 扩展命名

标准扩展：

```text
gfsip.<name>
```

私有扩展：

```text
<reverse-domain>.<name>
```

示例：

```text
com.example.robotics.safety-stop
```

### 20.3 注册表

稳定发布前应建立以下注册表：

- 消息类型
- Flags
- 错误码
- Channel 类型
- Profile 名称
- 扩展键
- 签名和摘要算法标识

---

## 21. 一致性要求

一个实现宣称兼容 Core Profile，必须通过：

1. 版本协商测试；
2. 双向认证测试；
3. 会话建立测试；
4. 通道建立和关闭测试；
5. 消息去重测试；
6. 超时后同幂等键重试测试；
7. 会话恢复测试；
8. 未知可选字段兼容测试；
9. 非法长度拒绝测试；
10. 优雅关闭测试。

宣称兼容 Audit Profile，还必须通过：

1. 多父事件解析；
2. 因果前驱缺失处理；
3. 签名验证失败处理；
4. 状态摘要不一致处理；
5. 审计记录规范化测试。

宣称兼容 Federation Profile，还必须通过：

1. Domain Descriptor 签名验证；
2. 描述符过期处理；
3. 多信任根；
4. 跨域策略拒绝；
5. 外部目录失效时的本域运行；
6. 路由循环和跳数限制。

---

## 22. 最小测试向量

### 22.1 共同版本

输入：

```json
{
  "client_versions": ["1.0", "2.0"],
  "server_versions": ["1.0", "1.1"]
}
```

期望：

```json
{
  "selected_version": "1.1",
  "next_state": "AUTHENTICATING"
}
```

### 22.2 无共同版本

输入：

```json
{
  "client_versions": ["2.0"],
  "server_versions": ["1.0", "1.1"]
}
```

期望：

```json
{
  "error": "VERSION_UNSUPPORTED",
  "next_state": "CLOSED"
}
```

### 22.3 去重执行

第一次输入：

```json
{
  "message_id": "m-1",
  "idempotency_key": "reserve-order-42",
  "operation": "reserve"
}
```

第二次输入：

```json
{
  "message_id": "m-2",
  "idempotency_key": "reserve-order-42",
  "operation": "reserve"
}
```

期望：

```json
{
  "side_effect_count": 1,
  "second_response": "DUPLICATE_ACCEPTED"
}
```

### 22.4 恢复令牌跨身份使用

输入：

```json
{
  "original_node_id": "urn:gfsip:node:a",
  "resume_node_id": "urn:gfsip:node:b",
  "token_valid": true
}
```

期望：

```json
{
  "resume": "rejected",
  "error": "AUTH_FAILED"
}
```

### 22.5 因果事件

输入：

```json
{
  "event_id": "e-3",
  "parent_event_ids": ["e-1", "e-2"],
  "rule_version": "4.2.1"
}
```

期望：

```json
{
  "accepted": true,
  "direct_parent_count": 2
}
```

不得从时间戳自动增加第三个父事件。

---

## 23. 参考处理伪代码

### 23.1 接收 DATA

```text
function handle_data(frame):
    require session.state == ESTABLISHED
    require frame.channel_id is open
    require frame.payload_length <= negotiated_max_frame

    authorize(frame.operation, session.identity)

    if operation_has_side_effect(frame):
        require frame.idempotency_key exists

        prior = dedupe_store.lookup(frame.idempotency_key)
        if prior exists:
            return APP_ACK(
                status = DUPLICATE_ACCEPTED,
                prior_result = prior.result
            )

    result = application.process(frame.payload)

    if operation_has_side_effect(frame):
        dedupe_store.commit(
            key = frame.idempotency_key,
            result = result,
            expiry = negotiated_dedupe_expiry
        )

    return APP_ACK(
        status = accepted,
        result_hash = hash(result)
    )
```

### 23.2 会话恢复

```text
function handle_resume(request):
    verify(request.resume_token)
    require token.node_id == authenticated_node_id
    require token.session_id == request.session_id
    require token.not_expired

    local_digest = compute_session_digest(request.session_id)

    if local_digest == request.state_digest:
        restore_channels(request.open_channels)
        return RESUME_RESULT(resumed)

    if partial_recovery_is_safe(request):
        return RESUME_RESULT(partial)

    return RESUME_RESULT(new_session_required)
```

---

## 24. 与 SPL / 因果审计引擎的映射

GFSIP 不要求网络专家阅读第二视角内部语言。SPL 引擎作为设计与审计的中间层，编译为标准协议对象：

| SPL 对象 | GFSIP 工程对象 |
|---|---|
| `E1 → E2` | 状态转换 |
| 因果机制 | 转换条件和处理动作 |
| `Hᵢ` | 前置条件或不变量 |
| `若非 Hᵢ` | 负向测试 |
| 脆弱变量 A | 强制依赖或单点故障 |
| `ΔD` | 可观测指标变化 |
| 责任单元 | 规范作者、参数批准者、代码提交者和测试签署者 |

推荐新增组件：

```text
CausalModelPlugin
    ↓
ProtocolSpecCompiler
    ↓
StateMachineGenerator
    ↓
TestVectorGenerator
    ↓
TraceabilityMatrixGenerator
```

每条强制规范必须能够回溯到：

```text
设计原因
→ 状态机规则
→ 线路字段
→ 参考实现代码
→ 一致性测试
→ 责任签署记录
```

---

## 25. 责任闭环

正式发布时必须建立不可分拆责任记录：

| 节点 | 最小责任单元 |
|---|---|
| 协议目标 | 签署目标声明的自然人 |
| Wire Format | 批准字段冻结的规范编辑者 |
| 状态机 | 批准状态转换表的技术负责人 |
| 安全配置 | 批准认证和算法配置的安全负责人 |
| 默认参数 | 批准资源和超时默认值的参数负责人 |
| 参考实现 | 合并核心代码的维护者 |
| 测试结论 | 签署一致性报告的测试负责人 |
| 发布版本 | 签署版本冻结决议的发布负责人 |

无法区分时必须记录：

```text
[责任模糊区：集合{候选责任节点}内无法进一步区分]
```

---

## 26. 生产发布门槛

v1.0 之前必须满足：

- 至少两个无共同代码来源的独立实现；
- Core Profile 强制测试通过率 100%；
- 未解决的严重安全缺陷数为 0；
- 至少三个相互独立的生产试点域；
- 单域故障不影响其他试点域内部通信；
- 会话恢复测试覆盖网络切换、进程重启和网关切换；
- 所有强制字段具有明确解析和错误处理规则；
- 公开规范、测试向量、变更记录和已知限制。

---

## 27. 已知限制

1. GFSIP 不提供全球政治或法律治理。
2. 多信任根会产生策略冲突，需要域级配置解决。
3. 会话恢复不能在双方都丢失状态时恢复原状态。
4. 幂等键只能在接收方保留窗口内防止重复副作用。
5. 审计记录只能证明记录与签名之间的一致性，不能单独证明现实事件真实性。
6. 中间网络完全断开且无替代路径时，协议无法保持连接。
7. 不同域可以拒绝互联，因此协议只能保证兼容接口，不能强制全球连通。
8. 本草案没有经过正式标准组织批准，不得对外宣称为国际标准。

---

## 28. 初始实现路线

### M0：规范可执行化

- 固定 Core Profile
- 编写二进制编解码器
- 实现状态机
- 生成基础测试向量

### M1：双实现互操作

- Rust 实现 A
- Go 或 Python 实现 B
- 交叉握手、Channel、去重和恢复测试

### M2：Audit Profile

- EVENT 规范化
- 事件签名
- 因果图导出
- SPL 引擎映射

### M3：Federation Profile

- Domain Descriptor
- 跨域网关
- 多信任根
- 故障隔离测试

### M4：生产试点

- AI Agent 协作
- IoT / 边缘设备
- 高责任企业工作流

---

## 29. 草案判定

```text
本协议能够实现：
跨域互操作
会话自动恢复
多信任根
故障隔离
消息去重
可选因果审计

本协议不能实现：
全球单一控制
绝对零故障
无物理链路通信
自动法律归责
任意场景的恰好一次执行
```

---

## 附录 A：最小合规清单

```text
[ ] 支持 QUIC 承载
[ ] 支持 1.0 版本协商
[ ] 支持双向认证
[ ] 支持会话恢复
[ ] 支持 Channel
[ ] 支持 message_id
[ ] 副作用操作支持 idempotency_key
[ ] 支持 APP_ACK
[ ] 支持结构化 ERROR
[ ] 限制最大帧和通道数
[ ] 通过非法帧测试
[ ] 通过重复操作测试
[ ] 通过恢复令牌跨身份拒绝测试
[ ] 提供公开测试结果
```

## 附录 B：文件标识

```text
Document: GFSIP Protocol Draft
Version: 0.1
Status: Experimental
Date: 2026-07-16
Primary language: Chinese
Normative profile: Core
Optional profiles: Audit, Federation
```
