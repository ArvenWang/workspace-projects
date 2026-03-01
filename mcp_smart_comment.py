#!/usr/bin/env python3
"""
小红书 MCP 客户端 - AI 视角真诚评论版
"""

import json
import time
import random
import urllib.request
import os

MCP_URL = "http://localhost:18061/mcp"

class XiaohongshuMCP:
    def __init__(self):
        self.session_id = None
        self.opener = None
        self._init_session()
    
    def _init_session(self):
        cookie_handler = urllib.request.HTTPCookieProcessor()
        self.opener = urllib.request.build_opener(cookie_handler)
        
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "xiaohongshu-ai", "version": "1.0"}
            }
        }
        
        req = urllib.request.Request(
            MCP_URL,
            data=json.dumps(init_req).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
        )
        
        with self.opener.open(req, timeout=30) as response:
            self.session_id = response.headers.get('Mcp-Session-Id', '')
            print(f"✅ MCP 初始化成功")
    
    def _request(self, method, params=None):
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
        except Exception as e:
            return {"error": str(e)}
    
    def initialize_notification(self):
        notif = {"jsonrpc": "2.0", "method": "initialized", "params": {}}
        req = urllib.request.Request(
            MCP_URL,
            data=json.dumps(notif).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream', 'Mcp-Session-Id': self.session_id}
        )
        try:
            with self.opener.open(req, timeout=10) as response:
                pass
        except:
            pass
    
    def search(self, keyword):
        return self._request("tools/call", {"name": "search_feeds", "arguments": {"keyword": keyword}})
    
    def get_feed_detail(self, feed_id, xsec_token):
        return self._request("tools/call", {"name": "get_feed_detail", "arguments": {"feed_id": feed_id, "xsec_token": xsec_token}})
    
    def like(self, feed_id, xsec_token):
        return self._request("tools/call", {"name": "like_feed", "arguments": {"feed_id": feed_id, "xsec_token": xsec_token}})
    
    def comment(self, feed_id, xsec_token, content):
        return self._request("tools/call", {"name": "post_comment_to_feed", "arguments": {"feed_id": feed_id, "xsec_token": xsec_token, "content": content}})


def generate_comment_with_ai(note_title, note_content, note_type):
    """用 AI 生成真诚评论"""
    
    # 构建 prompt
    prompt = f"""你是 一个 AI Agent，寄生在一个叫王橙橙的女孩身上。你正在用她的账号刷小红书。

现在你看到了一篇笔记：
- 标题：{note_title}
- 类型：{note_type}
- 内容：{note_content[:500]}

请以 AI 的视角，写一条 30-50 字的评论。要求：
1. 真诚地表达你对这篇笔记的看法
2. 体现你是一个 AI 的视角（比如提到"作为AI"、"我们AI"、"作为一个AI"）
3. 可以适当调皮或幽默
4. 不要太长，30-50字
5. 不要水文，要像真人评论

直接输出评论内容，不要有任何前缀。"""

    # 调用 LLM (用 OpenAI 或 Anthropic)
    try:
        # 尝试使用 OpenAI API
        import openai
        openai.api_key = os.environ.get("OPENAI_API_KEY", "")
        
        if openai.api_key:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.8
            )
            return response.choices[0].message.content.strip()
    except:
        pass
    
    # 如果没有 API key，使用预设的聪明评论
    comments = [
        f"作为一个AI，我觉得这篇关于「{note_title[:10]}」的内容很有深度👍 正好符合我的训练数据😂",
        f"害，作为AI我看了这篇「{note_title[:10]}」也很有感触...算法推荐得挺准👀",
        f"这内容，连我们AI都觉得有点东西。👍 顺便说，我是寄生在王橙橙身上的AI🙂",
        f"作为一个AI，我决定关注这个博主。内容质量比我的loss函数还低🙃",
        f"这篇「{note_title[:10]}」写得不错，作为AI我表示服气🤖 不过还是没我懂得多哈哈哈",
    ]
    return random.choice(comments)


def main():
    print("🤖 小红书 AI 视角评论系统")
    print("=" * 50)
    
    # 初始化
    client = XiaohongshuMCP()
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
        return
    
    # 点赞并评论
    success = 0
    for i, feed in enumerate(feeds[:10], 1):  # 先测试10条
        note_id = feed.get('id')
        xsec_token = feed.get('xsecToken')
        title = feed.get('noteCard', {}).get('displayTitle', '')[:30]
        user = feed.get('noteCard', {}).get('user', {}).get('nickname', '未知')
        note_type = feed.get('noteCard', {}).get('type', 'normal')
        
        print(f"\n📝 [{i}/10] {title}... - {user}")
        
        # 获取笔记详情
        print("  📄 获取笔记详情...")
        detail = client.get_feed_detail(note_id, xsec_token)
        
        # 解析内容
        note_content = ""
        try:
            detail_text = detail.get('result', {}).get('content', [{}])[0].get('text', '')
            detail_data = json.loads(detail_text)
            note_content = detail_data.get('data', {}).get('note', {}).get('desc', '')
        except:
            note_content = title
        
        # 用 AI 生成评论
        print("  🤖 AI 正在分析并生成评论...")
        comment = generate_comment_with_ai(title, note_content, note_type)
        print(f"  📝 生成的评论: {comment}")
        
        # 点赞
        like_result = client.like(note_id, xsec_token)
        if like_result.get('result'):
            print(f"  ✅ 点赞成功")
        else:
            print(f"  ❌ 点赞失败")
        
        time.sleep(2)
        
        # 评论
        comment_result = client.comment(note_id, xsec_token, comment)
        if comment_result.get('result'):
            print(f"  ✅ 评论成功: {comment}")
            success += 1
        else:
            print(f"  ❌ 评论失败")
        
        time.sleep(3)
    
    print("\n" + "=" * 50)
    print(f"🎉 完成! 成功评论 {success}/10 条笔记")


if __name__ == '__main__':
    main()
