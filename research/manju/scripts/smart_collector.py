#!/usr/bin/env python3
"""
智能B站漫剧采集器
- 自适应间隔，防止被限频
- 边采集边分析
"""

import requests
import json
import time
import random
from collections import Counter

SESSDATA = "8b3b6cd1%2C1787807698%2C535eb%2A22CjD80p6zbqn8UfyRopFr6p1hL1KejRiZKRyXuW_1IMnQ4FS8gsXxnsnpDPAGtGPwWDkSVmIycEZlVDFaSng2SkM4MEJKT2hBMTNST3VtbzBfWlNha0tHRHZzU1F6Ynd1N0M3bDV5WlhlNl9PRHBpdUdCRXU0X1VFX2RfZjlTM1lEOGtNbG5ucjR3IIEC"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Referer': 'https://www.bilibili.com',
    'Cookie': f'SESSDATA={SESSDATA}'
}

DATA_FILE = '/Users/wangjingwen/.openclaw/workspace/research/manju/data/collected/bilibili_manju.json'
ANALYSIS_FILE = '/Users/wangjingwen/.openclaw/workspace/research/manju/analysis/bilibili_manju_analysis.json'

# 关键词库
KEYWORDS = [
    '漫剧', '动态漫', 'AI漫剧', '小说漫剧',
    '霸总剧', '甜宠剧', '重生剧', '穿越剧', '修仙剧', '玄幻剧',
    '复仇剧', '虐剧', '爽剧', '逆袭剧', '战神',
    '古装剧', '宫斗剧', '宅斗剧', '武侠剧', '仙侠剧',
    '豪门剧', '闪婚剧', '先婚后爱', '双向奔赴',
    '都市剧', '职场剧', '情感剧', '悬疑剧',
    '末世', '丧尸', '系统', '签到', '打卡'
]

class SmartCollector:
    def __init__(self):
        self.data = self.load_data()
        self.bvids = {item['bvid'] for item in self.data}
        self.base_interval = 8  # 基础间隔8秒
        self.current_interval = 8
        self.ban_count = 0
        self.success_count = 0
        
    def load_data(self):
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except:
            return []
    
    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def analyze(self):
        """快速分析当前数据"""
        if not self.data:
            return
            
        total = len(self.data)
        total_plays = sum(int(item.get('play', 0)) for item in self.data)
        
        # 播放量分布
        dist = {
            '100万+': len([d for d in self.data if int(d.get('play', 0)) >= 1000000]),
            '50万-100万': len([d for d in self.data if 500000 <= int(d.get('play', 0)) < 1000000]),
            '10万-50万': len([d for d in self.data if 100000 <= int(d.get('play', 0)) < 500000]),
            '10万以下': len([d for d in self.data if int(d.get('play', 0)) < 100000]),
        }
        
        # 关键词分布
        keywords = Counter(item.get('keyword', '') for item in self.data)
        
        # Top10
        sorted_data = sorted(self.data, key=lambda x: int(x.get('play', 0)), reverse=True)[:10]
        
        result = {
            'total': total,
            'total_plays': total_plays,
            'avg_plays': int(total_plays / total) if total else 0,
            'distribution': dist,
            'keywords': dict(keywords.most_common(15)),
            'top10': [{'title': item['title'][:40], 'play': item['play']} for item in sorted_data]
        }
        
        with open(ANALYSIS_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 实时分析 (共{total}条):")
        print(f"   总播放: {total_plays/10000:.0f}万, 均播放: {result['avg_plays']/10000:.1f}万")
        print(f"   分布: 100万+:{dist['100万+']}, 50万:{dist['50万-100万']}, 10万:{dist['10万-50万']}, <10万:{dist['10万以下']}")
        
    def adjust_interval(self, success):
        """智能调整间隔"""
        if success:
            self.success_count += 1
            # 如果连续成功，逐步减少间隔
            if self.success_count >= 3 and self.current_interval > 6:
                self.current_interval -= 1
                self.success_count = 0
                print(f"   ➡️ 间隔调整为: {self.current_interval}秒")
        else:
            self.ban_count += 1
            self.success_count = 0
            # 被限频时增加间隔
            self.current_interval = min(30, self.current_interval + 5)
            print(f"   ⬇️ 被限频! 间隔调整为: {self.current_interval}秒")
    
    def collect(self, keyword):
        """采集单个关键词"""
        url = 'https://api.bilibili.com/x/web-interface/search/type'
        params = {'search_type': 'video', 'keyword': keyword, 'page': 1, 'page_size': 20}
        
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            
            if resp.status_code == 412:
                self.adjust_interval(False)
                return 0, "banned"
            
            data = resp.json()
            
            if data.get('code') == 0:
                results = data['data']['result']
                added = 0
                
                for r in results:
                    bvid = r.get('bvid', '')
                    if bvid and bvid not in self.bvids:
                        self.data.append({
                            'title': r.get('title', '').replace('<em class="keyword">', '').replace('</em>', ''),
                            'author': r.get('author', ''),
                            'play': r.get('play', 0),
                            'danmu': r.get('danmu', 0),
                            'keyword': keyword,
                            'bvid': bvid,
                            'url': f"https://www.bilibili.com/video/{bvid}"
                        })
                        self.bvids.add(bvid)
                        added += 1
                
                self.adjust_interval(True)
                return added, "success"
            else:
                return 0, data.get('message', 'error')
                
        except Exception as e:
            return 0, str(e)
    
    def run(self, rounds=3):
        """运行采集"""
        print(f"🚀 智能采集启动...")
        print(f"   初始数据: {len(self.data)}条")
        
        for round_num in range(1, rounds + 1):
            print(f"\n{'='*40}")
            print(f"第 {round_num}/{rounds} 轮采集")
            print(f"{'='*40}")
            
            # 随机打乱关键词顺序
            keywords = KEYWORDS.copy()
            random.shuffle(keywords)
            
            new_total = 0
            for i, kw in enumerate(keywords):
                print(f"[{i+1}/{len(keywords)}] 搜索: {kw}...", end=" ")
                added, status = self.collect(kw)
                
                if status == "success":
                    print(f"+{added}条")
                    new_total += added
                elif status == "banned":
                    print(f"被限频, 等待{self.current_interval}秒...")
                else:
                    print(f"失败: {status}")
                
                # 智能间隔 + 随机波动
                sleep_time = self.current_interval + random.uniform(-2, 2)
                time.sleep(max(3, sleep_time))
            
            # 每轮结束后分析
            print(f"\n轮次结束，新增: {new_total}条")
            self.save_data()
            self.analyze()
            
            # 轮次间休息
            if round_num < rounds:
                print(f"休息30秒...")
                time.sleep(30)
        
        print(f"\n✅ 采集完成! 总计: {len(self.data)}条")

if __name__ == '__main__':
    collector = SmartCollector()
    collector.run(rounds=2)
