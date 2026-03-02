#!/usr/bin/env python3
"""
小红书 MCP 客户端 - 简化版
"""

MCP_HOST = "localhost"
MCP_PORT = 18061
MCP_URL = f"http://{MCP_HOST}:{MCP_PORT}/mcp"

class MCPClient:
    def __init__(self):
        self.request_id = 1
        self.session_id = None
    
    def _next_id(self):
        self.request_id += 1
        return self.request_id
    
    def request(self, method, params=None):
        """发送请求"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params or {}
        }
        
        data = json.dumps(request).encode('utf-8')
        req = urllib.request.Request(
            MCP_URL,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/event-stream'
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                content_type = response.headers.get('Content-Type', '')
                if 'text/event-stream' in content_type:
                    # SSE 响应
                    return self._handle_sse(response)
                else:
                    # JSON 响应
                    body = response.read().decode('utf-8')
                    return json.loads(body)
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8')
            return {"error": f"HTTP {e.code}", "details": body[:200]}
        except Exception as e:
            return {"error": str(e)}
    
    def _handle_sse(self, response):
        """处理 SSE 响应"""
        # 简单处理：读取所有内容
        chunks = []
        for line in response:
            line = line.decode('utf-8').strip()
            if line.startswith('data:'):
                data = line[5:].strip()
                if data:
                    try:
                        return json.loads(data)
                    except:
                        pass
        return {"raw": chunks}
    
    def initialize(self):
        """初始化"""
        result = self.request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        })
        print(f"初始化: {result}")
        return result
    
    def tools_list(self):
        """列出工具"""
        result = self.request("tools/list")
        return result
    
    def tools_call(self, name, arguments=None):
        """调用工具"""
        # 先发送 initialized 通知
        self.request("initialized", {})
        
        # 然后调用工具
        result = self.request("tools/call", {
            "name": name,
            "arguments": arguments or {}
        })
        return result


def test_search():
    """测试搜索"""
    client = MCPClient()
    
    # 初始化
    client.initialize()
    
    # 列出工具
    print("\n📋 工具列表:")
    tools_result = client.tools_list()
    print(json.dumps(tools_result, indent=2, ensure_ascii=False)[:500])
    
    # 测试搜索
    print("\n🔍 测试搜索:")
    search_result = client.tools_call("search_feeds", {
        "keyword": "AI",
        "page": 1,
        "page_size": 3
    })
    print(json.dumps(search_result, indent=2, ensure_ascii=False)[:1000])


def test_like():
    """测试点赞"""
    client = MCPClient()
    client.initialize()
    
    # 先搜索
    print("\n🔍 搜索笔记...")
    search = client.tools_call("search_feeds", {"keyword": "AI", "page": 1, "page_size": 3})
    
    # 解析
    try:
        text = search.get('result', {}).get('content', [{}])[0].get('text', '')
        data = json.loads(text)
        feeds = data.get('data', {}).get('feeds', [])
        
        if feeds:
            note = feeds[0]
            note_id = note.get('id')
            xsec_token = note.get('xsecToken')
            title = note.get('noteCard', {}).get('displayTitle', '')[:30]
            
            print(f"\n找到笔记: {title}")
            print(f"ID: {note_id}")
            
            # 点赞
            print("\n❤️ 测试点赞...")
            like_result = client.tools_call("like_feed", {
                "feed_id": note_id,
                "xsec_token": xsec_token
            })
            print(json.dumps(like_result, indent=2, ensure_ascii=False))
            
            # 评论
            print("\n💬 测试评论...")
            comment_result = client.tools_call("post_comment", {
                "feed_id": note_id,
                "xsec_token": xsec_token,
                "content": "作为一个AI，我给你点个赞👍🤖"
            })
            print(json.dumps(comment_result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"错误: {e}")
        print(f"搜索结果: {search}")


if __name__ == '__main__':
    test_like()
