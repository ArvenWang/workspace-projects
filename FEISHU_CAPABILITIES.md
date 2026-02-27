# 飞书机器人能力迁移清单

以下是目前 workspace 中所有可用的技能，已全部支持通过飞书机器人调用。

---

## 💰 加密货币交易

### 1. Binance Pro (binance-pro)
**功能**: 完整的币安交易所集成
**飞书使用**:
```
查看账户余额
查询 BTC/USDT 价格
下单买入 0.01 BTC
设置止损 BTC 45000
查看持仓盈亏
```

### 2. Crypto Trading Bot (crypto-trading-bot)
**功能**: 自动交易机器人开发框架
**飞书使用**:
```
启动交易机器人
查看机器人状态
停止所有机器人
```

### 3. Realtime Crypto Price API (realtime-crypto-price-api)
**功能**: 实时加密货币价格查询
**飞书使用**:
```
查询 BTC 价格
查询 ETH 实时行情
显示热门币种
```

---

## 🔍 搜索与信息

### 4. DuckDuckGo Search (duckduckgo-search)
**功能**: 匿名网页搜索
**飞书使用**:
```
搜索 OpenAI 最新新闻
搜索 Python 教程
```

### 5. Perplexity (perplexity)
**功能**: AI 驱动的搜索引擎
**飞书使用**:
```
用 Perplexity 搜索量子计算
搜索 2024 年 AI 发展趋势
```

### 6. Firecrawl (firecrawl-search)
**功能**: 网页爬取和结构化数据提取
**飞书使用**:
```
爬取 https://example.com 的内容
提取网页中的表格数据
```

### 7. Baidu Search (baidu-search)
**功能**: 百度搜索
**飞书使用**:
```
百度搜索 北京天气
搜索中文技术文档
```

---

## 📱 飞书生态

### 8. Feishu Notification (feishu-notification)
**功能**: 主动发送飞书消息
**飞书使用**:
```
发送消息给 @张三
发送群通知给测试群
发送 Markdown 卡片
```

### 9. Feishu Doc (feishu_doc)
**功能**: 飞书文档操作
**飞书使用**:
```
读取文档 xxx
创建新文档
在文档中追加内容
```

### 10. Feishu Wiki (feishu_wiki)
**功能**: 飞书知识库操作
**飞书使用**:
```
列出知识库空间
读取 wiki 页面
创建 wiki 节点
```

### 11. Feishu Drive (feishu_drive)
**功能**: 飞书云盘操作
**飞书使用**:
```
列出云盘文件
创建文件夹
移动文件到 xxx
```

---

## 🌐 浏览器与媒体

### 12. Browser Use (browser-use)
**功能**: 浏览器自动化
**飞书使用**:
```
打开 https://example.com
截图当前页面
填写表单
点击按钮
```

### 13. YouTube Ultimate (youtube-ultimate)
**功能**: YouTube 视频下载和转录
**飞书使用**:
```
下载 YouTube 视频 xxx
获取视频字幕
提取视频关键帧
```

### 14. X/Twitter (x-twitter)
**功能**: Twitter/X 操作
**飞书使用**:
```
搜索推文 #Bitcoin
获取用户 @elonmusk 的最新推文
```

---

## 🤖 AI 与自动化

### 15. Agent Training (agent-training)
**功能**: Agent 培训系统
**飞书使用**:
```
创建新 Agent
查看 Agent 培训手册
执行团队监管检查
```

### 16. Recursive Self Improvement (recursive-self-improvement)
**功能**: 递归自我改进系统
**飞书使用**:
```
启动自我优化
查看优化日志
修复检测到的错误
```

### 17. Self Reflection (self-reflection)
**功能**: 自我反思和记忆
**飞书使用**:
```
反思今天的对话
更新记忆
查看历史反思
```

---

## 💻 系统控制

### 18. System Info (system-info)
**功能**: 系统信息查询
**飞书使用**:
```
查看系统状态
检查磁盘空间
查看内存使用
```

### 19. macOS Desktop Control (macos-desktop-control)
**功能**: macOS 桌面控制
**飞书使用**:
```
截图屏幕
控制音量
打开应用 xxx
```

---

## 📊 交易数据相关（自定义脚本）

以下是在 workspace 中的交易相关脚本：

| 脚本 | 功能 | 飞书使用 |
|------|------|----------|
| `safe_trading_bot_v2.py` | 安全交易机器人 | 启动安全交易模式 |
| `altcoin_trader_v4.py` | 山寨币交易 | 交易山寨币 |
| `manual_trader.py` | 手动交易 | 手动下单 |
| `monitor_bot.py` | 监控机器人 | 启动价格监控 |

---

## 🎤 语音功能

### 语音转文字 (Voice Transcription)
**功能**: 使用 Whisper 将语音转为文字
**飞书使用**:
- 直接发送语音消息给机器人
- 机器人自动转录并回复

---

## 🖼️ 图片功能

### 图片处理
**功能**: 接收、分析、发送图片
**飞书使用**:
- 发送图片给机器人进行分析
- 机器人可以发送截图或生成的图片

---

## 📋 快速命令参考

### 交易类
```
余额 - 查看账户余额
价格 <币种> - 查询价格
下单 <方向> <数量> <币种> - 下单
持仓 - 查看持仓
```

### 搜索类
```
搜索 <关键词> - 网页搜索
爬取 <URL> - 网页爬取
```

### 飞书类
```
文档 <token> - 读取文档
Wiki <token> - 读取知识库
云盘 - 列出文件
```

### 系统类
```
状态 - 系统状态
截图 - 屏幕截图
音量 <数值> - 调整音量
```

---

## ✅ 验证清单

部署完成后，在飞书中测试以下功能：

- [ ] 发送文本消息，正常回复
- [ ] 发送语音消息，自动转文字
- [ ] 发送图片，正常接收
- [ ] 查询加密货币价格
- [ ] 网页搜索
- [ ] 读取飞书文档
- [ ] 浏览器截图
- [ ] 系统状态查询

---

**所有能力已准备就绪！**
