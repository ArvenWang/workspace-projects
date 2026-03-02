#!/usr/bin/env python3
"""
测试 douyin-tiktok-scraper 库
"""

import asyncio
from douyin_tiktok_scraper.scraper import Scraper

async def test_douyin():
    """测试抖音采集"""
    print("🎵 测试抖音采集功能...")
    
    api = Scraper()
    
    # 测试视频链接解析
    test_urls = [
        "https://v.douyin.com/L4FJNR3/",  # 示例链接
    ]
    
    for url in test_urls:
        try:
            print(f"\n🔗 解析: {url}")
            result = await api.hybrid_parsing(url)
            print(f"✅ 成功: {result}")
        except Exception as e:
            print(f"❌ 失败: {str(e)}")

if __name__ == '__main__':
    asyncio.run(test_douyin())
