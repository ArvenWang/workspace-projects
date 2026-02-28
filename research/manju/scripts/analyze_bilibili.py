#!/usr/bin/env python3
"""
漫剧数据分析脚本
分析B站采集的漫剧数据
"""

import json
from collections import Counter
import re

DATA_FILE = '/Users/wangjingwen/.openclaw/workspace/research/manju/data/collected/bilibili_manju.json'
OUTPUT_FILE = '/Users/wangjingwen/.openclaw/workspace/research/manju/analysis/bilibili_manju_analysis.json'

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def analyze(data):
    # 1. 基本统计
    total = len(data)
    total_plays = sum(int(item.get('play', 0)) for item in data)
    avg_plays = total_plays / total if total > 0 else 0
    
    # 2. 播放量分布
    play_distribution = {
        '100万+': len([d for d in data if int(d.get('play', 0)) >= 1000000]),
        '50万-100万': len([d for d in data if 500000 <= int(d.get('play', 0)) < 1000000]),
        '10万-50万': len([d for d in data if 100000 <= int(d.get('play', 0)) < 500000]),
        '10万以下': len([d for d in data if int(d.get('play', 0)) < 100000]),
    }
    
    # 3. 关键词分布
    keywords = [item.get('keyword', '') for item in data]
    keyword_dist = dict(Counter(keywords))
    
    # 4. 高播放量Top20
    sorted_by_play = sorted(data, key=lambda x: int(x.get('play', 0)), reverse=True)
    top20 = [
        {
            'title': item['title'][:50],
            'play': item['play'],
            'author': item['author'],
            'keyword': item.get('keyword', '')
        }
        for item in sorted_by_play[:20]
    ]
    
    # 5. 热门创作者
    authors = [item.get('author', '') for item in data]
    author_dist = dict(Counter(authors).most_common(10))
    
    # 6. 标题关键词提取
    all_titles = ' '.join([item.get('title', '') for item in data])
    title_keywords = re.findall(r'[\u4e00-\u9fa5]{2,4}', all_titles)
    title_keyword_dist = dict(Counter(title_keywords).most_common(30))
    
    return {
        'total': total,
        'total_plays': total_plays,
        'avg_plays': int(avg_plays),
        'play_distribution': play_distribution,
        'keyword_distribution': keyword_dist,
        'top20': top20,
        'top_authors': author_dist,
        'title_keywords': title_keyword_dist
    }

def main():
    print("📊 加载数据...")
    data = load_data()
    
    print("📈 分析中...")
    result = analyze(data)
    
    # 保存结果
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    print(f"\n{'='*50}")
    print(f"📊 B站漫剧数据分析报告")
    print(f"{'='*50}")
    print(f"总数据量: {result['total']}")
    print(f"总播放量: {result['total_plays']:,}")
    print(f"平均播放: {result['avg_plays']:,}")
    
    print(f"\n�� 播放量分布:")
    for k, v in result['play_distribution'].items():
        print(f"  {k}: {v}")
    
    print(f"\n🔑 搜索关键词分布:")
    for k, v in sorted(result['keyword_distribution'].items(), key=lambda x: -x[1])[:10]:
        print(f"  {k}: {v}")
    
    print(f"\n🏆 Top10 热门:")
    for i, item in enumerate(result['top20'][:10], 1):
        print(f"  {i}. {item['title'][:35]} - {item['play']:,}")
    
    print(f"\n✅ 详细分析已保存到: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
