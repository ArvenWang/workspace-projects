# WeChat Bot Skill

> 自动回复微信消息的OpenClaw Skill

## 功能

- ✅ 自动回复微信消息
- ✅ 关键词自动回复
- ✅ AI智能回复 (需配置API)
- ✅ 群消息处理

## 前置要求

```bash
pip3 install itchat
```

## 配置

编辑 `wechat_bot.py` 配置:

```python
CONFIG = {
    'reply_enabled': True,
    'ai_enabled': True,
    'keyword_replies': {
        'hello': '你好！',
    }
}
```

## 启动

```bash
python3 ~/.openclaw/workspace/wechat_bot.py
```

首次运行需要扫码登录。

## AI接入

在 `get_ai_reply()` 中接入:
- OpenAI API
- Claude API
- Kimi API
- 等等

## 文件

- `wechat_bot.py` - 主程序
