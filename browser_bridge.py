#!/usr/bin/env python3
"""
OpenClaw 浏览器桥接服务器
通过 WebSocket 连接到用户浏览器，执行 JS 并返回结果

用法:
    python3 browser_bridge.py
    # 然后在浏览器安装 Tampermonkey + openclaw_browser_bridge.user.js
"""

import asyncio
import json
import uuid
import threading
import time
from datetime import datetime
from pathlib import Path

try:
    import websockets
except ImportError:
    print("请安装 websockets: pip install websockets")
    exit(1)


class BrowserBridge:
    """浏览器桥接服务器"""
    
    def __init__(self, host='localhost', port=18765):
        self.host = host
        self.port = port
        self.sessions = {}  # session_id -> {ws, url, title, last_seen}
        self.default_session = None
        self.results = {}   # id -> result
        self.acks = set()
        
    def register_session(self, session_id, websocket, url, title):
        """注册新会话"""
        is_new = session_id not in self.sessions
        self.sessions[session_id] = {
            'ws': websocket,
            'url': url,
            'title': title,
            'last_seen': time.time()
        }
        if is_new:
            print(f"[+] 新会话: {session_id} - {title}")
            print(f"    URL: {url}")
        else:
            print(f"[~] 会话重连: {session_id}")
        
        if self.default_session is None:
            self.default_session = session_id
    
    def unregister_session(self, session_id):
        """注销会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            print(f"[-] 会话断开: {session_id}")
            if self.default_session == session_id:
                self.default_session = list(self.sessions.keys())[0] if self.sessions else None
    
    async def handle_client(self, websocket, path):
        """处理客户端连接"""
        session_id = None
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type')
                    
                    if msg_type == 'ready':
                        session_id = data.get('sessionId')
                        url = data.get('url', '')
                        title = data.get('title', '')
                        self.register_session(session_id, websocket, url, title)
                    
                    elif msg_type == 'pong' or msg_type == 'ping':
                        self.acks.add(data.get('id', ''))
                    
                    elif msg_type == 'navigate':
                        if session_id and session_id in self.sessions:
                            self.sessions[session_id]['url'] = data.get('url', '')
                            self.sessions[session_id]['title'] = data.get('title', '')
                    
                    elif msg_type == 'result':
                        req_id = data.get('id')
                        self.results[req_id] = {
                            'success': True,
                            'data': data.get('result')
                        }
                    
                    elif msg_type == 'error':
                        req_id = data.get('id')
                        self.results[req_id] = {
                            'success': False,
                            'error': data.get('error')
                        }
                        
                except json.JSONDecodeError:
                    print("[!] JSON 解析错误")
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if session_id:
                self.unregister_session(session_id)
    
    async def execute_js(self, code, session_id=None, timeout=15):
        """执行 JS 代码"""
        if session_id is None:
            session_id = self.default_session
        
        if not session_id or session_id not in self.sessions:
            # 尝试使用任何可用的会话
            if self.sessions:
                session_id = list(self.sessions.keys())[0]
            else:
                raise Exception("没有活跃的浏览器会话")
        
        ws = self.sessions[session_id]['ws']
        req_id = str(uuid.uuid4())
        
        # 发送执行请求
        payload = json.dumps({
            'id': req_id,
            'code': code
        })
        await ws.send(payload)
        
        # 等待结果
        start_time = time.time()
        while time.time() - start_time < timeout:
            if req_id in self.results:
                result = self.results.pop(req_id)
                if result.get('success'):
                    return result.get('data')
                else:
                    raise Exception(result.get('error', 'Unknown error'))
            await asyncio.sleep(0.1)
        
        raise Exception(f"执行超时 ({timeout}s)")
    
    async def scan_page(self, session_id=None):
        """扫描页面内容"""
        code = """
(function() {
    return {
        title: document.title,
        url: window.location.href,
        html: document.documentElement.outerHTML.substring(0, 50000),
        links: Array.from(document.querySelectorAll('a')).slice(0, 20).map(a => ({
            text: a.textContent.trim().substring(0, 50),
            href: a.href
        }))
    };
})();
"""
        return await self.execute_js(code, session_id)
    
    async def click_element(self, selector, session_id=None):
        """点击元素"""
        code = f"""
(function() {{
    const el = document.querySelector('{selector}');
    if (el) {{
        el.click();
        return 'clicked: {selector}';
    }}
    return 'not found: {selector}';
}})();
"""
        return await self.execute_js(code, session_id)
    
    async def fill_form(self, selector, value, session_id=None):
        """填写表单"""
        code = f"""
(function() {{
    const el = document.querySelector('{selector}');
    if (el) {{
        el.value = `{value}`;
        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
        return 'filled: {selector} = {value}';
    }}
    return 'not found: {selector}';
}})();
"""
        return await self.execute_js(code, session_id)
    
    def get_sessions(self):
        """获取所有会话"""
        return [
            {
                'id': sid,
                'url': info['url'],
                'title': info['title'],
                'last_seen': datetime.fromtimestamp(info['last_seen']).strftime('%H:%M:%S')
            }
            for sid, info in self.sessions.items()
        ]
    
    async def start(self):
        """启动服务器"""
        print(f"🚀 浏览器桥接服务器启动: ws://{self.host}:{self.port}")
        print("📝 请在浏览器安装 Tampermonkey 扩展，然后安装 openclaw_browser_bridge.user.js")
        print("🔗 连接后即可通过 execute_js() 控制浏览器")
        print()
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            # 保持运行
            while True:
                await asyncio.sleep(1)


# 命令行界面
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenClaw 浏览器桥接')
    parser.add_argument('--host', default='localhost', help='监听地址')
    parser.add_argument('--port', type=int, default=18765, help='监听端口')
    parser.add_argument('--execute', '-e', help='直接执行 JS 代码')
    parser.add_argument('--scan', '-s', action='store_true', help='扫描当前页面')
    
    args = parser.parse_args()
    
    bridge = BrowserBridge(args.host, args.port)
    
    if args.execute:
        # 单次执行模式
        async with websockets.connect(f'ws://{args.host}:{args.port}') as ws:
            # 等待会话连接
            print("等待浏览器连接...")
            await asyncio.sleep(2)
            
            if bridge.default_session:
                result = await bridge.execute_js(args.execute)
                print("结果:", result)
            else:
                print("没有活跃的会话")
    elif args.scan:
        async with websockets.connect(f'ws://{args.host}:{args.port}') as ws:
            await asyncio.sleep(2)
            if bridge.default_session:
                result = await bridge.scan_page()
                print("页面标题:", result.get('title'))
                print("URL:", result.get('url'))
                print("链接:", result.get('links'))
            else:
                print("没有活跃的会话")
    else:
        # 服务器模式
        await bridge.start()


if __name__ == '__main__':
    asyncio.run(main())
