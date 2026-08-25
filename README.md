<p align="center">
  <img src="assets/banner.svg" alt="ANTARES banner" style="width:100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/protocol-D4AF37?style=flat-square" alt="protocol">
  <img src="https://img.shields.io/badge/quic-D4AF37?style=flat-square" alt="quic">
  <img src="https://img.shields.io/badge/federation-D4AF37?style=flat-square" alt="federation">
  <img src="https://img.shields.io/badge/gfsip-v1.0-D4AF37?style=flat-square" alt="gfsip-v1.0">
</p>

<blockquote align="center">
  <em>全球联邦稳定互操作协议 GFSIP v1.0</em>
</blockquote>

<div style="max-width:880px;margin:0 auto;padding:0 16px">

## ✦ 关于

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">ANTARES 即 GFSIP v1.0——全球联邦稳定互操作协议。为服务、AI 智能体、设备与组织提供加密、多通道、可恢复的跨域通信，无需中央权威。以 QUIC 为强制传输层、确定性 CBOR 序列化，内置会话恢复、幂等去重与因果审计，作为去中心化网络的稳定基座。</p>

<p align="center">
  <img src="assets/overview.svg" alt="ANTARES overview" style="width:100%">
</p>

</div>

<p align="center">— ✦ —</p>

## ✦ 核心能力

<div style="max-width:880px;margin:0 auto;padding:0 16px">

<table style="width:100%;border-collapse:collapse;font-size:14px">
  <tr><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">#</th><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">能力</th><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">说明</th></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">1</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>加密会话</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">QUIC 上互认证 TLS 或令牌认证会话</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">2</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>多通道</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">单会话内独立逻辑通道</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">3</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>会话恢复</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">网络切换后免重新认证恢复会话</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">4</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>幂等副作用</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">幂等键限窗去重</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">5</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>因果审计（可选）</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">带声明因果前驱的签名事件记录</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">6</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>跨域联邦</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">多信任锚路由 + 签名域描述符</td></tr>
  <tr><td style="padding:8px">7</td><td style="padding:8px"><strong>故障隔离</strong></td><td style="padding:8px">单域故障不阻塞域内流量</td></tr>
</table>

</div>

<p align="center">— ✦ —</p>

## ✦ 线路格式

<div style="max-width:880px;margin:0 auto;padding:0 16px">

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">GFSIP 在 QUIC 之上使用 <strong>44 字节定长头</strong>，ALPN <code style="background:#F5F0E6;padding:2px 6px;border-radius:3px;color:#C9A96E">gfsip/1</code>。扩展头使用确定性 CBOR（大端、最短编码）。18 种标准消息类型（<code>0x01</code>–<code>0x16</code>）覆盖完整生命周期：握手、通道管理、数据传输、会话恢复、审计事件、联邦路由。</p>

</div>

<p align="center">— ✦ —</p>

## ✦ 仓库内容

<div style="max-width:880px;margin:0 auto;padding:0 16px">

<table style="width:100%;border-collapse:collapse;font-size:14px">
  <tr><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">文件</th><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">用途</th></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><code>GFSIP_v1.0_protocol_spec.md</code></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">完整协议规范（33 节）</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><code>gfsip-state-machine.json</code></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">机器可读状态机定义</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><code>gfsip-message-schema.json</code></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">逻辑消息 JSON Schema</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><code>gfsip-error-registry.json</code></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">数字错误码注册表</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><code>gfsip-conformance-checklist.csv</code></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">一致性测试清单</td></tr>
  <tr><td style="padding:8px"><code>reference-impl/</code></td><td style="padding:8px">Python 参考实现——帧编解码、状态机、通道管理、认证、去重、恢复、审计、联邦、端到端演示（9/9 一致性向量通过）</td></tr>
</table>

</div>

<p align="center">— ✦ —</p>

## ✦ 协议画像

<div style="max-width:880px;margin:0 auto;padding:0 16px">

<p style="font-size:15px;line-height:1.8;color:#2C2C2C"><strong style="color:#C9A96E">Core/1（强制）</strong>——QUIC 传输、版本协商、互认证、会话与通道管理、会话恢复、结构化错误、优雅关闭。</p>

<p style="font-size:15px;line-height:1.8;color:#2C2C2C"><strong style="color:#C9A96E">Audit/1（可选）</strong>——带声明因果前驱、行为者身份、规则版本与状态前后哈希的签名因果事件记录；拒绝自环与已知环。</p>

<p style="font-size:15px;line-height:1.8;color:#2C2C2C"><strong style="color:#C9A96E">Federation/1（可选）</strong>——经签名 <code>DomainDescriptor</code> 对象的跨域路由、多信任锚配置、描述符过期 / 撤销与故障隔离。</p>

</div>

<p align="center">— ✦ —</p>

## ✦ 快速开始

```bash
# 安装 SDK（PyPI）
pip install gfsip

# 运行端到端演示（clone 仓库获取 demo.py）
git clone https://github.com/nohn3043-arch/Antares.git
cd Antares/reference-impl
pip install -r requirements.txt
python demo.py                # 端到端演示：握手 → 通道 → 数据 → 去重 → 恢复
python gfsip/conformance.py   # 9/9 第 28 节最小一致性向量——全部通过
```

<p align="center">— ✦ —</p>

## ✦ 应用场景

<div style="max-width:880px;margin:0 auto;padding:0 16px">

- **AI 智能体网络**——跨组织边界的多智能体任务协同，带可审计痕迹
- **企业集成**——无需中央权威的跨组织工作流编排
- **IoT / 边缘**——网络切换下的设备到云会话恢复
- **金融 / 合规**——面向监管报告的签名因果审计链
- **医疗健康**——带域级策略执行的联邦数据交换
- **机器人**——幂等安全操作的可靠命令通道

</div>

<p align="center">— ✦ —</p>

## ✦ 项目状态

<div style="max-width:880px;margin:0 auto;padding:0 16px">

<table style="width:100%;border-collapse:collapse;font-size:14px">
  <tr><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">里程碑</th><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">状态</th></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">规范 v1.0（接口冻结）</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">✅ 完成</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">机器可读状态机与模式</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">✅ 完成</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">Python 参考实现（9/9 一致性）</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">✅ 完成</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">独立第二实现</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">🔲 进行中</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">公开互操作报告</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">🔲 待办</td></tr>
  <tr><td style="padding:8px">生产试点域</td><td style="padding:8px">🔲 待办</td></tr>
</table>

</div>

<p align="center">— ✦ —</p>

## ✦ 生态

ANTARES 是 NOHN AI 生态的一员——围绕第二视角因果审计与确定性执行构建的项目家族：

| 项目 | 仓库 | 定位 |
|---|---|---|
| **Second-Perspective (GCAE)** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective) | 全局认知审计引擎——五算子因果审计内核（IMDA 95/100） |
| **NOMOS** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective)（`Intelligent-Decision-Hub--Nomos` 分支） | 可审计确定性决策中心（IMDA 95/100） |
| **SPL-G1** | [nohn3043-arch/SPL-G1](https://github.com/nohn3043-arch/SPL-G1) | 硬件因果审计可信计算单元（TCU） |
| **SPL-Virtual-World-Base** | [nohn3043-arch/Second-Reality](https://github.com/nohn3043-arch/Second-Reality) | 虚拟世界与元宇宙基础设施（宪法 / 法律 / 桥梁） |
| **Story-Engine** | [nohn3043-arch/story-engine](https://github.com/nohn3043-arch/story-engine) | 长篇叙事一致性引擎 |
| **Antares** | [nohn3043-arch/Antares](https://github.com/nohn3043-arch/Antares) | GFSIP v1.0——带因果审计的联邦稳定互操作协议 |
| **Anthropomorphic-Agent-Engine** | [nohn3043-arch/Anthropomorphic-Agent-Engine](https://github.com/nohn3043-arch/Anthropomorphic-Agent-Engine) | 确定性拟人心理引擎（SPL Pure Core V8.0） |
| **PAGES** | [nohn3043-arch/pages](https://github.com/nohn3043-arch/pages) | NOHN AI 生态官方落地页 |

<p align="center">— ✦ —</p>

## ✦ 许可与授权

本仓库**非开源**，采用双轨模式：个人非商业研究免费；政府 / 企业需付费商业授权。详见 [LICENSE](./LICENSE)。

- **申请授权**：国际 / 全球 — [ai@nohnlins.com](mailto:ai@nohnlins.com) · 中国 — [lin@secondai.top](mailto:lin@secondai.top)

<p align="center">
  <a href="https://github.com/nohn3043-arch">GitHub</a>
  &nbsp;·&nbsp;
  <a href="https://www.nohnlins.com/">nohnlins.com</a>
  &nbsp;·&nbsp;
  <a href="mailto:ai@nohnlins.com">ai@nohnlins.com</a>
</p>
<p align="center"><sub>NOHN AI · ANTARES</sub></p>
