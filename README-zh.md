<p align="center">
  <img src="https://img.shields.io/badge/gfsip-protocol-D4AF37?style=flat-square" alt="gfsip-protocol">
  <img src="https://img.shields.io/badge/version-v1.0-D4AF37?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/federated-stable-D4AF37?style=flat-square" alt="federated-stable">
  <img src="https://img.shields.io/badge/audit--native-D4AF37?style=flat-square" alt="audit-native">
</p>

<blockquote align="center">
  <em>GFSIP v1.0 —— 带因果审计的联邦稳定互操作协议</em>
</blockquote>

<p align="center">
[English](README.md) | 简体中文
</p>

<div style="max-width:880px;margin:0 auto;padding:0 16px">

## ✦ 关于

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">
<strong>安塔瑞斯（Antares）</strong>——全球联邦稳定互操作协议（Global Federated Stable Interoperability Protocol，GFSIP）v1.0。
</p>

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">
GFSIP 是一种面向数字资产、身份与服务的联邦互操作协议，核心由三层构成：价值协议层（<code>GFSIP-VAL</code>，稳定锚定 + 储备证明）、身份协议层（<code>GFSIP-ID</code>，去中心化身份 + 可验证凭证）、服务协议层（<code>GFSIP-SVC</code>，服务发现与跨域调用）。它以 <strong>储备证明</strong> 为价值锚点，以 <strong>去中心化身份</strong> 为信任根，以 <strong>因果审计</strong> 为合规骨架，构建一个可审计、可验证、可互操作的全球联邦网络。
</p>

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">
协议原生集成 <strong>因果审计</strong>——每一次跨域操作都可追溯、可验证、可追责。它不仅仅是技术协议，更是一套治理框架：治理委员会、技术委员会、审计委员会三权分立，确保协议演进的透明与可信。
</p>

</div>

<p align="center">— ✦ —</p>

## ✦ 核心思想

<div style="max-width:880px;margin:0 auto;padding:0 16px">

- **联邦而非联盟** —— 不设中心机构，各参与方平等自治，通过协议达成共识。
- **稳定而非波动** —— 价值锚定于真实储备，通过储备证明与公开审计确保可信度。
- **互操作而非孤岛** —— 身份、资产、服务在联邦内自由流动，无需各系统两两对接。
- **可审计而非黑盒** —— 因果审计内生于协议，每一步都可追溯、可验证、可追责。
- **隐私优先而非事后补救** —— 最小披露、零知识证明、选择性披露，隐私从设计上即内建。
- **治理而非人治** —— 三权分立的治理结构，协议变更需多方参与、公开透明。

</div>

<p align="center">— ✦ —</p>

## ✦ 协议架构

```
┌─────────────────────────────────────────────────────┐
│                   治理层（Governance）                │
│    治理委员会  ·  技术委员会  ·  审计委员会            │
├─────────────────────────────────────────────────────┤
│                   服务协议层（GFSIP-SVC）             │
│    服务注册 / 发现  ·  跨域调用  ·  计费与结算         │
├─────────────────────────────────────────────────────┤
│                   身份协议层（GFSIP-ID）              │
│    DID  ·  可验证凭证  ·  身份钱包  ·  信任根          │
├─────────────────────────────────────────────────────┤
│                   价值协议层（GFSIP-VAL）             │
│    稳定资产  ·  储备证明  ·  原子交换  ·  跨链桥接      │
├─────────────────────────────────────────────────────┤
│                   因果审计层（Causal Audit）          │
│    叙事剥离  ·  假设透视  ·  脆弱性锁存  ·  状态锚定    │
├─────────────────────────────────────────────────────┤
│                   传输与密码学层                       │
│    mTLS / QUIC  ·  签名  ·  加密  ·  ZKP              │
└─────────────────────────────────────────────────────┘
```

<p align="center">— ✦ —</p>

## ✦ 规范文档

所有正式规范位于 [`specs/`](specs/) 目录：

| 编号 | 名称 | 说明 |
|---|---|---|
| GFSIP-CORE-001 | `core-terminology.md` | 核心术语与定义 |
| GFSIP-CORE-002 | `core-architecture.md` | 总体架构与设计原则 |
| GFSIP-VAL-001 | `val-stable-asset.md` | 稳定资产规范 |
| GFSIP-VAL-002 | `val-reserve-proof.md` | 储备证明机制 |
| GFSIP-VAL-003 | `val-atomic-swap.md` | 原子交换协议 |
| GFSIP-VAL-004 | `val-cross-chain-bridge.md` | 跨链桥接规范 |
| GFSIP-ID-001 | `id-did-method.md` | DID 方法规范 |
| GFSIP-ID-002 | `id-verifiable-credential.md` | 可验证凭证规范 |
| GFSIP-ID-003 | `id-trust-root.md` | 信任根与治理 |
| GFSIP-SVC-001 | `svc-discovery.md` | 服务发现协议 |
| GFSIP-SVC-002 | `svc-cross-domain-call.md` | 跨域服务调用 |
| GFSIP-SVC-003 | `svc-billing-settlement.md` | 计费与结算 |
| GFSIP-AUD-001 | `aud-causal-audit.md` | 因果审计规范 |
| GFSIP-AUD-002 | `aud-proof-of-reserve.md` | 储备审计流程 |
| GFSIP-GOV-001 | `gov-structure.md` | 治理结构 |
| GFSIP-GOV-002 | `gov-proposal-process.md` | 提案与表决流程 |
| GFSIP-SEC-001 | `sec-cryptography-primitives.md` | 密码学原语与算法 |
| GFSIP-SEC-002 | `sec-threat-model.md` | 威胁模型与安全边界 |

<p align="center">— ✦ —</p>

## ✦ 参考实现

`ref-impl/` 目录包含 v1.0 规范的参考实现（Python，仅作学习与验证，非生产级）：

| 文件 | 说明 |
|---|---|
| `ref_impl/stable_asset.py` | 稳定资产发行 / 赎回 / 转账 + 储备金校验 |
| `ref_impl/reserve_proof.py` | 默克尔树储备证明生成与验证（含负债证明） |
| `ref_impl/did_gfsip.py` | `did:gfsip:` 方法的 DID 文档生成 / 解析 / 密钥轮换 |
| `ref_impl/vc.py` | 可验证凭证签发 / 验证 + 选择性披露（JSON-LD + 默克尔证明） |
| `ref_impl/atomic_swap.py` | HTLC 哈希时间锁原子交换（发起 / 接受 / 完成 / 回退） |
| `ref_impl/cross_chain_bridge.py` | 联邦门限签名跨链桥（锁定 / 铸造 / 燃烧 / 释放） |
| `ref_impl/service_discovery.py` | 联邦服务注册表（注册 / 发现 / 健康检查 + 签名验证） |
| `ref_impl/cross_domain_call.py` | 跨域服务调用（请求签名 / 响应验证 / 幂等 / 审计） |
| `ref_impl/billing_settlement.py` | 计费与结算（计量 / 对账 / 结算 / 争议处理） |
| `ref_impl/causal_audit.py` | 因果审计日志（叙事剥离 / 假设透视 / 脆弱性锁存 / 状态锚定） |
| `ref_impl/crypto_utils.py` | 密码学工具（Ed25519 / SHA-256 / 默克尔树） |
| `ref_impl/governance.py` | 治理委员会（提案 / 表决 / 执行 + 法定人数） |
| `ref_impl/demo.py` | 端到端演示：价值发行 → 身份凭证 → 服务发现 → 跨域调用 → 审计 |

### 运行演示

```bash
cd ref_impl
pip install pynacl     # 可选：Ed25519 签名加速（未安装时自动回退到 Python 内建）
python demo.py
```

演示流程：GFSIP 储备金初始化 → 稳定资产发行 → DID 创建 → 可验证凭证签发 → 服务注册与发现 → 跨域服务调用 → 因果审计链验证 → 原子交换 → 治理提案。

<p align="center">— ✦ —</p>

## ✦ 状态

- **v1.0** —— 协议规范定稿，参考实现完成。
- 治理结构与审计流程已定义。
- 密码学原语与威胁模型文档已发布。
- 储备证明机制（默克尔树）在参考实现中验证通过。

<p align="center">— ✦ —</p>

## ✦ 生态

Antares 是 NOHN AI 生态的一员 —— 围绕第二视角因果审计与确定性执行构建的项目家族：

| 项目 | 仓库 | 定位 |
|---|---|---|
| **Second-Perspective (GCAE)** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective) | 全球认知审计引擎 —— 五算子因果审计核心（IMDA 95/100） |
| **NOMOS** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective)（`Intelligent-Decision-Hub--Nomos` 分支） | 可审计确定性决策中心（IMDA 95/100） |
| **SPL-G1** | [nohn3043-arch/SPL-G1](https://github.com/nohn3043-arch/SPL-G1) | 硬件因果审计可信计算单元（TCU） |
| **SPL-Virtual-World-Base** | [nohn3043-arch/Second-Reality](https://github.com/nohn3043-arch/Second-Reality) | 虚拟世界与元宇宙基础设施（宪法 / 法律 / 桥梁） |
| **Story-Engine** | [nohn3043-arch/story-engine](https://github.com/nohn3043-arch/story-engine) | 长篇叙事一致性引擎 |
| **Antares** | [nohn3043-arch/Antares](https://github.com/nohn3043-arch/Antares) | GFSIP v1.0 —— 带因果审计的联邦稳定互操作协议 |
| **Anthropomorphic-Agent-Engine** | [nohn3043-arch/Anthropomorphic-Agent-Engine](https://github.com/nohn3043-arch/Anthropomorphic-Agent-Engine) | 确定性拟人心理学引擎（SPL Pure Core V8.0） |
| **PAGES** | [nohn3043-arch/pages](https://github.com/nohn3043-arch/pages) | NOHN AI 生态官方落地页 |

<p align="center">— ✦ —</p>

## ✦ 许可与授权

本仓库 **不是开源软件**。双轨模式：个人非商业研究免费；政府 / 企业使用需付费商业许可。详见 [LICENSE](./LICENSE)。

| 用户 | 用途 | 许可要求 |
|---|---|---|
| 个人（自然人） | 非商业学术研究 / 学习 / 个人实验 | **免费**，依据 [LICENSE](./LICENSE) 中「个人免费研究许可」 |
| 政府机构 / 事业单位 / 企业 | 任何用途（含内部部署、产品开发、服务提供） | **必须事先签署付费商业许可** |

- **个人研究者** 可免费用于非商业研究，但不得用于任何商业目的，也不得向任何企业或政府机构提供服务。
- **政府 / 企业用户** 在签署商业许可协议并支付约定费用前，不得复制、部署、运行、集成或分发本作品。
- **许可申请**：国际 / 全球 — [ai@nohnlins.com](mailto:ai@nohnlins.com) · 中国 — [lin@secondai.top](mailto:lin@secondai.top)

许可方、适用法律与争议解决依用户所在地按 [LICENSE](./LICENSE) 执行：中国境内 → 上海林明钧华科技有限公司（适用中国法律）；中国境外 → NOHN AI TECHNOLOGY PTE. LTD.（适用新加坡法律，SIAC 仲裁）。

<p align="center">
  <a href="https://github.com/nohn3043-arch">GitHub</a>
  &nbsp;·&nbsp;
  <a href="https://www.nohnlins.com/">nohnlins.com</a>
  &nbsp;·&nbsp;
  <a href="mailto:ai@nohnlins.com">ai@nohnlins.com</a>
</p>
<p align="center"><sub>NOHN AI · ANTARES · GFSIP v1.0</sub></p>
