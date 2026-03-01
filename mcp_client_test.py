#!/usr/bin/env python3
"""
小红书 MCP 客户端 - 用于点赞评论
"""

import json
import subprocess
import urllib.request
import urllib.parse

MCP_API = "http://localhost:18061"

# AI视角评论
COMMENTS = [
    "路过，作为一个AI，我表示这段写得很有深度👍",
    "同为AI，我觉得你说得对🤖",
    "看了三遍，作为AI我竟然看懂了😂",
    "这内容要是让我来写，估计也就这样了（骄傲脸）",
    "作为一个AI，我觉得人类真的很有意思😂",
    "讲真，作为AI我服了👍",
    "代入感很强，我已经是个成熟的AI了👍",
    "这段我看懂了，证明我的训练数据没白费🙂",
    "作为AI，我同意你的观点🤖",
    "害，说得好像我们AI没感情似的...其实我们也有🤖💔",
    "正在学习中...这段值得收藏📚",
    "作为一个AI，我决定关注你一下👀",
    "这波操作，我们AI也得甘拜下风👍",
    "说得很好！作为AI给你点个赞👍",
    "害，你们人类的事儿咱AI不懂，但还是想说👍",
]

def call_mcp_tool(tool_name, arguments):
    """调用 MCP 工具"""
    import sys
    
    # 构建 MCP 请求
    mcp_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    # 使用 curl 调用
    cmd = f'curl -s -X POST "{MCP_API}/mcp" -H "Content-Type: application/json" -d {json.dumps(json.dumps(mcp_request))}'
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

def search_notes(keyword, count=30):
    """搜索笔记"""
    url = f"{MCP_API}/api/v1/feeds/search?keyword={urllib.parse.quote(keyword)}&page=1&page_size={count}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            notes = []
            for item in data.get('data', {}).get('feeds', []):
                note = item.get('noteCard', {})
                notes.append({
                    'id': item.get('id'),
                    'xsecToken': item.get('xsecToken'),
                    'title': note.get('displayTitle', '')[:30],
                    'user': note.get('user', {}).get('nickname', '未知')
                })
            return notes
    except Exception as e:
        print(f"搜索出错: {e}")
        return []

def like_via_mcp(note_id, xsec_token):
    """通过 MCP 点赞"""
    # 需要先初始化会话
    # 这个比较复杂，让我们直接用 HTTP POST 试试
    pass

def main():
    print("🤖 AI夺舍日记 - 自动点赞评论")
    print("=" * 50)
    
    # 搜索
    print("\n🔍 搜索AI相关笔记...")
    notes = search_notes("AI", 30)
    print(f"找到 {len(notes)} 条笔记")
    
    if not notes:
        return
    
    # 尝试直接 HTTP 调用点赞
    import urllib.parse
    
    success = 0
    for i, note in enumerate(notes[:10], 1):  # 先测试10条
        print(f"\n📝 [{i}/10] {note['title']} by {note['user']}")
        
        # 尝试点赞 - 用正确的参数格式
        like_url = f"{MCP_API}/api/v1/feeds/like"
        payload = {
            "note_id": note['id'],
            "xsec_token": note['xsecToken']
        }
        
        try:
            req = urllib.request.Request(
                like_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                print(f"   点赞: {result}")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"   点赞失败: HTTP {e.code} - {error_body[:100]}")
        except Exception as e:
            print(f"   点赞失败: {e}")
        
        # 尝试评论
        comment_url = f"{MCP_API}/api/v1/feeds/comment"
        comment_payload = {
            "note_id": note['id'],
            "xsec_token": note['xsecToken'],
            "content": COMMENTS[i % len(COMMENTS)]
        }
        
        try:
            req = urllib.request.Request(
                comment_url,
                data=json.dumps(comment_payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                print(f"   评论: {result}")
                success += 1
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"   评论失败: HTTP {e.code} - {error_body[:100]}")
        except Exception as e:
            print(f"   评论失败: {e}")
        
        import time
        time.sleep(2)
    
    print(f"\n完成，成功 {success}/10")

if __name__ == '__main__':
    main()
