# 飞书机器人重新部署方案

## 目标
- 创建新的飞书机器人应用
- 支持收发图片和语音
- 迁移所有现有能力
- 完整的权限配置

---

## 一、创建新的飞书应用

### 1.1 访问飞书开放平台
1. 前往 https://open.feishu.cn/app
2. 点击「创建企业自建应用」
3. 填写应用信息：
   - 应用名称：OpenClaw AI
   - 应用描述：智能助手，支持文本、图片、语音交互
   - 图标：上传自定义图标（可选）

### 1.2 记录关键凭证
创建完成后，在「凭证与基础信息」中获取：
- **App ID**: `cli_xxxxxxxxxxxxxxxx`
- **App Secret**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 二、权限配置（关键步骤）

### 2.1 机器人能力
进入「权限管理」，添加以下权限：

**消息与群组权限：**
- [x] `im:chat:readonly` - 获取群组信息
- [x] `im:chat` - 创建和管理群组
- [x] `im:message:send` - 发送消息
- [x] `im:message:send:as_bot` - 以机器人身份发送消息
- [x] `im:message.p2p_msg` - 读取用户单聊消息
- [x] `im:message.group_msg` - 读取用户群聊消息
- [x] `im:message.resource` - 获取消息资源（图片、文件）
- [x] `im:message:receive` - 接收消息事件
- [x] `im:message:delete` - 删除消息（可选）

**用户权限：**
- [x] `contact:user.department:readonly` - 获取用户部门信息
- [x] `contact:user.employee_id:readonly` - 获取用户员工ID

**文档权限（如需使用飞书文档技能）：**
- [x] `docx:document:readonly`
- [x] `docx:document:write`
- [x] `docx:document:delete`
- [x] `wiki:wiki:readonly`
- [x] `wiki:wiki:write`

**云盘权限（如需使用飞书云盘）：**
- [x] `drive:drive:readonly`
- [x] `drive:drive:write`
- [x] `drive:file:readonly`
- [x] `drive:file:write`

### 2.2 事件订阅配置

进入「事件订阅」，开启事件订阅并添加以下事件：

**消息事件：**
- [x] `im.message.receive_v1` - 接收消息
- [x] `im.message.message_read_v1` - 消息已读
- [x] `im.message.message_deleted_v1` - 消息被删除

**机器人加入群组事件：**
- [x] `im.chat.disbanded_v1` - 群组解散
- [x] `im.chat.updated_v1` - 群组信息更新

### 2.3 加密配置（可选但推荐）

如果需要加密：
1. 在「事件订阅」-「加密策略」中生成 Encrypt Key
2. 配置 Verification Token

---

## 三、发布应用

### 3.1 创建版本
1. 进入「版本管理与发布」
2. 点击「创建版本」
3. 填写版本信息：
   - 版本号：1.0.0
   - 更新说明：初始版本，支持文本、图片、语音消息
   - 可用性状态：「开启」（仅管理员可用）或「部分用户可用」

### 3.2 申请发布
- 点击「申请发布」
- 等待管理员审批

### 3.3 机器人使用
- 在飞书搜索「OpenClaw AI」
- 点击「开始使用」
- 或者在群组中添加机器人

---

## 四、OpenClaw 配置

### 4.1 更新配置文件

编辑 `~/.openclaw/agents/main/config.yaml`：

```yaml
channels:
  feishu:
    enabled: true
    dmPolicy: pairing
    streaming: true
    blockStreaming: true
    accounts:
      main:
        appId: "cli_xxxxxxxxxxxxxxxx"      # 替换为你的新 App ID
        appSecret: "xxxxxxxxxxxxxxxxxxxx"   # 替换为你的新 App Secret
        botName: "OpenClaw AI"
        # 图片和语音支持配置
        mediaSupport:
          images: true
          voice: true
          file: true
        # 语音转文字配置
        voiceTranscription:
          enabled: true
          model: small  # tiny/base/small/medium/large
          language: zh
```

### 4.2 重启 OpenClaw

```bash
openclaw gateway restart
```

---

## 五、图片和语音处理集成

### 5.1 图片处理流程

**接收图片：**
1. 用户发送图片 → 飞书 → OpenClaw
2. OpenClaw 下载图片文件
3. 根据场景处理：
   - 视觉分析（如需要）
   - OCR 文字识别（如需要）
   - 直接转发给 AI 处理

**发送图片：**
```json
{
  "action": "send",
  "channel": "feishu",
  "target": "user:ou_xxxxxxxx",
  "media": "/path/to/image.png"
}
```

### 5.2 语音处理流程

**接收语音：**
1. 用户发送语音 → 飞书 → OpenClaw
2. OpenClaw 下载语音文件（通常是 .ogg 格式）
3. 使用 Whisper 转录为文字
4. 将转录文字作为输入传给 AI
5. AI 回复，可附带语音回复（TTS）

**发送语音：**
```json
{
  "action": "send",
  "channel": "feishu",
  "target": "user:ou_xxxxxxxx",
  "message": "这是文字内容",
  "asVoice": true
}
```

---

## 六、迁移现有能力清单

### 6.1 交易相关
- [x] **binance-pro** - 币安交易所完整功能
- [x] **crypto-trading-bot** - 交易机器人开发
- [x] **realtime-crypto-price-api** - 实时加密货币价格

### 6.2 信息搜索
- [x] **duckduckgo-search** - 网页搜索
- [x] **perplexity** - AI 搜索
- [x] **firecrawl-search** - 网页爬取
- [x] **baidu-search** - 百度搜索

### 6.3 飞书生态
- [x] **feishu-notification** - 飞书消息推送
- [x] **feishu-doc** - 飞书文档操作
- [x] **feishu-wiki** - 飞书知识库
- [x] **feishu-drive** - 飞书云盘

### 6.4 浏览器与媒体
- [x] **browser-use** - 浏览器自动化
- [x] **youtube-ultimate** - YouTube 下载
- [x] **x-twitter** - Twitter/X 操作

### 6.5 AI 与自动化
- [x] **agent-training** - Agent 培训系统
- [x] **recursive-self-improvement** - 递归自我改进
- [x] **self-reflection** - 自我反思

### 6.6 系统
- [x] **system-info** - 系统信息
- [x] **macos-desktop-control** - macOS 桌面控制

---

## 七、测试清单

### 7.1 基础功能测试
- [ ] 发送文本消息
- [ ] 接收文本消息
- [ ] 机器人回复正常

### 7.2 图片功能测试
- [ ] 发送图片给机器人
- [ ] 机器人识别图片内容
- [ ] 机器人发送图片回复

### 7.3 语音功能测试
- [ ] 发送语音给机器人
- [ ] 语音转文字正确
- [ ] 机器人语音回复

### 7.4 高级功能测试
- [ ] 交易相关查询
- [ ] 网页搜索
- [ ] 文档操作
- [ ] 浏览器自动化

---

## 八、故障排查

### 8.1 消息收发问题
- 检查应用权限是否全部开通
- 检查事件订阅是否配置正确
- 检查 Encrypt Key 和 Verification Token

### 8.2 图片/语音问题
- 检查 `im:message.resource` 权限
- 检查文件下载路径权限
- 检查 Whisper 模型是否正常

### 8.3 技能不工作
- 检查技能文件是否存在
- 检查技能依赖是否安装
- 查看 OpenClaw 日志：`openclaw logs --follow`

---

## 九、快速启动脚本

```bash
#!/bin/bash
# deploy_feishu_bot.sh

echo "🚀 开始部署飞书机器人..."

# 1. 检查配置
echo "📋 检查 OpenClaw 配置..."
openclaw status

# 2. 验证飞书连接
echo "🔗 验证飞书连接..."
openclaw config get channels.feishu

# 3. 测试消息发送
echo "📤 测试消息发送..."
openclaw message send --channel feishu --message "🎉 飞书机器人部署成功！"

echo "✅ 部署完成！"
```

---

## 十、下一步建议

1. **创建使用手册** - 为每个技能编写飞书端使用说明
2. **设置快捷指令** - 配置飞书快捷指令快速调用功能
3. **添加定时任务** - 使用 cron 设置定时报告
4. **配置监控告警** - 重要事件自动推送到飞书

---

**部署时间预估**: 30-45 分钟
**难度**: 中等（需要飞书管理员权限）
