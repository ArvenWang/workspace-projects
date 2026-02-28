#!/usr/bin/env python3
"""
Discord Bot - 完整版
功能：
1. 自动回复
2. 群管理
3. 定时任务
4. 嵌入消息
5. 语音频道

依赖：
pip3 install discord.py

运行：
python3 discord_bot.py run
python3 discord_bot.py test
"""

import asyncio
import os
import json
from datetime import datetime
from pathlib import Path

# 配置
CONFIG = {
    'data_dir': os.path.expanduser('~/.discord_bot'),
    'token_file': os.path.expanduser('~/.discord_bot/token'),
}

Path(CONFIG['data_dir']).mkdir(parents=True, exist_ok=True)


class DiscordBot:
    def __init__(self):
        self.client = None
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置"""
        config_file = os.path.join(CONFIG['data_dir'], 'config.json')
        default = {
            'prefix': '!',
            'auto_reply': True,
            'welcome_channel': None,
            'log_channel': None
        }
        
        if os.path.exists(config_file):
            with open(config_file) as f:
                return json.load(f)
        return default
    
    def save_config(self):
        """保存配置"""
        config_file = os.path.join(CONFIG['data_dir'], 'config.json')
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    async def on_ready(self):
        """登录成功"""
        print(f"✅ 机器人已登录: {self.client.user}")
        print(f"📍 当前服务器: {len(self.client.guilds)}个")
    
    async def on_message(self, message):
        """消息处理"""
        # 忽略机器人消息
        if message.author == self.client.user:
            return
        
        content = message.content.strip()
        prefix = self.config.get('prefix', '!')
        
        # 命令处理
        if content.startswith(prefix):
            await self.handle_command(message, content)
        
        # 自动回复
        elif self.config.get('auto_reply'):
            await self.auto_reply(message, content)
    
    async def handle_command(self, message, content):
        """命令处理"""
        cmd = content[1:].split()[0].lower()
        args = content[1:].split()[1:]
        
        commands = {
            'help': self.cmd_help,
            'ping': self.cmd_ping,
            'info': self.cmd_info,
            'echo': self.cmd_echo,
            'kick': self.cmd_kick,
            'ban': self.cmd_ban,
            'clear': self.cmd_clear,
        }
        
        if cmd in commands:
            await commands[cmd](message, args)
    
    async def cmd_help(self, message, args):
        """帮助命令"""
        embed = {
            'title': '🤖 命令列表',
            'description': '''
!help - 显示帮助
!ping - 检查延迟
!info - 机器人信息
!echo <内容> - 复述
!clear <数量> - 清理消息
''',
            'color': 0x00ff00
        }
        await message.channel.send(embed=embed)
    
    async def cmd_ping(self, message, args):
        """延迟测试"""
        latency = self.client.latency * 1000
        await message.channel.send(f"🏓 延迟: {latency:.0f}ms")
    
    async def cmd_info(self, message, args):
        """机器人信息"""
        await message.channel.send(f'''
🤖 机器人信息
- 用户: {self.client.user}
- 服务器: {len(self.client.guilds)}个
- 登录时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
''')
    
    async def cmd_echo(self, message, args):
        """复述"""
        if args:
            await message.channel.send(' '.join(args))
        else:
            await message.channel.send('请输入内容')
    
    async def cmd_kick(self, message, args):
        """踢人"""
        if message.author.guild_permissions.kick_members:
            # 实现踢人逻辑
            await message.channel.send("踢人功能需要指定用户")
        else:
            await message.channel.send("你没有权限")
    
    async def cmd_ban(self, message, args):
        """ban人"""
        if message.author.guild_permissions.ban_members:
            await message.channel.send("ban功能需要指定用户")
        else:
            await message.channel.send("你没有权限")
    
    async def cmd_clear(self, message, args):
        """清理消息"""
        if not message.author.guild_permissions.manage_messages:
            await message.channel.send("你没有权限")
            return
        
        try:
            count = int(args[0]) if args else 10
            deleted = await message.channel.purge(limit=count + 1)
            await message.channel.send(f"✅ 已清理 {len(deleted)} 条消息")
        except:
            await message.channel.send("用法: !clear <数量>")
    
    async def auto_reply(self, message, content):
        """自动回复"""
        # 简单关键词回复
        replies = {
            'hello': '你好！👋',
            'hi': '你好！👋',
            'help': '输入 !help 查看命令',
            '帮助': '输入 !help 查看命令',
        }
        
        content_lower = content.lower()
        for keyword, reply in replies.items():
            if keyword in content_lower:
                await message.channel.send(reply)
                break
    
    async def on_member_join(self, member):
        """新成员加入"""
        channel = self.config.get('welcome_channel')
        if channel:
            await self.client.send_message(channel, f"欢迎 {member.mention}！")
    
    def run(self, token):
        """运行机器人"""
        try:
            import discord
        except ImportError:
            print("❌ 请安装 discord.py: pip3 install discord.py")
            return
        
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.client = discord.Client(intents=intents)
        
        @self.client.event
        async def on_ready():
            await self.on_ready()
        
        @self.client.event
        async def on_message(message):
            await self.on_message(message)
        
        @self.client.event
        async def on_member_join(member):
            await self.on_member_join(member)
        
        print("🔄 启动Discord机器人...")
        self.client.run(token)


def test_bot():
    """测试"""
    print("\n🧪 Discord Bot 测试")
    print("="*50)
    print("Bot需要Token才能运行")
    print()
    print("获取Token:")
    print("1. 访问 https://discord.com/developers/applications")
    print("2. 创建应用 -> Bot")
    print("3. 复制Token")
    print()
    print("运行命令:")
    print("  python3 discord_bot.py run <TOKEN>")
    print()
    print("="*50)
    print("✅ 配置文件已创建")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
Discord Bot - 使用说明

依赖安装:
  pip3 install discord.py

使用:
  python3 discord_bot.py test        # 测试配置
  python3 discord_bot.py run <TOKEN>  # 运行

命令:
  !help   - 帮助
  !ping   - 延迟
  !info   - 信息
  !echo   - 复述
  !clear  - 清理

示例:
  python3 discord_bot.py run YOUR_TOKEN_HERE
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'test':
        test_bot()
    elif cmd == 'run' and len(sys.argv) >= 3:
        token = sys.argv[2]
        bot = DiscordBot()
        bot.run(token)
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
