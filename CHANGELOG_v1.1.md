# Changelog — v1.1.0

## 许可变更（重要）

自本版本起，本仓库采用**双轨许可**：

| 内容 | 许可 | 文件 |
|---|---|---|
| 代码实现（`reference-impl/` 下的 Python 包 `gfsip`） | Apache License 2.0 | `LICENSE` |
| 协议规范与文档（`GFSIP_v1.0_protocol_spec.md`、`gfsip-*.json`、`gfsip-*.csv`、`assets/` 图示） | CC BY 4.0（不变） | `LICENSE-SPEC.md` |

改动动机：CC BY 4.0 是内容许可，无明示专利授予且非 OSI 认证，企业采购流程通常不予接受；代码层改用 Apache-2.0 可获得明示专利授予与 OSI 认证。规范层保留 CC BY 4.0，以强制署名服务于 GFSIP 作为开放标准的传播目标。

### 不可撤销声明

v1.0 及此前发布的版本曾整体以 CC BY 4.0 发布（含代码）。该授权依 CC BY 4.0 条款**不可撤销**——相关版本将永久可依 CC BY 4.0 使用，本次变更不减损任何人已取得的权利。上述双轨安排自 v1.1.0 起生效。

### 新增文件

- `LICENSE` — Apache License 2.0 全文（替换原 CC BY 4.0 全文）
- `LICENSE-SPEC.md` — CC BY 4.0 全文及其适用范围说明
- `NOTICE` — Apache-2.0 归属声明与分离许可说明

## 依赖修复

- 新增必需依赖 `aioquic>=1.0.0`（QUIC 传输层）。此前 `aioquic` 仅列于 `reference-impl/requirements.txt`，未进入 `pyproject.toml` 的 `dependencies`，导致 `pip install gfsip` 装出的包缺少 QUIC 传输依赖、`quic_transport` 无法使用。
