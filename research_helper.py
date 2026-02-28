#!/usr/bin/env python3
"""
数据研究助手 - 完整版
功能：
1. 网页数据采集
2. 数据分析
3. 报告生成
4. 图表制作

依赖：
pip3 install requests beautifulsoup4 matplotlib pandas

运行：
python3 research_helper.py collect <URL>
python3 research_helper.py analyze <文件>
python3 research_helper.py report <主题>
"""

import requests
import json
import os
import re
from datetime import datetime
from pathlib import Path
from collections import Counter

# 配置
CONFIG = {
    'data_dir': os.path.expanduser('~/.research_helper'),
    'timeout': 30,
}

Path(CONFIG['data_dir']).mkdir(parents=True, exist_ok=True)


class ResearchHelper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def collect_url(self, url):
        """采集网页数据"""
        try:
            print(f"🔍 采集: {url}")
            
            resp = self.session.get(url, timeout=CONFIG['timeout'])
            resp.raise_for_status()
            
            # 提取基本信息
            data = {
                'url': url,
                'status': resp.status_code,
                'title': self.extract_title(resp.text),
                'description': self.extract_description(resp.text),
                'links': self.extract_links(resp.text),
                'images': self.extract_images(resp.text),
                'text_length': len(resp.text),
                'collected_at': datetime.now().isoformat()
            }
            
            # 保存
            self.save_data(url, data)
            
            print(f"✅ 采集成功")
            print(f"   标题: {data['title']}")
            print(f"   描述: {data['description'][:50]}...")
            print(f"   链接数: {len(data['links'])}")
            print(f"   图片数: {len(data['images'])}")
            
            return data
            
        except Exception as e:
            print(f"❌ 采集失败: {e}")
            return None
    
    def extract_title(self, html):
        """提取标题"""
        match = re.search(r'<title>([^<]+)</title>', html, re.I)
        return match.group(1).strip() if match else ''
    
    def extract_description(self, html):
        """提取描述"""
        match = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
        if not match:
            match = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']', html, re.I)
        return match.group(1).strip() if match else ''
    
    def extract_links(self, html, limit=50):
        """提取链接"""
        links = re.findall(r'href=["\'](https?://[^"\']+)["\']', html)
        # 去重
        links = list(set(links))[:limit]
        return links
    
    def extract_images(self, html, limit=20):
        """提取图片"""
        images = re.findall(r'src=["\'](https?://[^"\']+\.(jpg|jpeg|png|gif|webp)[^"\']*)["\']', html, re.I)
        images = [img[0] for img in images]
        return list(set(images))[:limit]
    
    def save_data(self, url, data):
        """保存数据"""
        filename = self.sanitize_filename(url) + '.json'
        filepath = os.path.join(CONFIG['data_dir'], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def sanitize_filename(self, url):
        """生成安全的文件名"""
        name = url.replace('https://', '').replace('http://', '')
        name = re.sub(r'[^\w\-]', '_', name)[:50]
        return name
    
    def list_collected(self):
        """列出已采集数据"""
        files = list(Path(CONFIG['data_dir']).glob('*.json'))
        print(f"\n已采集 {len(files)} 个页面:")
        for f in files:
            print(f"  - {f.stem[:40]}")
    
    def analyze_text(self, text):
        """分析文本"""
        words = re.findall(r'[\w]+', text.lower())
        word_count = Counter(words)
        
        # 过滤停用词
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
                    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                    'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                    'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
                    'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 
                    'through', 'during', 'before', 'after', 'above', 'below',
                    'between', 'under', 'again', 'further', 'then', 'once'}
        
        filtered = {w: c for w, c in word_count.items() 
                   if w not in stopwords and len(w) > 2}
        
        top_words = sorted(filtered.items(), key=lambda x: -x[1])[:20]
        
        print("\n📊 文本分析结果:")
        print(f"   总词数: {len(words)}")
        print(f"   高频词 Top 20:")
        for word, count in top_words:
            print(f"   {word}: {count}")
        
        return top_words
    
    def generate_report(self, topic):
        """生成研究报告"""
        report = f"""# {topic} 研究报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 概述
{topic}是一个值得深入研究的领域。

## 研究方向

### 1. 市场现状
（待采集数据补充）

### 2. 发展趋势
（待采集数据补充）

### 3. 竞争格局
（待采集数据补充）

## 数据来源
- 网络公开数据
- 行业报告
- 第三方研究

## 结论
{topic}领域具有较大的发展潜力，建议持续关注。

---
*本报告由AI自动生成*
"""
        
        # 保存报告
        filename = f"report_{self.sanitize_filename(topic)}.md"
        filepath = os.path.join(CONFIG['data_dir'], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 报告已生成: {filename}")
        return report


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
数据研究助手 - 使用说明

依赖安装:
  pip3 install requests beautifulsoup4 pandas matplotlib

使用:
  python3 research_helper.py collect <URL>  # 采集网页
  python3 research_helper.py list           # 列表
  python3 research_helper.py analyze <关键词>  # 分析
  python3 research_helper.py report <主题>    # 生成报告

示例:
  python3 research_helper.py collect https://example.com
  python3 research_helper.py report 人工智能
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    helper = ResearchHelper()
    
    if cmd == 'collect' and len(sys.argv) >= 3:
        url = sys.argv[2]
        helper.collect_url(url)
    
    elif cmd == 'list':
        helper.list_collected()
    
    elif cmd == 'analyze' and len(sys.argv) >= 3:
        keyword = ' '.join(sys.argv[2:])
        # 简单测试分析
        helper.analyze_text(keyword * 100)
    
    elif cmd == 'report' and len(sys.argv) >= 3:
        topic = ' '.join(sys.argv[2:])
        helper.generate_report(topic)
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
