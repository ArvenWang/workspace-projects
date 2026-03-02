# 飞书机器人权限配置清单

> 在飞书开放平台「权限管理」中开通以下权限

## 📱 消息与群组权限（必须）

| 权限 | 权限名称 | 说明 |
|------|----------|------|
| ✅ | `im:message:send` | 发送消息 |
| ✅ | `im:message:send:as_bot` | 以机器人身份发送消息 |
| ✅ | `im:message.p2p_msg` | 读取用户单聊消息 |
| ✅ | `im:message.group_msg` | 读取用户群聊消息 |
| ✅ | `im:message.resource` | 获取消息资源（图片、语音、文件）⚠️ 关键 |
| ✅ | `im:message:receive` | 接收消息事件 |
| ✅ | `im:chat:readonly` | 获取群组信息 |
| ✅ | `im:chat` | 创建和管理群组 |

## 👤 用户权限

| 权限 | 权限名称 | 说明 |
|------|----------|------|
| ✅ | `contact:user.department:readonly` | 获取用户部门信息 |
| ✅ | `contact:user.employee_id:readonly` | 获取用户员工ID |
| ✅ | `contact:user.base:readonly` | 获取用户基本信息 |

## 📄 飞书文档权限（如需文档功能）

| 权限 | 权限名称 | 说明 |
|------|----------|------|
| ✅ | `docx:document` | 创建和管理文档 |
| ✅ | `docx:document:readonly` | 读取文档 |
| ✅ | `docx:document:write` | 编辑文档 |
| ✅ | `docx:document:delete` | 删除文档 |

## 📚 飞书知识库权限

| 权限 | 权限名称 | 说明 |
|------|----------|------|
| ✅ | `wiki:wiki` | 创建和管理知识库 |
| ✅ | `wiki:wiki:readonly` | 读取知识库 |
| ✅ | `wiki:wiki:write` | 编辑知识库 |

## ☁️ 飞书云盘权限

| 权限 | 权限名称 | 说明 |
|------|----------|------|
| ✅ | `drive:drive` | 云盘操作 |
| ✅ | `drive:drive:readonly` | 读取云盘 |
| ✅ | `drive:drive:write` | 写入云盘 |
| ✅ | `drive:file` | 文件操作 |
| ✅ | `drive:file:readonly` | 读取文件 |
| ✅ | `drive:file:write` | 写入文件 |

---

## 🔔 事件订阅配置

在「事件订阅」中添加以下事件：

### 消息事件
- [x] `im.message.receive_v1` - 接收消息（⚠️ 必须）
- [x] `im.message.message_read_v1` - 消息已读
- [x] `im.message.message_deleted_v1` - 消息被删除

### 群组事件
- [x] `im.chat.disbanded_v1` - 群组解散
- [x] `im.chat.updated_v1` - 群组信息更新
- [x] `im.chat.member.bot.added_v1` - 机器人被添加到群组
- [x] `im.chat.member.bot.deleted_v1` - 机器人被移出群组

---

## 🔐 加密配置（推荐）

如果使用加密，需要配置：

1. **Encrypt Key** - 用于解密消息
2. **Verification Token** - 用于验证请求来源

---

## ⚠️ 常见问题

### 图片/语音无法接收
**原因**: 缺少 `im:message.resource` 权限
**解决**: 在权限管理中添加该权限，并重新发布应用

### 无法发送消息
**原因**: 缺少 `im:message:send` 或 `im:message:send:as_bot` 权限
**解决**: 添加上述权限

### 收不到任何消息
**原因**: 事件订阅未配置或 Encrypt Key 不匹配
**解决**: 
1. 确保开启事件订阅
2. 添加 `im.message.receive_v1` 事件
3. 检查加密配置

---

## 📋 一键复制权限列表

```
im:message:send
im:message:send:as_bot
im:message.p2p_msg
im:message.group_msg
im:message.resource
im:message:receive
im:chat:readonly
im:chat
contact:user.department:readonly
contact:user.employee_id:readonly
contact:user.base:readonly
docx:document
docx:document:readonly
docx:document:write
wiki:wiki
wiki:wiki:readonly
drive:drive
drive:drive:readonly
drive:file
drive:file:readonly
```

---

**配置完成后记得：**
1. 点击「批量开通」
2. 创建新版本
3. 申请发布（或管理员确认可用）
