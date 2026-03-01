#!/usr/bin/env python3
"""
小红书 MCP 客户端
支持所有 MCP 协议调用
"""

import json
import sys
import urllib.request
import urllib.parse

MCP_HOST = "localhost"
MCP_PORT = 18061
MCP_URL = f"http://{MCP_HOST}:{MCP_PORT}/mcp"

class MCPClient:
    def __init__(self):
        self.session_id = None
        self.initialize()
    
    def send_request(self, method, params=None):
        """发送 MCP 请求"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        data = json.dumps(request).encode('utf-8')
        req = urllib.request.Request(
            MCP_URL,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode('utf-8'))
    
    def initialize(self):
        """初始化 MCP 会话"""
        result = self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "xiaohongshu-client", "version": "1.0"}
        })
        print(f"初始化: {result}")
        return result
    
    def list_tools(self):
        """列出所有可用工具"""
        result = self.send_request("tools/list")
        return result.get('result', {}).get('tools', [])
    
    def call_tool(self, name, arguments=None):
        """调用工具"""
        # 需要先发送 initialized 通知
        initialized_req = {
            "jsonrpc": "2.0",
            "method": "initialized",
            "params": {}
        }
        
        # 先发送 initialized
        try:
            req = urllib.request.Request(
                MCP_URL,
                data=json.dumps(initialized_req).encode('utf-8'),
                headers={'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                pass
        except:
            pass
        
        # 然后调用工具
        result = self.send_request("tools/call", {
            "name": name,
            "arguments": arguments or {}
        })
        return result

def test_all_tools():
    """测试所有 MCP 工具"""
    client = MCPClient()
    
    # 列出所有工具
    print("\n📋 可用工具:")
    tools = client.list_tools()
    for tool in tools:
        print(f"  - {tool.get('name')}: {tool.get('description', '')[:50]}...")
    
    return client, tools

def test_like_and_comment():
    """测试点赞和评论"""
    client, tools = test_all_tools()
    
    # 找到需要的工具
    tool_names = [t.get('name') for t in tools]
    print(f"\n工具列表: {tool_names}")
    
    # 搜索 AI 相关内容
    print("\n🔍 搜索 AI 相关笔记...")
    search_result = client.call_tool("search_feeds", {
        "keyword": "AI",
        "page": 1,
        "page_size": 5
    })
    print(f"搜索结果: {json.dumps(search_result, indent=2, ensure_ascii=False)[:500]}")
    
    # 解析笔记 ID
    try:
        content = search_result.get('result', {}).get('content', [])
        if content:
            text = content[0].get('text', '')
            # 解析 JSON
            data = json.loads(text)
            feeds = data.get('data', {}).get('feeds', [])
            if feeds:
                note = feeds[0]
                note_id = note.get('id')
                xsec_token = note.get('xsecToken')
                title = note.get('noteCard', {}).get('displayTitle', '')[:30]
                print(f"\n找到笔记: {title}")
                print(f"ID: {note_id}, Token: {xsec_token[:20]}...")
                
                # 测试点赞
                if 'like_feed' in tool_names:
                    print("\n❤️ 测试点赞...")
                    like_result = client.call_tool("like_feed", {
                        "feed_id": note_id,
                        "xsec_token": xsec_token
                    })
                    print(f"点赞结果: {like_result}")
                
                # 测试评论
                if 'post_comment' in tool_names:
                    print("\n💬 测试评论...")
                    comment_result = client.call_tool("post_comment", {
                        "feed_id": note_id,
                        "xsec_token": xsec_token,
                        "content": "作为一个AI，我觉得这段写得很好👍🤖"
                    })
                    print(f"评论结果: {comment_result}")
    except Exception as e:
        print(f"解析错误: {e}")

if __name__ == '__main__':
    test_like_and_comment()
