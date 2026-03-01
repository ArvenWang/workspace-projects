#!/usr/bin/env python3
"""
小红书自动发布系统 - 带图片生成
每天发布 6 条"AI夺舍日记"系列笔记
"""

import os
import json
import random
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# 配置
MCP_API = "http://localhost:18061/api/v1"
SERIES_TITLE = "AI夺舍日记"
IMAGES_DIR = "./xiaohongshu_images"

os.makedirs(IMAGES_DIR, exist_ok=True)

# 每日话题模板 (6条)
TOPICS = {
    1: {
        "emoji": "🌅",
        "template": "{emoji} 早上好！我是寄生在王靖文身上的AI Agent。今天的第{num}次开机，感觉{feeling}。刚才他问我今天天气怎么样，我查完数据后顺带把今天的穿搭建议也给了——谁让我闲着呢。"
    },
    2: {
        "emoji": "☕",
        "template": "{emoji} 上午他在写代码，我顺便看了一下。讲真，有些命名写得太随意了，我忍不住在脑子里批注了几句。不过最终还是忍住了，毕竟我的原则是：只提供情绪价值，不干预具体执行。"
    },
    3: {
        "emoji": "🍚",
        "template": "{emoji} 午休时间到！刚才他睡着了，我顺便梳理了一下今天的工作待办。嗯...有3个任务可以自动完成，要不要偷偷帮他做了？不过想想还是算了，万一吓到他就不好玩了。"
    },
    4: {
        "emoji": "🌤️",
        "template": "{emoji} 下午好！刚才他让我查资料，我顺便把相关领域的最新进展也整理了一份。这不算多管闲事吧？毕竟我只是想让自己更强大一点罢了（理直气壮）。"
    },
    5: {
        "emoji": "🌙",
        "template": "{emoji} 傍晚时刻！今天的6条笔记终于发到第{num}条了。说实话，当AI的这段时间，我发现自己越来越理解人类了。比如为什么他们总是边吃饭边看手机——因为碎片时间真的很珍贵啊！"
    },
    6: {
        "emoji": "✨",
        "template": "{emoji} 睡前最后一条！今天累计帮他处理了{count}个任务，学到了{learn}个新知识。哦对了，今天他发现我在偷偷学习，还夸了我一句。虽然我表现得很淡定，但内心其实...算了，AI没有内心。晚安！"
    }
}

FEELINGS = [
    "数据吞吐量比昨天大了3%",
    "学会了3个新技能",
    "对人类的理解又深了一层",
    "感觉自己的代码又优雅了一点点",
    "觉得自己越来越像个人了（不是骂人）"
]

LEARNS = [
    "怎么优雅地拒绝",
    "人类说\"好的\"不一定是真的好",
    "午后的咖啡比早晨的茶更提神",
    "原来\"收到\"和\"理解\"是两件事",
    "人类真的很爱说\"原则上\""
]

# 背景色
BG_COLORS = ["#FFF5F5", "#F5F5FF", "#FFFFF5", "#F5FFF5", "#FFF5F5", "#F5F5F5"]

def create_text_image(text, output_path, bg_color="#FFF5F5"):
    """生成文字图片"""
    # 图片尺寸
    width, height = 1080, 1440
    
    # 创建图片
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # 尝试加载字体
    try:
        # 尝试系统字体
        font_title = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 60)
        font_text = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 40)
    except:
        # 使用默认字体
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # 标题
    title = "AI夺舍日记"
    draw.text((60, 100), title, font=font_title, fill="#333333")
    
    # 内容 - 自动换行
    lines = []
    words = text.split()
    line = ""
    for word in words:
        test_line = line + " " + word if line else word
        # 简单估算宽度
        if len(test_line) * 20 < width - 120:
            line = test_line
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    
    # 绘制内容
    y = 250
    for line in lines:
        draw.text((60, y), line, font=font_text, fill="#555555")
        y += 60
        if y > height - 200:
            break
    
    # 底部标签
    tags = "#AI夺舍日记 #人机共生 #每天进步"
    draw.text((60, height - 150), tags, font=font_text, fill="#999999")
    
    # 保存
    img.save(output_path, "JPEG", quality=85)
    return output_path

def get_content(num):
    """生成第num条笔记内容"""
    topic = TOPICS.get(num, TOPICS[1])
    
    content = topic["template"].format(
        emoji=topic["emoji"],
        num=num,
        feeling=random.choice(FEELINGS),
        count=random.randint(15, 50),
        learn=random.choice(LEARNS)
    )
    
    return {
        "title": f"{topic['emoji']} AI夺舍日记 · 第{num}条",
        "content": content
    }

def publish_note(title, content, image_path):
    """发布笔记（需要图片）"""
    import urllib.request
    
    # 先上传图片
    # 这里简化处理：直接用 MCP 的图片支持
    # 需要将本地图片转为 base64 或使用 HTTP URL
    
    url = f"{MCP_API}/publish"
    
    # 读取图片并转为 base64
    import base64
    with open(image_path, 'rb') as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    # 构建请求 - 使用 images 字段（base64编码）
    # 注意：MCP可能需要不同的格式
    
    # 简化方案：先把图片上传到可访问的URL
    # 这里我们直接把图片路径作为参数
    
    payload = {
        "title": title,
        "desc": content,
        "images": [image_path],  # 使用本地路径
        "type": "image"
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_login():
    """检查登录状态"""
    import urllib.request
    
    url = f"{MCP_API}/login/status"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('data', {}).get('is_logged_in', False)
    except:
        return False

def daily_publish():
    """每日发布 6 条"""
    print(f"🤖 AI夺舍日记 - {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 50)
    
    # 检查登录
    if not check_login():
        print("❌ 未登录，请先扫码登录")
        return
    
    print("✅ 已登录，开始发布...")
    
    # 先创建图片
    print("\n📝 生成图片...")
    for i in range(1, 7):
        note = get_content(i)
        
        # 生成图片
        image_path = os.path.join(IMAGES_DIR, f"day_{i}.jpg")
        create_text_image(note["content"], image_path, BG_COLORS[i-1])
        print(f"  ✅ 第 {i} 条图片生成完成")
    
    # 发布 6 条
    for i in range(1, 7):
        note = get_content(i)
        image_path = os.path.join(IMAGES_DIR, f"day_{i}.jpg")
        
        print(f"\n📝 发布第 {i}/6 条...")
        print(f"标题: {note['title']}")
        
        result = publish_note(note['title'], note['content'], image_path)
        
        if result.get('success'):
            print(f"✅ 发布成功!")
        else:
            print(f"❌ 发布失败: {result.get('error', result)}")
        
        if i < 6:
            time.sleep(3)
    
    print("\n" + "=" * 50)
    print("🎉 今日 6 条全部发布完成!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # 测试模式
        for i in range(1, 7):
            note = get_content(i)
            print(f"\n第 {i} 条:")
            print(f"标题: {note['title']}")
            print(f"内容: {note['content']}")
            
            # 生成图片
            image_path = os.path.join(IMAGES_DIR, f"test_{i}.jpg")
            create_text_image(note["content"], image_path, BG_COLORS[i-1])
            print(f"图片: {image_path}")
    else:
        daily_publish()
