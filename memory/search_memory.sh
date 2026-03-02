#!/bin/bash
# 记忆检索工具
# 用法: ./search_memory.sh <关键词>

KEYWORD=$1

echo "🔍 搜索记忆: $KEYWORD"
echo "=========================================="

# 1. 搜索关键词索引
if [ -f "indices/keywords.json" ]; then
    echo "📑 相关主题:"
    cat indices/keywords.json | grep -A 5 "$KEYWORD" | head -20
    echo
fi

# 2. 搜索今日对话
if [ -f "conversations/2026-02-24.jsonl" ]; then
    echo "💬 今日相关对话:"
    grep -i "$KEYWORD" conversations/2026-02-24.jsonl | head -5
    echo
fi

# 3. 搜索主题文件
for topic in topics/*/README.md; do
    if grep -q -i "$KEYWORD" "$topic" 2>/dev/null; then
        echo "📁 主题文件: $topic"
        grep -i -B 2 -A 2 "$KEYWORD" "$topic" | head -10
        echo
    fi
done

# 4. 搜索摘要
echo "📝 相关摘要:"
grep -r -i "$KEYWORD" summaries/ 2>/dev/null | head -5
