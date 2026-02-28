#!/usr/bin/env python3
"""
B站漫剧定时采集脚本
每小时运行一次
"""

import requests
import json
import time
import random
import os

SESSDATA = "8b3b6cd1%2C1787807698%2C535eb%2A22CjD80p6zbqn8UfyRopFr6p1hL1KejRiZKRyXuW_1IMnQ4FS8gsXxnsnpDPAGtGPwWDkSVmIycEZlVDFaSng2SkM4MEJKT2hBMTNST3VtbzBfWlNha0tHRHZzU1F6Ynd1N0M3bDV5WlhlNl9PRHBpdUdCRXU0X1VFX2RfZjlTM1lEOGtNbG5ucjR3IIEC"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.bilibili.com',
    'Cookie': f'SESSDATA={SESSDATA}'
}

DATA_FILE = '/Users/wangjingwen/.openclaw/workspace/research/manju/data/collected/bilibili_manju.json'

# 漫剧关键词
keywords = ['漫剧', 'AI漫剧', '小说漫剧', '修仙漫剧', '霸总漫剧', '穿越漫剧', '重生漫剧', '古装漫剧', '甜宠漫剧']

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def search(keyword, page=1):
    url = 'https://api.bilibili.com/x/web-interface/search/type'
    params = {'search_type': 'video', 'keyword': keyword, 'page': page, 'page_size': 30}
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 412:
            return [], "banned"
        
        data = resp.json()
        if data.get('code') == 0:
            results = data['data']['result']
            items = []
            for r in results:
                items.append({
                    'title': r.get('title', '').replace('<em class="keyword">', '').replace('</em>', ''),
                    'author': r.get('author', ''),
                    'play': r.get('play', 0),
                    'keyword': keyword,
                    'bvid': r.get('bvid', ''),
                    'url': f"https://www.bilibili.com/video/{r.get('bvid', '')}"
                })
            return items, "success"
        return [], data.get('message', 'error')
    except Exception as e:
        return [], str(e)

def main():
    print(f"🚀 B站漫剧采集开始...")
    
    existing = load_data()
    existing_bvids = set(item['bvid'] for item in existing)
    print(f"已有: {len(existing)} 条")
    
    new_count = 0
    
    for kw in keywords:
        items, status = search(kw)
        
        if status == "banned":
            print(f"⚠️ {kw}: 被限频")
            continue
        
        if status == "success":
            new_items = [item for item in items if item['bvid'] not in existing_bvids]
            existing.extend(new_items)
            existing_bvids.update(item['bvid'] for item in new_items)
            new_count += len(new_items)
            print(f"✅ {kw}: 新增 {len(new_items)} 条")
        
        # 间隔8-12秒
        time.sleep(random.uniform(8, 12))
    
    save_data(existing)
    print(f"✅ 完成! 总计: {len(existing)}, 新增: {new_count}")

if __name__ == '__main__':
    main()
