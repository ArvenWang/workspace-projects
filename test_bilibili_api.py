#!/usr/bin/env python3
"""
测试 bilibili-api 库
"""

import asyncio
from bilibili_api import video, search

async def test_bilibili():
    """测试B站API"""
    print("📺 测试B站API...")
    
    try:
        # 测试搜索功能
        print("\n🔍 测试搜索短剧...")
        results = await search.search_by_type(
            keyword="短剧",
            search_type="video",
            page=1
        )
        print(f"✅ 搜索成功，找到 {len(results['result'])} 个结果")
        
        # 打印前3个结果
        for item in results['result'][:3]:
            print(f"  - {item.get('title', 'N/A')}")
        
        # 测试视频信息获取
        print("\n📹 测试获取视频信息...")
        # BV1vE421j7NR 是一个示例视频
        v = video.Video(bvid="BV1vE421j7NR")
        info = await v.get_info()
        print(f"✅ 视频标题: {info['title']}")
        print(f"   播放量: {info['stat']['view']}")
        print(f"   点赞: {info['stat']['like']}")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")

if __name__ == '__main__':
    asyncio.run(test_bilibili())
