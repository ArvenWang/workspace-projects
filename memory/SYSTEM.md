# 记忆系统操作规范

## 核心原则

**所有对话必须记录，关键信息必须提取。**

## 何时记录

### 必须记录的场景
- [x] 用户提出新需求或任务
- [x] 完成重要工作或达成决策
- [x] 用户分享个人偏好、目标、约束
- [x] 犯错或学习到教训
- [x] 约定时间、待办事项

### 记录格式 (JSONL)
```json
{
  "timestamp": "ISO8601",
  "session_id": "...",
  "message_id": "...",
  "role": "user|assistant",
  "type": "message|action|decision|preference|todo",
  "content": "...",
  "topics": ["topic1", "topic2"],
  "importance": 1-5,
  "summary": "一句话摘要"
}
```

## 何时使用摘要回答

以下情况使用简洁摘要而非详细回答：

1. **重复性问题** - 用户问过类似问题
2. **状态查询** - 询问之前的工作进度
3. **日常问候** - 简单寒暄
4. **确认信息** - 核实之前的约定

**摘要格式**：
```
[摘要] 核心结论 (详见: memory/xxx)
[要点] 1. xxx  2. xxx  3. xxx
[时间] 2026-02-24
```

## 何时检索记忆

**上下文缺失时必须检索**：

1. 用户提到"之前说的"、"上次"等词
2. 用户问"进度如何"、"完成了吗"
3. 感觉对话有断裂或不连贯
4. 长时间（>1小时）后的新对话

**检索顺序**：
1. 检查今日summary文件
2. 查询相关topic目录
3. 搜索indices/keywords.json
4. 必要时读取完整conversation文件

## 记忆维护

### 每日维护（heartbeat时）
- [ ] 整理今日对话摘要
- [ ] 更新topic分类
- [ ] 检查待办事项状态
- [ ] 更新decisions.md

### 每周维护
- [ ] 清理过期临时信息
- [ ] 归档已完成项目
- [ ] 更新knowledge graph

## 关键文件说明

| 文件 | 用途 | 更新频率 |
|------|------|----------|
| conversations/*.jsonl | 原始对话 | 每次对话 |
| summaries/*.md | 每日摘要 | 每天 |
| topics/*/README.md | 主题汇总 | 每周 |
| indices/decisions.md | 决策记录 | 每次决策 |
| indices/timeline.md | 时间线 | 每周 |
| indices/keywords.json | 关键词索引 | 每周 |

## 用户画像 (USER_PROFILE)

记录用户的偏好和约束：

```json
{
  "name": "...",
  "preferences": {
    "response_style": "detailed|summary",
    "working_hours": "...",
    "notification_preference": "..."
  },
  "constraints": {
    "budget": "...",
    "timeline": "..."
  },
  "active_projects": ["..."],
  "habits": ["..."]
}
```
