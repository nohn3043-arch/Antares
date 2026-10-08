<div align="center">

# 📖 术语表 · Glossary

**ANTARES · GFSIP v1.0**

*每个词都用一句人话解释 · Every term explained in one plain sentence*

</div>

---

> 英文术语保留原样，方便你对照 README、协议规范与代码。
> The English term is kept as-is so you can match it against the README, the spec and the code.

| 术语 Term | 中文 | 一句话人话 · Plain meaning |
|---|---|---|
| **GFSIP** | 全球联邦稳定互通协议 | 一套让不同机构、设备、AI 之间安全通信的开放协议标准。 |
| **QUIC** | QUIC 传输层 | 新一代传输协议（也是 HTTP/3 的底座），换网时连接不容易断。 |
| **ALPN `gfsip/1`** | 应用层协议标识 | 握手时用来声明「我讲的是 GFSIP 第 1 版」。 |
| **44-byte fixed header** | 44 字节定长头 | 每条消息开头固定 44 字节，解析快、不易出错。 |
| **CBOR** | 二进制 JSON | 比 JSON 更紧凑的序列化格式，且编码唯一、结果可复现。 |
| **Multiplexing** | 多路复用 | 一条连接里开出多条互不阻塞的「车道」。 |
| **Session resumption** | 会话恢复 | 网络切换后不用重新登录，接着用。 |
| **Idempotency key** | 幂等键 | 同一个请求带上同一个键，服务端保证只执行一次。 |
| **Windowed deduplication** | 窗口去重 | 只在一个时间窗内做去重，不必无限保存历史。 |
| **Causal audit** | 因果审计 | 每条事件都记下「我是由谁引起的」，并可验签抽查。 |
| **Causal predecessor** | 因果前驱 | 事件声明的上游事件，把历史连成一张有向图。 |
| **DomainDescriptor** | 域描述符 | 一个域的签名名片，含公钥与路由信息，可过期、可吊销。 |
| **Trust anchor** | 信任锚 | 你预先信任的那个根公钥，其他信任都从它推导出来。 |
| **Fault isolation** | 故障隔离 | 一个域挂了，不影响该域内部以及其它域的通信。 |
| **Core / Audit / Federation** | 三个协议档位 | 必选的通信核心，加上两个可选能力档：审计、联邦。 |
| **Conformance vectors** | 一致性测试向量 | 规范给出的测试用例，第三方实现拿它自测是否合规。 |

---

<div align="center">

[← 返回 README](./README.md) &nbsp;·&nbsp; [中文说明](./README-zh.md)

<sub>NOHN AI · ANTARES</sub>

</div>
