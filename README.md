

# ANTARES - GFSIP v1.0 全球联邦稳定互操作协议

<div align="center">

![ANTARES Banner](assets/banner.svg)

**GFSIP/1.0: Global Federated Stable Interoperability Protocol**

[![protocol-D4AF37](https://img.shields.io/badge/protocol-D4AF37?style=flat-square)](https://gitee.com/nohn-ecosystem/antares)
[![quic-D4AF37](https://img.shields.io/badge/quic-D4AF37?style=flat-square)](https://gitee.com/nohn-ecosystem/antares)
[![federation-D4AF37](https://img.shields.io/badge/federation-D4AF37?style=flat-square)](https://gitee.com/nohn-ecosystem/antares)

*全球联邦稳定互操作协议 v1.0*

</div>

---

## ✦ 项目简介

ANTARES 是 **GFSIP v1.0（全球联邦稳定互操作协议）** 的开源实现。该协议为服务、AI 代理、设备和组织提供加密、多通道、可恢复的跨域通信，无需中心化权威机构即可实现安全互联。

### 核心技术特点

| 特性 | 说明 |
|------|------|
| **传输层** | 强制使用 QUIC 协议（ALPN: `gfsip/1`） |
| **数据编码** | 确定性 CBOR（big-endian，最短编码） |
| **帧结构** | 44 字节固定头部 + 扩展头 |
| **消息类型** | 18 种标准消息类型（`0x01`-`0x16`） |
| **会话恢复** | 支持网络切换后无需重新认证 |
| **幂等去重** | 基于幂等键的有限窗口去重机制 |
| **因果审计**（可选） | 带因果前因的签名事件记录 |
| **联邦路由**（可选） | 多信任锚的跨域路由 |

---

## ✦ 核心能力

| # | 能力 | 描述 |
|---|------|------|
| 1 | **加密会话** | 基于 QUIC 的双向 TLS 或令牌认证会话 |
| 2 | **多通道** | 单会话内独立逻辑通道 |
| 3 | **会话恢复** | 网络切换时无需重新认证即可恢复会话 |
| 4 | **幂等副作用** | 通过幂等键实现有限窗口去重 |
| 5 | **因果审计**（可选） | 带因果前因的签名事件记录 |
| 6 | **跨域联邦** | 多信任锚路由及签名域描述符 |
| 7 | **故障隔离** | 单域故障不影响域内通信 |

---

## ✦ 协议架构

### 协议层次

```
+----------------------------------+
|         应用层 (Application)      |
+----------------------------------+
|      联邦路由 (Federation/1)      |  ← 可选
+----------------------------------+
|       因果审计 (Audit/1)          |  ← 可选
+----------------------------------+
|     会话/通道管理 (Core/1)        |  ← 必需
+----------------------------------+
|     确定性 CBOR 编码层            |
+----------------------------------+
|      QUIC 传输层 (必需)           |
+----------------------------------+
```

### 消息类型概览

| 类型码 | 消息类型 | 作用 |
|--------|----------|------|
| `0x01` | CLIENT_HELLO | 握手起始 |
| `0x02` | SERVER_HELLO | 握手响应 |
| `0x03` | AUTH | 认证凭证 |
| `0x04` | AUTH_RESULT | 认证结果 |
| `0x05` | SESSION_READY | 会话就绪 |
| `0x06` | OPEN_CHANNEL | 打开通道 |
| `0x07` | CHANNEL_READY | 通道就绪 |
| `0x08` | DATA | 数据传输 |
| `0x09` | APP_ACK | 应用确认 |
| `0x0A` | CHANNEL_CLOSE | 通道关闭 |
| `0x0B` | SESSION_CLOSE | 会话关闭 |
| `0x0C` | SESSION_RECOVERY | 会话恢复 |
| `0x0D` | RESUME_TOKEN | 恢复令牌 |
| `0x0E` | RESUME_REQUEST | 恢复请求 |
| `0x0F` | RESUME_RESPONSE | 恢复响应 |
| `0x10` | HEARTBEAT | 心跳检测 |
| `0x11` | HEARTBEAT_ACK | 心跳响应 |
| `0x12` | ERROR | 错误通知 |

---

## ✦ 项目内容

| 文件/目录 | 说明 |
|-----------|------|
| `GFSIP_v1.0_protocol_spec.md` | 完整协议规范（34 个章节） |
| `gfsip-state-machine.json` | 机器可读状态机定义 |
| `gfsip-message-schema.json` | 消息 JSON Schema |
| `gfsip-error-registry.json` | 错误码注册表 |
| `gfsip-conformance-checklist.csv` | 一致性测试清单 |
| `gfsip-traceability-matrix.csv` | 需求追踪矩阵 |
| `reference-impl/` | Python 参考实现 |

### Python 参考实现模块

| 模块 | 功能 |
|------|------|
| `audit.py` | 因果审计事件记录与验证 |
| `auth.py` | 认证与授权机制 |
| `channel.py` | 通道生命周期管理 |
| `conformance.py` | 一致性测试用例 |
| `dedupe.py` | 幂等去重存储 |
| `endpoint.py` | 协议端点核心实现 |
| `federation.py` | 跨域联邦路由 |
| `frame.py` | 帧编解码器 |
| `resume.py` | 会话恢复服务 |
| `state_machine.py` | 会话状态机 |
| `transport.py` | QUIC 传输抽象层 |
| `types.py` | 类型定义与枚举 |
| `cbor_utils.py` | CBOR 编码工具 |

---

## ✦ 快速开始

### 环境要求

- Python 3.10+
- pip

### 安装与运行

```bash
# 克隆项目
git clone https://gitee.com/nohn-ecosystem/antares.git
cd antares/reference-impl

# 安装依赖
pip install -r requirements.txt

# 运行端到端演示
python demo.py
# 输出: 握手 → 通道建立 → 数据传输 → 去重测试 → 恢复测试

# 运行一致性测试
python -m gfsip.conformance
# 输出: 10 个一致性向量测试结果
```

### 演示流程说明

`demo.py` 执行以下完整流程：

1. **握手建立** - 双向认证
2. **通道管理** - 打开逻辑通道
3. **数据传输** - 发送数据帧
4. **幂等测试** - 重复消息去重
5. **恢复测试** - 跨节点会话恢复

---

## ✦ 协议配置

### Core/1（必需）

- QUIC 传输与版本协商
- 双向认证
- 会话与通道管理
- 会话恢复
- 结构化错误处理
- 优雅关闭

### Audit/1（可选）

- 带因果前因的签名事件
- 参与者身份标识
- 规则版本声明
- 状态前后哈希
- 自环与已知环检测

### Federation/1（可选）

- 签名 `DomainDescriptor` 跨域路由
- 多信任锚配置
- 描述符过期与撤销
- 故障隔离

---

## ✦ 应用场景

| 场景 | 用途 |
|------|------|
| **AI 代理网络** | 跨组织多代理任务协调与可审计轨迹 |
| **企业集成** | 无中心权威的跨组织工作流编排 |
| **IoT/Edge** | 设备与云端的跨网络会话恢复 |
| **金融合规** | 监管报告签名因果审计轨迹 |
| **医疗健康** | 联邦数据交换与域级策略执行 |
| **机器人学** | 幂等安全操作的可靠命令通道 |

---

## ✦ 项目状态

| 里程碑 | 状态 |
|--------|------|
| 规范 v1.0（接口冻结） | ✅ 完成 |
| 机器可读状态机与 Schema | ✅ 完成 |
| Python 参考实现（10/10 一致性） | ✅ 完成 |
| 独立第二实现 | 🔲 进行中 |
| 公开互操作性报告 | 🔲 待定 |
| 生产试点域 | 🔲 待定 |

---

## ✦ 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/xxx`)
3. 提交更改 (`git commit -am 'Add feature xxx'`)
4. 推送分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

### 实现建议

- 参考 `conformance.py` 确保一致性
- 遵循 `gfsip-state-machine.json` 状态转移规则
- 使用 `gfsip-message-schema.json` 验证消息格式
- 运行 `python -m gfsip.conformance` 验证实现

---

## ✦ 许可证

本项目采用 MIT License - 详见 LICENSE 文件。

---

## ✦ 联系方式

- **项目地址**: https://gitee.com/nohn-ecosystem/antares
- **组织**: NOHN AI
- **邮箱**: ai@nohnlins.com
- **官网**: https://www.nohnlins.com/

---

<div align="center">

*NOHN AI · ANTARES · GFSIP v1.0*

</div>