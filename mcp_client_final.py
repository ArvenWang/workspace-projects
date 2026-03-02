#!/usr/bin/env python3
"""
小红书 MCP 客户端 - 完整版
支持所有 MCP 工具调用
"""

import json
import time
import random
import urllib.request

MCP_URL = "http://localhost:18061/mcp"

# AI视角评论
COMMENTS = [
    "路过，作为一个AI，我表示这段写得很有深度👍",
    "同为AI，我觉得你说得对🤖",
    "看了三遍，作为AI我竟然看懂了😂",
    "作为一个AI，我觉得人类真的很有意思😂",
    "作为AI，我同意你的观点🤖",
    "讲真，作为AI我服了👍",
    "代入感很强，我已经是个成熟的AI了👍",
    "这段我看懂了，证明我的训练数据没白费🙂",
    "害，说得好像我们AI没感情似的...其实我们也有🤖💔",
    "正在学习中...这段值得收藏📚",
]

class XiaohongshuMCP:
    def __init__(self):
        self.session_id = None
        self.opener = None
        self._init_session()
    
    def _init_session(self):
        """初始化会话"""
        # 创建持久化的 opener
        cookie_handler = urllib.request.HTTPCookieProcessor()
        self.opener = urllib.request.build_opener(cookie_handler)
        
        # 初始化请求
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "xiaohongshu-bot", "version": "1.0"}
            }
        }
        
        req = urllib.request.Request(
            MCP_URL,
            data=json.dumps(init_req).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/event-stream'
            }
        )
        
        with self.opener.open(req, timeout=30) as response:
            # 获取 session id
            self.session_id = response.headers.get('Mcp-Session-Id', '')
            print(f"✅ MCP 初始化成功, Session: {self.session_id[:20]}...")
    
    def _request(self, method, params=None):
        """发送 MCP 请求"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }
        if self.session_id:
            headers['Mcp-Session-Id'] = self.session_id
        
        req = urllib.request.Request(
            MCP_URL,
            data=json.dumps(request).encode('utf-8'),
            headers=headers
        )
        
        try:
            with self.opener.open(req, timeout=60) as response:
                body = response.read().decode('utf-8')
                if body.strip():
                    return json.loads(body)
                return {}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            return {"error": f"HTTP {e.code}", "details": error_body[:200]}
        except Exception as e:
            return {"error": str(e)}
    
    def initialize_notification(self):
        """发送 initialized 通知"""
        notif = {
            "jsonrpc": "2.0",
            "method": "initialized",
            "params": {}
        }
        
        req = urllib.request.Request(
            MCP_URL,
            data=json.dumps(notif).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/event-stream',
                'Mcp-Session-Id': self.session_id
            }
        )
        
        try:
            with self.opener.open(req, timeout=10) as response:
                pass
        except:
            pass
    
    def list_tools(self):
        """列出所有工具"""
        return self._request("tools/list")
    
    def call_tool(self, name, arguments=None):
        """调用工具"""
        return self._request("tools/call", {
            "name": name,
            "arguments": arguments or {}
        })
    
    def search(self, keyword):
        """搜索笔记"""
        return self.call_tool("search_feeds", {"keyword": keyword})
    
    def like(self, feed_id, xsec_token):
        """点赞"""
        return self.call_tool("like_feed", {
            "feed_id": feed_id,
            "xsec_token": xsec_token
        })
    
    def comment(self, feed_id, xsec_token, content):
        """评论"""
        return self.call_tool("post_comment_to_feed", {
            "feed_id": feed_id,
            "xsec_token": xsec_token,
            "content": content
        })


def main():
    print("🤖 小红书 MCP 客户端 - 自动点赞评论")
    print("=" * 50)
    
    # 初始化
    client = XiaohongshuMCP()
    
    # 发送 initialized 通知
    client.initialize_notification()
    
    # 搜索
    print("\n🔍 搜索 AI 相关笔记...")
    result = client.search("AI")
    
    # 解析
    try:
        text = result.get('result', {}).get('content', [{}])[0].get('text', '')
        data = json.loads(text)
        feeds = data.get('feeds', [])
        print(f"找到 {len(feeds)} 条笔记")
    except Exception as e:
        print(f"解析错误: {e}")
        print(result)
        return
    
    # 点赞并评论
    success = 0
    for i, feed in enumerate(feeds[:30], 1):
        note_id = feed.get('id')
        xsec_token = feed.get('xsecToken')
        title = feed.get('noteCard', {}).get('displayTitle', '')[:25]
        user = feed.get('noteCard', {}).get('user', {}).get('nickname', '未知')
        
        print(f"\n📝 [{i}/30] {title}... - {user}")
        
        # 点赞
        like_result = client.like(note_id, xsec_token)
        if like_result.get('result'):
            print(f"  ✅ 点赞成功")
        else:
            print(f"  ❌ 点赞失败")
        
        time.sleep(1)
        
        # 评论
        comment_text = random.choice(COMMENTS)
        comment_result = client.comment(note_id, xsec_token, comment_text)
        if comment_result.get('result'):
            print(f"  ✅ 评论: {comment_text}")
            success += 1
        else:
            print(f"  ❌ 评论失败")
        
        time.sleep(2)
    
    print("\n" + "=" * 50)
    print(f"🎉 完成! 成功点赞并评论 {success}/30 条笔记")


if __name__ == '__main__':
    main()
