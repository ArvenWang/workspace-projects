#!/usr/bin/env python3
"""
微信自动回复机器人
基于OpenClaw + itchat + AI

功能:
1. 自动回复微信消息
2. AI智能回复
3. 关键词触发
4. 群管理
"""

import itchat
import os
import json
from datetime import datetime

# 配置
CONFIG = {
    'reply_enabled': True,
    'ai_enabled': True,
    'keyword_replies': {
        'hello': '你好！我是AI助手',
        '帮助': '我可以帮你：1.回答问题 2.查资料 3.聊天',
        '天气': '请告诉我你想查哪个城市的天气',
    }
}

# 回复消息
@itchat.msg_register(['Text', 'Map', 'Card', 'Note', 'Sharing', 'Picture', 'Recording', 'Attachment', 'Video', 'Friends'])
def handle_message(msg):
    # 忽略自己发送的消息
    if msg['FromUserName'] == myUserName:
        return
    
    msg_type = msg['Type']
    msg_text = msg.get('Text', '')
    sender = msg['User'].get('NickName', msg['User'].get('RemarkName', '未知'))
    
    print(f"\n收到消息 | {sender} | {msg_type}: {msg_text[:30]}...")
    
    # 自动回复
    if not CONFIG['reply_enabled']:
        return
    
    # 关键词回复
    for keyword, reply in CONFIG['keyword_replies'].items():
        if keyword in msg_text:
            itchat.send(reply, msg['FromUserName'])
            print(f"-> 关键词回复: {reply}")
            return
    
    # AI回复 (需要配置API)
    if CONFIG['ai_enabled'] and msg_type == 'Text':
        # 这里可以接入GPT/Claude API
        reply = get_ai_reply(msg_text)
        if reply:
            itchat.send(reply, msg['FromUserName'])
            print(f"-> AI回复: {reply}")

def get_ai_reply(text):
    """AI回复 - 可接入各种API"""
    # TODO: 接入OpenAI/Claude API
    return None

def login():
    """登录微信"""
    print("正在登录微信...")
    itchat.auto_login(hotReload=True, enableCmdQR=2)
    print("登录成功!")

def main():
    global myUserName
    
    login()
    myUserName = itchat.get_friends()[0]['UserName']
    
    print(f"\n=== 微信自动回复机器人已启动 ===")
    print(f"我的昵称: {itchat.get_friends()[0]['NickName']}")
    print(f"功能: {'AI智能回复' if CONFIG['ai_enabled'] else '关键词回复'}")
    print("按 Ctrl+C 退出")
    print("=" * 35)
    
    itchat.run()

if __name__ == '__main__':
    main()
