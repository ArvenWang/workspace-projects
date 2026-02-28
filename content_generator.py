#!/usr/bin/env python3
"""
AI文案生成器 - 完整版
功能：
1. 小红书笔记生成
2. 公众号文案
3. 广告文案
4. 短视频脚本
5. 批量生成

依赖：
pip3 install requests

运行：
python3 content_generator.py xhs "推荐一款好用的产品"
python3 content_generator.py ad "护肤品"
python3 content_generator.py video "美食"
"""

import json
import random
import os
from pathlib import Path

# 配置
CONFIG = {
    'data_dir': os.path.expanduser('~/.content_generator'),
}

Path(CONFIG['data_dir']).mkdir(parents=True, exist_ok=True)


class ContentGenerator:
    def __init__(self):
        self.templates = self.load_templates()
    
    def load_templates(self):
        """加载模板"""
        templates = {
            'xhs_intro': [
                "姐妹们！今天必须分享这个{}",
                "绝了！这个{}也太好用了吧",
                "不允许你不知道！{}",
                "挖到宝了！这个{}",
            ],
            'xhs_body': [
                "用了两个月了，真的爱不释手！",
                "亲测有效！集美们可以冲了",
                "真实使用感受分享一下~",
                "我已经回购第三个了！",
            ],
            'xhs_outro': [
                "需要的姐妹评论区见~",
                "有问题留言问我",
                "喜欢的话点个赞再走呀",
                "持续更新中，关注我不迷路",
            ],
            'ad_headline': [
                "{}，你值得拥有",
                "一款让{}爱不释手的产品",
                "用了{}，再也回不去了",
                "{}，年轻人的第一选择",
            ],
            'video_intro': [
                "今天来聊聊{}",
                "这期视频带你了解{}",
                "{}你真的了解吗？",
                "关于{}，我想说说",
            ]
        }
        return templates
    
    def generate_xhs(self, topic):
        """生成小红书笔记"""
        intro = random.choice(self.templates['xhs_intro']).format(topic)
        body = random.choice(self.templates['xhs_body'])
        outro = random.choice(self.templates['xhs_outro'])
        
        # 添加标签
        tags = f"\n\n#{topic} #好物分享 #真实测评"
        
        content = f"""{intro}

{body}

{topic}使用感受：
✅ 优点1：...
✅ 优点2：...
✅ 优点3：...

💰 价格：...
📦 购买方式：...

{ outro }

{tags}"""
        return content
    
    def generate_ad(self, product):
        """生成广告文案"""
        headline = random.choice(self.templates['ad_headline']).format(product)
        
        content = f"""{headline}

为什么选择{product}？

🔥 核心优势：
• 品质保证
• 性价比高
• 用户口碑好

📢 现在下单享优惠！

#广告 #推广"""
        return content
    
    def generate_video_script(self, topic):
        """生成短视频脚本"""
        intro = random.choice(self.templates['video_intro']).format(topic)
        
        script = f"""【{topic}】短视频脚本

开场 (0-3秒):
{intro}

内容 (3-45秒):
1. 介绍{topic}的基本信息
2. 分享使用体验
3. 演示效果

结尾 (45-60秒):
"如果喜欢，记得点赞关注！"

#短视频 #脚本"""
        return script
    
    def generate_wechat(self, topic):
        """生成公众号文案"""
        content = f"""【深度】{topic}

hi，大家好，今天想和大家聊聊{topic}。

▎写在前面
最近{topic}成为了热门话题...

▎正文
关于{topic}，我有以下几点想分享：

1. 第一点...
2. 第二点...
3. 第三点...

▎总结
以上就是关于{topic}的全部内容...

如果你有其他看法，欢迎评论区交流~

-End-"""
        return content
    
    def batch_generate(self, template_type, topic, count=5):
        """批量生成"""
        results = []
        
        for i in range(count):
            if template_type == 'xhs':
                content = self.generate_xhs(topic)
            elif template_type == 'ad':
                content = self.generate_ad(topic)
            elif template_type == 'video':
                content = self.generate_video_script(topic)
            elif template_type == 'wechat':
                content = self.generate_wechat(topic)
            else:
                content = "未知类型"
            
            results.append(content)
        
        return results


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
AI文案生成器 - 使用说明

使用:
  python3 content_generator.py xhs <主题>    # 小红书
  python3 content_generator.py ad <产品>    # 广告
  python3 content_generator.py video <主题> # 短视频
  python3 content_generator.py wechat <主题> # 公众号
  python3 content_generator.py batch <类型> <主题> <数量>

示例:
  python3 content_generator.py xhs 护肤品
  python3 content_generator.py ad 咖啡
  python3 content_generator.py video 美食
  python3 content_generator.py batch xhs 美食 5
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    gen = ContentGenerator()
    
    if cmd == 'xhs' and len(sys.argv) >= 3:
        topic = ' '.join(sys.argv[2:])
        print(gen.generate_xhs(topic))
    
    elif cmd == 'ad' and len(sys.argv) >= 3:
        product = ' '.join(sys.argv[2:])
        print(gen.generate_ad(product))
    
    elif cmd == 'video' and len(sys.argv) >= 3:
        topic = ' '.join(sys.argv[2:])
        print(gen.generate_video_script(topic))
    
    elif cmd == 'wechat' and len(sys.argv) >= 3:
        topic = ' '.join(sys.argv[2:])
        print(gen.generate_wechat(topic))
    
    elif cmd == 'batch' and len(sys.argv) >= 5:
        template_type = sys.argv[2]
        topic = sys.argv[3]
        count = int(sys.argv[4])
        
        results = gen.batch_generate(template_type, topic, count)
        
        for i, content in enumerate(results, 1):
            print(f"\n{'='*40}")
            print(f"版本 {i}")
            print('='*40)
            print(content)
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
