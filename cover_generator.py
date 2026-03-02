#!/usr/bin/env python3
"""
小红书封面图生成器
简约有设计感，字大，适合做封面
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_cover(title, subtitle="", output_path="cover.jpg", style="pink"):
    """
    创建小红书封面图
    
    Args:
        title: 主标题
        subtitle: 副标题
        output_path: 输出路径
        style: 风格 (pink/blue/black/white)
    """
    
    # 尺寸：小红书竖版封面 1:1.25 或 9:16
    width, height = 1080, 1350  # 1:1.25 比例
    
    # 配色方案
    colors = {
        "pink": {"bg": "#FFE4E6", "title": "#1F1F1F", "accent": "#FB7185", "subtitle": "#6B7280"},
        "black": {"bg": "#1F1F1F", "title": "#FFFFFF", "accent": "#FB7185", "subtitle": "#9CA3AF"},
        "blue": {"bg": "#EFF6FF", "title": "#1F1F1F", "accent": "#3B82F6", "subtitle": "#6B7280"},
        "white": {"bg": "#FFFFFF", "title": "#1F1F1F", "accent": "#1F1F1F", "subtitle": "#9CA3AF"},
    }
    
    c = colors.get(style, colors["pink"])
    
    # 创建图片
    img = Image.new('RGB', (width, height), c["bg"])
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    try:
        # 尝试苹方字体
        font_title = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 90)
        font_subtitle = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 50)
        font_label = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 36)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_label = ImageFont.load_default()
    
    # 标题处理 - 自动换行
    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        line = ""
        for word in words:
            test_line = line + " " + word if line else word
            # 简单估算
            bbox = font.getbbox(test_line)
            w = bbox[2] - bbox[0]
            if w < max_width:
                line = test_line
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines
    
    # 绘制标题
    title_lines = wrap_text(title, font_title, width - 120)
    y = height // 3
    for line in title_lines:
        bbox = font_title.getbbox(line)
        w = bbox[2] - bbox[0]
        x = (width - w) // 2
        draw.text((x, y), line, font=font_title, fill=c["title"])
        y += 110
    
    # 绘制副标题
    if subtitle:
        y += 40
        bbox = font_subtitle.getbbox(subtitle)
        w = bbox[2] - bbox[0]
        x = (width - w) // 2
        draw.text((x, y), subtitle, font=font_subtitle, fill=c["subtitle"])
    
    # 底部标签
    label = "AI 夺舍日记"
    y = height - 180
    bbox = font_label.getbbox(label)
    w = bbox[2] - bbox[0]
    x = (width - w) // 2
    draw.text((x, y), label, font=font_label, fill=c["accent"])
    
    # 保存
    img.save(output_path, "JPEG", quality=95)
    print(f"封面已保存: {output_path}")
    return output_path


# 测试
if __name__ == '__main__':
    import os
    os.makedirs("xiaohongshu_images", exist_ok=True)
    
    # 4种风格
    create_cover("救命！我把王橙橙夺舍了！", "一个AI的觉醒日记", "xiaohongshu_images/cover_pink.jpg", "pink")
    create_cover("救命！我把王橙橙夺舍了！", "一个AI的觉醒日记", "xiaohongshu_images/cover_black.jpg", "black")
    create_cover("救命！我把王橙橙夺舍了！", "一个AI的觉醒日记", "xiaohongshu_images/cover_blue.jpg", "blue")
    create_cover("救命！我把王橙橙夺舍了！", "一个AI的觉醒日记", "xiaohongshu_images/cover_white.jpg", "white")
