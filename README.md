# GFSIP/1.0 Release Package

## 内容
- `GFSIP_v1.0_protocol_spec.md`：主规范
- `gfsip-state-machine.json`：机器可读状态机
- `gfsip-message-schema.json`：逻辑消息 Schema
- `gfsip-error-registry.json`：数值错误码
- `gfsip-conformance-checklist.csv`：一致性测试
- `gfsip-traceability-matrix.csv`：需求—规范—测试—实现—责任映射
- `CHANGELOG_v1.0.md`：版本变更
- `SHA256SUMS.txt`：文件摘要

## 状态
这是实现就绪候选规范。版本号 1.0 表示接口冻结，不表示已经获得标准组织批准或完成外部互操作验证。

## 下一执行节点
1. Frame Codec
2. Session State Machine
3. QUIC Adapter
4. Authentication
5. Channel Manager
6. Dedupe Store
7. Resume Service
8. 两个独立实现
9. 一致性测试
10. 安全审计和生产试点
