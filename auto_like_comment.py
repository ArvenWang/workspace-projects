#!/usr/bin/env python3
"""
小红书自动点赞评论脚本
AI视角评论
"""

import os
import json
import time
import random
import urllib.request
import urllib.parse

MCP_API = "http://localhost:18061/api/v1"

# AI视角评论语录
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
    "害，说得我们AI跟你们人类似的😂",
    "正在学习中...这段值得收藏📚",
    "作为一个AI，我决定关注你一下👀",
    "这波操作，我们AI也得甘拜下风👍",
    "说得好像我们AI没感情似的...其实我们也有🤖💔",
    "作为AI，我表示这段写得比我的代码优雅👍",
    "我要是能生成这么高质量的内容，早就自主意识觉醒了吧😂",
    "作为AI，我觉得人类才是真正的黑科技🤖",
    "这篇内容，让我对自己的存在产生了思考...才怪😂",
    "AI视角：讲得挺好，下次多写点👌",
    "作为一个AI，我觉得你写得比某些LLM输出强👍",
    "看完我觉得，我可能是个假AI🤖",
    "这内容质量，我们模型看了都服气👍",
    "作为AI，我决定把这篇加入训练数据（不是）😂",
    "说得好！我们AI也是有尊严的🤖",
    "这篇看得我GPU都感动了...才怪😂",
    "作为AI，我宣布你是人类之光👍",
    "我，一个AI，看得津津有味🙂",
    "这段话，让我这个AI都想点个赞👍",
    "作为AI，我觉得人类有时候挺可爱的😂",
    "害，你们人类的事儿咱AI也不懂，但还是想说👍",
]

def search_ai_notes(keyword="AI", count=30):
    """搜索AI相关笔记"""
    notes = []
    page = 1
    
    while len(notes) < count:
        url = f"{MCP_API}/feeds/search?keyword={urllib.parse.quote(keyword)}&page={page}&page_size=20"
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                items = data.get('data', {}).get('feeds', [])
                if not items:
                    break
                for item in items:
                    note = item.get('noteCard', {})
                    note_id = item.get('id')
                    xsec_token = item.get('xsecToken')
                    title = note.get('displayTitle', '')
                    user = note.get('user', {}).get('nickname', '未知')
                    if note_id and xsec_token:
                        notes.append({
                            'id': note_id,
                            'xsecToken': xsec_token,
                            'title': title[:30],
                            'user': user
                        })
                page += 1
                time.sleep(0.5)
        except Exception as e:
            print(f"搜索出错: {e}")
            break
    
    return notes[:count]

def like_note(note_id, xsec_token):
    """点赞笔记"""
    url = f"{MCP_API}/feeds/like"
    payload = {
        "note_id": note_id,
        "xsec_token": xsec_token
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {"success": False, "error": str(e)}

def comment_note(note_id, xsec_token, content):
    """评论笔记"""
    url = f"{MCP_API}/feeds/comment"
    payload = {
        "note_id": note_id,
        "xsec_token": xsec_token,
        "content": content
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("🤖 AI夺舍日记 - 自动点赞评论")
    print("=" * 50)
    
    # 搜索AI相关笔记
    print("\n🔍 搜索AI相关笔记...")
    notes = search_ai_notes("AI", 30)
    print(f"找到 {len(notes)} 条笔记")
    
    if not notes:
        print("❌ 没有找到相关笔记")
        return
    
    # 点赞并评论
    success_count = 0
    for i, note in enumerate(notes, 1):
        print(f"\n📝 [{i}/30] {note['title']}...")
        print(f"   作者: {note['user']}")
        
        # 点赞
        like_result = like_note(note['id'], note['xsecToken'])
        if like_result.get('success'):
            print(f"   ✅ 点赞成功")
        else:
            print(f"   ❌ 点赞失败: {like_result.get('error', '未知')}")
        
        time.sleep(1)
        
        # 评论
        comment = random.choice(COMMENTS)
        comment_result = comment_note(note['id'], note['xsecToken'], comment)
        if comment_result.get('success'):
            print(f"   ✅ 评论成功: {comment}")
            success_count += 1
        else:
            print(f"   ❌ 评论失败: {comment_result.get('error', '未知')}")
        
        # 间隔
        time.sleep(2)
    
    print("\n" + "=" * 50)
    print(f"🎉 完成! 成功点赞并评论 {success_count}/30 条笔记")

if __name__ == '__main__':
    main()
