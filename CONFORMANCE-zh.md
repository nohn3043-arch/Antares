# GFSIP/1.0 一致性测试指南

[English](CONFORMANCE.md) | 简体中文

**适用对象** —— 评估 GFSIP/1.0 的企业工程与安全团队、集成方、审计方，以及任何实现方。

**一条原则** —— 不要依赖协议作者发布的任何测试结果，包括本仓库中的"9/9 通过"。以下内容只服务一个目的：让你能从规范性工件中自行推导测试用例、在你自己的环境中运行、得出你自己的结论。参考实现及其测试脚本只是工作示例——可以作为被测对象或互操作对端使用，也可以完全忽略。

---

## 1. 声明可以说什么

规范 §27（一致性声明）规定了一条声明被允许包含的内容。宣称 `GFSIP/1.0 Core Conformant` 必须：

1. 实现固定帧头；
2. 实现确定性 CBOR；
3. 支持 QUIC + `gfsip/1`；
4. 通过全部 Core Mandatory 测试；
5. 发布实现版本、配置摘要和测试报告；
6. 不存在已知未修复的 Critical 安全问题。

`Audit/1` 与 `Federation/1` 必须独立声明。

§28 定义了九个**最小测试向量** —— 这是下限，不是度量。完整的必测清单是 `gfsip-conformance-checklist.csv`（34 条，全部 Mandatory）：

| 档位 | 条数 | 编号 |
|---|---|---|
| Core | 24 | CORE-001 … CORE-024 |
| Federation/1 | 6 | FED-001 … FED-006 |
| Audit/1 | 4 | AUDIT-001 … AUDIT-004 |

清单应作为**推导示例**阅读，而非权威 —— 第 3 节演示如何从规范自行推导用例。规范正文是唯一权威。

## 2. 规范性工件 —— 你的取证基准

| 工件 | 内容 | 在测试设计中的作用 |
|---|---|---|
| `GFSIP_v1.0_protocol_spec.md` | 规范性规范，33 节 | 你据以测试的条款 |
| `gfsip-traceability-matrix.csv` | 11 条需求 → 规范节 → 用例编号 → 实现组件 → 责任角色 | 定范围：选定需求，即得到对应条款与用例 |
| `gfsip-conformance-checklist.csv` | 34 条用例：`test_id, profile, level, name, input_condition, expected_result` | 交叉核对清单；`expected_result` 的取值是错误码登记表中的错误名 |
| `gfsip-error-registry.json` | 35 个数值错误码（`code, name, scope, fatal, retryable, description`） | 判定用语：断言错误码，绝不断言提示文字 |
| `gfsip-state-machine.json` | 8 个状态、不变量、转换表 | 负向测试：枚举非法的（状态, 事件）组合 |
| `gfsip-message-schema.json` | 逻辑消息 JSON Schema | 字段级与类型级检查 |

若机器可读工件与规范正文冲突，以规范为准——冲突本身就是值得报告的发现。抓出这类漂移，正是第三方复核存在的意义。

## 3. 设计你自己的测试

### 3.1 循环六步

1. **选定一条声明和一个档位。** 从可追溯矩阵出发：需求 → 规范节。
2. **精读条款。** 抽出每一条规范性的「必须 / 不得」。
3. **转化为可观测的预期**：一个错误码（错误码登记表）、一个状态（状态机）、一个副作用计数、一条审计链属性，或逐字节相等。
4. **构造刺激**：合法与非法帧、握手顺序、带指定属性的令牌与描述符。
5. **在运行之前定义判定器与通过标准。** 只能在看到输出之后才被解释的测试，不是证据。
6. **留痕**：原始日志、种子、工件哈希。第二个人必须能凭你保存的内容重跑。

### 3.2 可测性前提——实现必须暴露什么

- **带名字的数值错误码** —— 断言错误码，绝不断言人类可读文本。
- **会话状态与转换** —— 当前状态必须可查询；拒绝必须显式，绝不静默。
- **确定性 CBOR** —— 相同输入、逐字节相同的输出，因此"黄金字节"测试是正当的。规范允许随机的字段（nonce、会话 ID）不得做相等断言。
- **副作用计数** —— 已执行副作用的次数必须可观测；这是幂等性可被测试的前提。
- **若声明 Audit/1** —— 事件对象须暴露 ID、声明的因果前驱与状态哈希，使你能自行重算整条链。

### 3.3 技法目录

| 类别 | 攻击对象 | 依据工件 | 预期示例 |
|---|---|---|---|
| 线格式与编码 | 帧头合法性；CBOR 规范化 | 规范 §8 | `MALFORMED_FRAME`、`MALFORMED_HEADER` |
| 版本协商 | 版本不相交；降级尝试 | 规范 §11 | `VERSION_UNSUPPORTED`、`DOWNGRADE_DETECTED` |
| 状态机 | 非法（状态, 事件）组合 | 状态机 JSON | 以错误码显式拒绝；不得静默忽略 |
| 认证与会话安全 | 伪造凭证；重放；0-RTT 副作用 | 规范 §12、§23 | `AUTH_FAILED`、`EARLY_DATA_REJECTED` |
| 恢复 | 令牌绑定身份；一次性 | 规范 §16 | `RESUME_IDENTITY_MISMATCH`、`RESUME_REPLAY`、`RESUME_EXPIRED` |
| 幂等性 | 重复键；丢包下重试 | 规范 §15 | 副作用计数 = 1；`DUPLICATE_ACCEPTED` / `IN_PROGRESS` 语义 |
| 审计完整性 | 因果环；前驱上限；伪造签名 | 规范 §17 | `CAUSAL_CYCLE`、`CAUSAL_PARENT_LIMIT`、`EVENT_SIGNATURE_FAILED` |
| 联邦 | 描述符过期/伪造；环路；跳数上限 | 规范 §18 | `DESCRIPTOR_EXPIRED`、`DESCRIPTOR_SIGNATURE_FAILED`、`ROUTE_LOOP`、`ROUTE_HOP_LIMIT` |
| 资源限制 | 超大帧；解压炸弹；洪泛 | 规范 §21 | `FRAME_TOO_LARGE`、`DECOMPRESSION_LIMIT`、`RATE_LIMITED` |
| 故障注入 | 延迟、丢包、乱序、分区 | 规范 §16、§19 | 恢复可用；降级/终止行为显式 |

## 4. 参考实现 —— 作为被测对象或互操作对端

```bash
cd reference-impl
pip install -r requirements.txt    # cbor2, cryptography, aioquic
python -m gfsip.conformance        # 九个 §28 向量；退出码 0 = 通过，1 = 失败
python demo.py                     # 端到端演示；逐阶段打印 PASS/FAIL；退出码 0/1
python async_demo.py               # 异步 API 演示；退出码 0/1
python quic_demo.py                # 真实 QUIC/UDP 回环 127.0.0.1:4433（需 aioquic）
```

`conformance.py` 使用包内相对导入——必须用 `python -m gfsip.conformance` 运行，直接运行文件路径会报错。安装包之后（`pip install gfsip`），该模块在仓库之外也能运行。

作者自测（2026-10-08，Python 3.13.14 / Windows）：9/9 通过，退出码 0。请把它当作输出格式的示例——不是证据。想复现就复现，不想就忽略。Windows 控制台若非 UTF-8 代码页，部分字符可能显示乱码，设置 `PYTHONUTF8=1` 即可；结果不受影响。

## 5. 演示范例 —— 把九个 §28 向量重写为你自己的测试

每一行都是你可以对任意实现重新实现的用例。行为名与参考测试脚本的打印一致。

| 行为 | 清单编号 | 规范 | 你的刺激 → 你的判定 |
|---|---|---|---|
| 无共同版本 | CORE-006 | §11 | 两个 major 版本不相交的 HELLO → 握手失败；状态 CLOSED；错误码 `VERSION_UNSUPPORTED` |
| Initiator 申请偶数通道 | CORE-011 | §14 | Initiator 申请偶数通道 ID → 拒绝 `INVALID_CHANNEL_ID`；其后不存在该通道 |
| 同一幂等键 → 1 次副作用 | CORE-014 | §15 | 同一操作、同一键提交两次 → 副作用计数 = 1；第二次结果标记为重复 |
| 恢复令牌跨节点 | CORE-017 | §16 | 把签发给身份 A 的恢复令牌以身份 B 出示 → `RESUME_IDENTITY_MISMATCH`；会话不恢复 |
| 重复 Sequence | CORE-015 | §8.2 | 同一序号投递两次 → 第二帧拒绝 `SEQUENCE_REPLAY`；不交付应用 |
| 事件以自身为父 | AUDIT-001 | §17 | 添加父事件列表包含自身的事件 → `CAUSAL_CYCLE`；事件不入链 |
| 0-RTT 副作用 | CORE-019 | §23 | 在 ESTABLISHED 之前发送携带副作用的 EARLY_DATA → `EARLY_DATA_REJECTED`；状态不变 |
| 描述符过期 | FED-002 | §18 | 注册已过 `valid_until` 的域描述符 → `DESCRIPTOR_EXPIRED`；不建立新信任 |
| 路由循环 | FED-003 | §18 | `visited_domains` 已含本域的路由查询 → `ROUTE_LOOP` |

## 6. 结果报告格式

按以下结构写的报告可以逐行审计，分歧可以定位到单条用例：

| 字段 | 内容 |
|---|---|
| 被测实现 | 名称、版本、源码提交 |
| 所测工件 | 规范 / 清单的哈希（如 `SHA256SUMS.txt` 中的行） |
| 环境 | 操作系统、运行时、网络路径、传输配置 |
| 档位 | Core/1（如测了则加 Audit/1、Federation/1） |
| 用例 | 每条一行：刺激、预期、实测、判定、原始日志引用 |
| 偏差 | 每一项未满足的「必须」，附规范条款 |

## 7. 覆盖边界 —— 本仓库不证明什么

- 本仓库自动化的范围：九个 §28 最小向量。34 条清单**并未**全部自动化。
- 未配置 CI，测试脚本为手动运行。
- 尚无独立第二实现，也没有公开的互操作报告——两者在 README「项目状态」中均标注为进行中/待办。
- §27.6（"不存在已知未修复的 Critical 安全问题"）是一项声明性断言，无法黑盒测试——请通过厂商的漏洞披露流程去核实。
- v1.0 未规定性能与负载指标，属于一致性范围之外。
- PyPI 包版本可能与仓库 HEAD 漂移——请锁定你实际测试的提交或工件哈希。

---

规范与文档：CC BY 4.0（`LICENSE-SPEC.md`）。代码：Apache-2.0（`LICENSE`）。
