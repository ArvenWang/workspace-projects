# GitHub 工作流程指南

## 账户信息
- **GitHub 账号**: ArvenWang
- **邮箱**: nefish29945344@gmail.com
- **用途**: 代码上传、拉取、项目管理

## 已配置工具

### 1. GitHub CLI (gh)
```bash
# 检查登录状态
gh auth status

# 常用命令
gh repo list                    # 列出仓库
gh repo create <name>           # 创建仓库
gh repo clone <owner>/<repo>    # 克隆仓库
gh pr create                    # 创建 Pull Request
gh issue create                 # 创建 Issue
```

### 2. Git
```bash
# 全局配置（已设置）
git config --global user.name "ArvenWang"
git config --global user.email "nefish29945344@gmail.com"

# 基本工作流程
git init                        # 初始化仓库
git add .                       # 添加所有文件
git commit -m "message"         # 提交
git push origin main            # 推送
git pull origin main            # 拉取
```

### 3. 当前工作目录
- **本地路径**: `~/.openclaw/workspace`
- **远程地址**: `https://github.com/ArvenWang/workspace-projects.git`

## 标准工作流程

### 开始新项目
```bash
cd ~/.openclaw/workspace

# 1. 创建项目目录
mkdir my-project
cd my-project

# 2. 初始化 Git
git init

# 3. 创建 GitHub 仓库
gh repo create my-project --public

# 4. 关联远程仓库
git remote add origin https://github.com/ArvenWang/my-project.git

# 5. 添加文件并推送
git add .
git commit -m "Initial commit"
git push -u origin main
```

### 日常开发
```bash
# 拉取最新代码
git pull origin main

# 创建新分支（推荐）
git checkout -b feature/my-feature

# 工作完成后
git add .
git commit -m "Add feature X"
git push origin feature/my-feature

# 创建 Pull Request
gh pr create --title "Add feature X" --body "Description"
```

## 注意事项

1. **VPN 连接**: 使用 Shadowrocket 保持网络畅通
2. **GitHub 设备验证**: 新设备登录时需要邮箱验证码
3. **Cursor 登录**: 仍需手动完成 OAuth 授权

## 快捷命令

已添加到环境：
- `gh` - GitHub CLI
- `git` - Git 版本控制
- `cursor` - Cursor 编辑器 CLI
- `codebuddy` - CodeBuddy CLI

## 待完成

- [ ] 完成 Cursor App 的 GitHub OAuth 登录
- [ ] 创建第一个正式项目仓库
- [ ] 设置 SSH Key（可选，更安全）

---
*由 OpenClaw 自动管理*
