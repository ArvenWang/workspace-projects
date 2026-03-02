# 记忆系统架构文档

## 目录结构

```
workspace/memory/
├── README.md                 # 本文件 - 系统说明
├── SYSTEM.md                 # 记忆系统使用规范
├── conversations/            # 原始对话记录
│   ├── 2026-02-24.jsonl     # 按日期存储
│   ├── 2026-02-25.jsonl
│   └── ...
├── summaries/               # 对话摘要
│   ├── 2026-02-24.md
│   └── ...
├── topics/                  # 主题分类
│   ├── trading/            # 交易相关
│   ├── manju/              # 漫剧相关
│   ├── automation/         # 自动化相关
│   └── ...
└── indices/                # 索引文件
    ├── keywords.json       # 关键词索引
    ├── timeline.md         # 时间线
    └── decisions.md        # 决策记录
```

## 文件格式

### 1. 对话记录 (.jsonl)
```json
{
  "timestamp": "2026-02-24T10:05:15+08:00",
  "session_id": "xxx",
  "message_id": "xxx",
  "role": "user|assistant",
  "content": "...",
  "topics": ["trading", "automation"],
  "importance": 1-5
}
```

### 2. 摘要 (.md)
- 每次对话结束后的要点总结
- 便于快速回顾

### 3. 主题分类
- 按项目/话题组织的汇总
- 包含相关对话的链接

## 使用流程

1. **对话中**：实时记录到conversations/
2. **对话后**：生成摘要到summaries/
3. **定期整理**：更新topics/和indices/
4. **上下文缺失时**：查询相关主题和摘要
