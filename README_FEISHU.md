# 🚀 飞书机器人重新部署方案

> 支持收发图片和语音，迁移所有现有能力

---

## 📦 已创建的文件

| 文件 | 说明 |
|------|------|
| `FEISHU_BOT_DEPLOY.md` | 完整部署文档 |
| `FEISHU_PERMISSIONS.md` | 权限配置清单 |
| `FEISHU_CAPABILITIES.md` | 能力迁移清单 |
| `deploy_feishu_bot.sh` | 交互式部署脚本（推荐） |
| `setup_feishu_bot.sh` | 快速配置脚本 |
| `feishu_message_handler.py` | 消息处理器 |

---

## 🚀 快速开始（推荐方式）

### 方式一：交互式部署向导

```bash
cd ~/.openclaw/workspace
./deploy_feishu_bot.sh
```

然后按照提示输入飞书应用的 App ID 和 App Secret。

### 方式二：命令行快速配置

```bash
cd ~/.openclaw/workspace
./setup_feishu_bot.sh <your_app_id> <your_app_secret>
```

---

## 📋 完整部署流程

### Step 1: 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 创建「企业自建应用」
3. 记录 **App ID** 和 **App Secret**

### Step 2: 开通权限（关键）

在「权限管理」中开通：

**必须开通（收发消息）：**
- `im:message:send`
- `im:message:send:as_bot`
- `im:message.p2p_msg`
- `im:message.group_msg`
- `im:message.resource` ⚠️ **关键：用于接收图片/语音**
- `im:message:receive`

**图片/语音必需：**
- `im:message.resource` - 获取消息资源

完整权限列表见 `FEISHU_PERMISSIONS.md`

### Step 3: 配置事件订阅

1. 进入「事件订阅」
2. 开启事件订阅
3. 添加事件：`im.message.receive_v1`

### Step 4: 运行部署脚本

```bash
./deploy_feishu_bot.sh
```

输入 App ID 和 App Secret，脚本会自动：
- 备份旧配置
- 写入新配置
- 重启服务
- 验证连接

### Step 5: 发布应用

1. 进入「版本管理与发布」
2. 创建版本（1.0.0）
3. 申请发布

### Step 6: 开始使用

在飞书搜索「OpenClaw AI」，点击「开始使用」。

---

## ✅ 测试清单

部署完成后，在飞书中测试：

- [ ] 发送文本消息
- [ ] 发送语音消息（自动转文字）
- [ ] 发送图片
- [ ] 查询加密货币价格
- [ ] 网页搜索
- [ ] 读取飞书文档

---

## 🎨 支持的消息类型

| 类型 | 接收 | 发送 | 说明 |
|------|------|------|------|
| 文本 | ✅ | ✅ | 基础消息 |
| 图片 | ✅ | ✅ | 图片分析、截图 |
| 语音 | ✅ | ✅ | 语音转文字、TTS 回复 |
| 文件 | ✅ | ✅ | 文件传输 |
| Markdown | ✅ | ✅ | 富文本 |
| 卡片 | ❌ | ✅ | 富文本卡片 |

---

## 🔧 语音转文字配置

语音功能依赖 Whisper，已安装：

```bash
# 检查 Whisper 状态
python3 ~/.openclaw/workspace/voice_transcriber.py --check

# 支持的模型
tiny (39MB) - 最快
base (74MB) - 快
small (461MB) - 推荐 ✅
medium (1.5GB) - 准确
large (2.9GB) - 最准确
```

修改配置文件可切换模型：
```yaml
voiceTranscription:
  model: small  # tiny/base/small/medium/large
  language: zh
```

---

## 📚 迁移的能力清单

全部 19 个技能已迁移：

### 💰 交易
- binance-pro - 币安完整功能
- crypto-trading-bot - 交易机器人
- realtime-crypto-price-api - 实时价格

### 🔍 搜索
- duckduckgo-search
- perplexity
- firecrawl-search
- baidu-search

### 📱 飞书
- feishu-notification
- feishu-doc
- feishu-wiki
- feishu-drive

### 🌐 浏览器/媒体
- browser-use
- youtube-ultimate
- x-twitter

### 🤖 AI
- agent-training
- recursive-self-improvement
- self-reflection

### 💻 系统
- system-info
- macos-desktop-control

---

## 🐛 故障排查

### 收不到消息
```bash
# 检查飞书状态
openclaw status

# 查看日志
openclaw logs --follow
```

### 图片/语音无法接收
- 检查 `im:message.resource` 权限是否开通
- 检查事件订阅是否包含 `im.message.receive_v1`

### 语音转文字失败
```bash
# 测试语音转录
python3 ~/.openclaw/workspace/voice_transcriber.py /path/to/audio.ogg
```

---

## 📖 相关文档

```bash
# 部署指南
cat FEISHU_BOT_DEPLOY.md

# 权限清单
cat FEISHU_PERMISSIONS.md

# 能力清单
cat FEISHU_CAPABILITIES.md
```

---

## 💡 高级配置

### 自定义机器人名称

编辑 `~/.openclaw/agents/main/config.yaml`：

```yaml
channels:
  feishu:
    accounts:
      main:
        botName: "你的机器人名称"
```

### 限制可访问用户

```yaml
channels:
  feishu:
    accounts:
      main:
        allowFrom:
          - "ou_xxxxxxxxxxxxxxxx"  # 你的 OpenID
```

### 语音模型切换

```yaml
voiceTranscription:
  model: medium  # 更高的准确性
  language: zh
```

---

**准备开始了吗？运行 `./deploy_feishu_bot.sh`** 🚀
