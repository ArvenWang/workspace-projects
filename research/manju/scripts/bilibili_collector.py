#!/usr/bin/env python3
"""
B站漫剧数据持续采集脚本
防限频：每次请求间隔随机2-5秒
"""

import requests
import json
import time
import random

SESSDATA = "8b3b6cd1%2C1787807698%2C535eb%2A22CjD80p6zbqn8UfyRopFr6p1hL1KejRiZKRyXuW_1IMnQ4FS8gsXxnsnpDPAGtGPwWDkSVmIycEZlVDFaSng2SkM4MEJKT2hBMTNST3VtbzBfWlNha0tHRHZzU1F6Ynd1N0M3bDV5WlhlNl9PRHBpdUdCRXU0X1VFX2RfZjlTM1lEOGtNbG5ucjR3IIEC"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.bilibili.com',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cookie': f'SESSDATA={SESSDATA}'
}

# 漫剧相关关键词
keywords = [
    '漫剧', 'AI漫剧', '小说漫剧', '小说改编漫剧',
    '修仙漫剧', '玄幻漫剧', '霸总漫剧', '甜宠漫剧',
    '穿越漫剧', '重生漫剧', '武侠漫剧', '古装漫剧'
]

DATA_FILE = '/Users/wangjingwen/.openclaw/workspace/research/manju/data/collected/bilibili_manju.json'

def load_existing():
    """加载已有数据"""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    """保存数据"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def search_bilibili(keyword, page=1):
    """搜索B站"""
    url = 'https://api.bilibili.com/x/web-interface/search/type'
    params = {'search_type': 'video', 'keyword': keyword, 'page': page, 'page_size': 30}
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        
        if resp.status_code == 412:
            return None, "banned"
        
        data = resp.json()
        
        if data.get('code') == 0:
            results = data['data']['result']
            items = []
            for r in results:
                items.append({
                    'title': r.get('title', '').replace('<em class="keyword">', '').replace('</em>', ''),
                    'author': r.get('author', ''),
                    'play': r.get('play', 0),
                    'danmu': r.get('danmu', 0),
                    'keyword': keyword,
                    'bvid': r.get('bvid', ''),
                    'duration': r.get('duration', ''),
                    'url': f"https://www.bilibili.com/video/{r.get('bvid', '')}"
                })
            return items, "success"
        else:
            return None, data.get('message', 'unknown')
    except Exception as e:
        return None, str(e)

def deduplicate(new_items, existing):
    """去重"""
    existing_bvids = set(item['bvid'] for item in existing)
    unique = [item for item in new_items if item['bvid'] and item['bvid'] not in existing_bvids]
    return unique

def main():
    print(f"🚀 开始B站漫剧数据采集...")
    
    existing_data = load_existing()
    print(f"📂 已有数据: {len(existing_data)} 条")
    
    total_new = 0
    
    for keyword in keywords:
        print(f"\n🔍 搜索: {keyword}")
        
        for page in range(1, 6):  # 每关键词5页
            items, status = search_bilibili(keyword, page)
            
            if status == "banned":
                print(f"   ⚠️ 第{page}页被限频，等待30秒...")
                time.sleep(30)
                continue
            elif status != "success":
                print(f"   ❌ 第{page}页失败: {status}")
                break
            
            # 去重
            unique_items = deduplicate(items, existing_data + [])
            existing_data.extend(unique_items)
            total_new += len(unique_items)
            
            print(f"   ✅ 第{page}页: 获取{len(items)}条, 新增{len(unique_items)}条")
            
            # 随机间隔2-5秒防限频
            time.sleep(random.uniform(2, 5))
        
        # 每关键词间稍作休息
        time.sleep(random.uniform(3, 8))
    
    # 保存
    save_data(existing_data)
    
    print(f"\n✅ 采集完成!")
    print(f"   总数据: {len(existing_data)} 条")
    print(f"   新增: {total_new} 条")

if __name__ == '__main__':
    main()
