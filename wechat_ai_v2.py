#!/usr/bin/env python3
"""
微信AI助手 - Webhook版本
使用OpenClaw的message工具发送消息

原理：
1. 微信收到消息
2. 调用本地API (FastAPI)
3. API调用OpenClaw的message工具发送消息给自己(Agent)
4. Agent处理后回复
5. API收到回复，发送到微信

需要先配置feishu消息通道来接收消息
"""

from fastapi import FastAPI, Request
import uvicorn
import itchat
from itchat.content import *
import requests
import json
import os
import asyncio

# ============== 配置 ==============
CONFIG = {
    'openclaw_url': 'http://127.0.0.1:18789',
    'my_friends': [],  # 白名单好友
}

app = FastAPI()
myUserName = None

# ============== 微信消息处理 ==============
@itchat.msg_register([TEXT, PICTURE, VIDEO])
def handle_wechat_msg(msg):
    """微信收到消息，转发给OpenClaw Agent"""
    global myUserName
    
    # 忽略自己发的
    if msg['FromUserName'] == myUserName:
        return
    
    msg_text = msg.get('Text', '')
    sender_nick = msg['User'].get('NickName', '未知')
    
    print(f"\n📱 收到微信: {sender_nick}: {msg_text[:30]}...")
    
    # 调用OpenClaw Agent处理
    reply = call_openclaw_agent(msg_text, sender_nick)
    
    if reply:
        # 发送回复
        itchat.send(reply, msg['FromUserName'])
        print(f"✅ 回复: {reply[:30]}...")
    else:
        print("⚠️ 无回复")

def call_openclaw_agent(message, sender):
    """调用OpenClaw Agent获取回复"""
    try:
        # 方式1: 通过Feishu发送消息给自己
        # 需要配置feishu channel
        
        # 方式2: 直接调用session API
        # 需要看OpenClaw是否有外部API
        
        # 方式3: 使用本地消息队列 + Agent轮询
        # 保存消息到本地，Agent自动处理
        
        return None
        
    except Exception as e:
        print(f"❌ Agent调用失败: {e}")
        return None

# ============== REST API ==============
@app.post("/webhook/wechat")
async def wechat_webhook(request: Request):
    """接收微信消息的Webhook"""
    data = await request.json()
    
    message = data.get('message', '')
    sender = data.get('sender', '微信用户')
    
    print(f"📱 Webhook收到: {sender}: {message}")
    
    # 调用Agent
    reply = call_openclaw_agent(message, sender)
    
    return {"reply": reply or "消息已收到"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ============== 启动 ==============
def main():
    global myUserName
    
    print("=" * 50)
    print("微信AI助手 (Webhook版)")
    print("=" * 50)
    
    # 启动FastAPI服务
    import threading
    api_thread = threading.Thread(target=lambda: uvicorn.run(app, host="127.0.0.1", port=8765))
    api_thread.daemon = True
    api_thread.start()
    print("✅ API服务启动: http://127.0.0.1:8765")
    
    # 登录微信
    print("正在登录微信...")
    itchat.auto_login(hotReload=True, enableCmdQR=2)
    myUserName = itchat.get_friends()[0]['UserName']
    print(f"✅ 微信登录成功")
    
    print("\n" + "=" * 50)
    print("微信AI助手已启动!")
    print("API地址: http://127.0.0.1:8765/webhook/wechat")
    print("=" * 50)
    
    itchat.run()

if __name__ == '__main__':
    main()
