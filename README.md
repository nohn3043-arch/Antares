<p align="center">
  <img src="assets/banner.svg" alt="ANTARES banner" style="width:100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/protocol-D4AF37?style=flat-square" alt="protocol">  <img src="https://img.shields.io/badge/quic-D4AF37?style=flat-square" alt="quic">  <img src="https://img.shields.io/badge/federation-D4AF37?style=flat-square" alt="federation">
</p>

<blockquote align="center">
  <em>全球联邦化稳定互操作协议 v1.0（Global Federated Stable Interoperability Protocol）</em>
</blockquote>

<div style="max-width:880px;margin:0 auto;padding:0 16px">

## ✦ 关于

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">ANTARES 即 GFSIP v1.0——全球联邦化稳定互操作协议。它为服务、AI 智能体、设备与组织提供加密、多通道、可恢复的跨域通信，且无需中心化权威节点。协议以 QUIC 为强制传输层，采用确定性 CBOR 序列化，内置会话恢复、幂等去重与因果审计，是去中心化网络的稳定基石。</p>

<p align="center">
  <img src="assets/overview.svg" alt="ANTARES overview" style="width:100%">
</p>

</div>

<p align="center">— ✦ —</p>

## ✦ 核心能力

<div style="max-width:880px;margin:0 auto;padding:0 16px">

<table style="width:100%;border-collapse:collapse;font-size:14px">
  <tr><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">#</th><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">能力</th><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">说明</th></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">1</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>加密会话</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">基于 QUIC 的双向 TLS 或令牌认证会话</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">2</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>多通道</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">单个会话内相互独立的逻辑通道</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">3</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>会话恢复</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">跨网络切换恢复会话，无需重新认证</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">4</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>幂等副作用</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">基于幂等键的有限窗口去重</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">5</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>因果审计（可选）</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">带声明因果前驱的签名事件记录</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">6</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>跨域联邦</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">基于签名域描述符的多信任锚路由</td></tr>
  <tr><td style="padding:8px">7</td><td style="padding:8px"><strong>故障隔离</strong></td><td style="padding:8px">单域故障不会阻塞域内流量</td></tr>
</table>

</div>

<p align="center">— ✦ —</p>

## ✦ 线协议

<div style="max-width:880px;margin:0 auto;padding:0 16px">

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">GFSIP 在 QUIC 之上使用 <strong>44 字节固定头部</strong>，ALPN 为 <code style="background:#F5F0E6;padding:2px 6px;border-radius:3px;color:#C9A96E">gfsip/1</code>。扩展头部采用确定性 CBOR（大端、最短编码）。18 种标准消息类型（<code>0x01</code>–<code>0x16</code>）覆盖完整生命周期：握手、通道管理、数据传输、会话恢复、审计事件与联邦路由。</p>

</div>

<p align="center">— ✦ —</p>

## ✦ 仓库内容

<div style="max-width:880px;margin:0 auto;padding:0 16px">

<table style="width:100%;border-collapse:collapse;font-size:14px">
  <tr><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">文件</th><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">用途</th></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><code>GFSIP_v1.0_protocol_spec.md</code></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">完整协议规范（33 节）</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><code>gfsip-state-machine.json</code></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">机器可读的状态机定义</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><code>gfsip-message-schema.json</code></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">逻辑消息 JSON Schema</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><code>gfsip-error-registry.json</code></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">数字错误码注册表</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><code>gfsip-conformance-checklist.csv</code></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">一致性测试检查清单</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><code>reference-impl/</code></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">Python 参考实现——帧编解码、状态机、通道管理、认证、去重、恢复、审计、联邦、端到端演示（9/9 一致性向量全部通过）</td></tr>
</table>

</div>

<p align="center">— ✦ —</p>

## ✦ 协议档位

<div style="max-width:880px;margin:0 auto;padding:0 16px">

<p style="font-size:15px;line-height:1.8;color:#2C2C2C"><strong style="color:#C9A96E">Core/1（强制）</strong> —— QUIC 传输、版本协商、双向认证、会话与通道管理、会话恢复、结构化错误与优雅关闭。</p>

<p style="font-size:15px;line-height:1.8;color:#2C2C2C"><strong style="color:#C9A96E">Audit/1（可选）</strong> —— 带声明前驱、行为者身份、规则版本与状态前后哈希的签名因果事件记录。拒绝自环与已知环。</p>

<p style="font-size:15px;line-height:1.8;color:#2C2C2C"><strong style="color:#C9A96E">Federation/1（可选）</strong> —— 通过签名的 <code>DomainDescriptor</code> 对象进行跨域路由，多信任锚配置，以及带故障隔离的描述符过期/撤销机制。</p>

</div>

<p align="center">— ✦ —</p>

## ✦ 快速开始

```bash
git clone git@github.com:NOHN-AI/ANTARES.git
cd ANTARES/reference-impl
pip install -r requirements.txt
python demo.py          # 端到端演示：握手 → 通道 → 数据 → 去重 → 恢复
python conformance.py   # 9 个最小一致性向量——全部通过
```

<p align="center">— ✦ —</p>

## ✦ 使用场景

<div style="max-width:880px;margin:0 auto;padding:0 16px">

- **AI 智能体网络** —— 跨组织边界、带可审计轨迹的多智能体任务协同
- **企业集成** —— 无需中心化权威节点的跨组织工作流编排
- **IoT / 边缘** —— 跨网络变化的设备到云会话恢复
- **金融 / 合规** —— 用于监管报告的可签名因果审计轨迹
- **医疗健康** —— 带域级策略执行的联邦数据交换
- **机器人** —— 带幂等安全操作的可靠指令通道

</div>

<p align="center">— ✦ —</p>

## ✦ 项目状态

<div style="max-width:880px;margin:0 auto;padding:0 16px">

<table style="width:100%;border-collapse:collapse;font-size:14px">
  <tr><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">里程碑</th><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">状态</th></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">规范 v1.0（接口已冻结）</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">✅ 完成</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">机器可读状态机与 Schema</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">✅ 完成</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">Python 参考实现（9/9 一致性）</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">✅ 完成</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">独立的第二实现</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">🔲 进行中</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">公开互操作性报告</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">🔲 待办</td></tr>
  <tr><td style="padding:8px">生产试点域</td><td style="padding:8px">🔲 待办</td></tr>
</table>

</div>

<p align="center">— ✦ —</p>

<p align="center">
  <a href="https://github.com/NOHN-AI">NOHN-AI</a>
  &nbsp;·&nbsp;
  <a href="https://www.nohnlins.com/">nohnlins.com</a>
  &nbsp;·&nbsp;
  <a href="mailto:lin@secondai.top">lin@secondai.top</a>
</p>
<p align="center"><sub>NOHN AI · ANTARES</sub></p>
