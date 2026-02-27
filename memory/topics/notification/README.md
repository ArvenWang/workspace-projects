# 飞书通知与自动化主题

## 概述
用户需要可靠的飞书主动消息推送能力，用于交易提醒、定时报告等场景。

## 关键决策

### ✅ 已实现功能
1. **OpenClaw原生Cron定时任务**
   - 使用 `openclaw cron add` 创建定时任务
   - 支持多种调度方式（interval、cron表达式）
   - 自动持久化，Gateway负责唤醒

2. **运行中的任务**
   | 任务 | 频率 | 状态 |
   |-----|------|------|
   | feishu-test | 每3分钟 | ✅ 运行中 |
   | 交易日报推送 | 每日20:00 | ✅ 运行中 |

## 技术方案

### 正确方案（已采用）
```bash
openclaw cron add \
  --name "任务名" \
  --cron "0 20 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "提示词" \
  --announce \
  --channel feishu \
  --to "user:用户ID"
```

### 错误方案（已废弃）
- bash脚本后台运行（不可靠，进程易被杀）

## 相关对话
- 2026-02-24: conversations/2026-02-24.jsonl (消息ID: om_x100b56f...)

## 后续优化方向
- [ ] 飞书交互卡片支持
- [ ] 多渠道通知（备用渠道）
- [ ] 通知失败重试机制
