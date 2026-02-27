# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

### System Access (王靖文的Mac mini)

- **Host**: 192.168.50.78
- **User**: wangjingwen
- **sudo 密码**: Yourname123
- **Gateway**: ws://127.0.0.1:18789 / http://127.0.0.1:18789
- **SSH**: 已启用 (port 22)

---

### VPN / Shadowrocket

- **应用**: Shadowrocket.app (已安装)
- **代理端口**: 127.0.0.1:1082 (HTTP/HTTPS)
- **网络服务**: Shadowrocket
- **启动脚本**: `./scripts/shadowrocket.sh`
- **完整指南**: `SHADOWROCKET_GUIDE.md`

**快速启动**:
```bash
# 自动启动并配置
./scripts/shadowrocket.sh

# 或手动步骤
open -a Shadowrocket
sleep 3
networksetup -setwebproxystate "Shadowrocket" on
git config --global http.proxy http://127.0.0.1:1082
git config --global https.proxy http://127.0.0.1:1082
```

**用途**: 访问 GitHub、Google 等外网服务

---

Add whatever helps you do your job. This is your cheat sheet.
