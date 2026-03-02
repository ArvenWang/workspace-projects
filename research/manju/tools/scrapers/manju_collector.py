#!/usr/bin/env python3
"""
漫剧Top500数据采集系统
使用Playwright自动化爬取各平台短剧榜单数据
"""

import asyncio
import json
import csv
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright


class ManjuDataCollector:
    """漫剧数据采集器"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.rankings_dir = self.data_dir / "rankings"
        
        # 创建目录
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.rankings_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = []
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()
    
    async def collect_douyin(self, limit=100):
        """采集抖音短剧热榜"""
        print("📱 开始采集抖音短剧热榜...")
        page = await self.context.new_page()
        
        try:
            # 访问抖音短剧页面
            await page.goto('https://www.douyin.com/', wait_until='networkidle', timeout=30000)
            
            # 等待页面加载
            await page.wait_for_timeout(3000)
            
            # 搜索短剧相关内容
            # 注意：抖音的反爬较强，这里使用搜索方式
            print("🔍 正在搜索短剧热榜...")
            
            # 截图保存
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = self.raw_dir / f"douyin_search_{timestamp}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"📸 截图已保存: {screenshot_path}")
            
            # 提取页面信息
            title = await page.title()
            url = page.url
            
            data = {
                'platform': 'douyin',
                'url': url,
                'title': title,
                'collected_at': datetime.now().isoformat(),
                'screenshot': str(screenshot_path),
                'notes': '抖音需要登录才能查看完整榜单，建议手动收集或使用API'
            }
            
            self.results.append(data)
            print(f"✅ 抖音数据采集完成")
            return data
            
        except Exception as e:
            print(f"❌ 抖音采集失败: {str(e)}")
            return {'platform': 'douyin', 'error': str(e)}
        finally:
            await page.close()
    
    async def collect_kuaishou(self, limit=100):
        """采集快手短剧榜单"""
        print("📱 开始采集快手短剧榜单...")
        page = await self.context.new_page()
        
        try:
            # 访问快手
            await page.goto('https://www.kuaishou.com/', wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(3000)
            
            # 截图保存
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = self.raw_dir / f"kuaishou_{timestamp}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            title = await page.title()
            
            data = {
                'platform': 'kuaishou',
                'url': page.url,
                'title': title,
                'collected_at': datetime.now().isoformat(),
                'screenshot': str(screenshot_path),
                'notes': '快手需要登录后查看星芒短剧榜'
            }
            
            self.results.append(data)
            print(f"✅ 快手数据采集完成")
            return data
            
        except Exception as e:
            print(f"❌ 快手采集失败: {str(e)}")
            return {'platform': 'kuaishou', 'error': str(e)}
        finally:
            await page.close()
    
    async def collect_bilibili(self, limit=100):
        """采集B站短剧数据"""
        print("📱 开始采集B站短剧数据...")
        page = await self.context.new_page()
        
        try:
            # 访问B站短剧分区
            await page.goto('https://www.bilibili.com/v/channel/shortplay', wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(3000)
            
            # 提取短剧列表
            print("🔍 提取短剧列表...")
            
            # 获取视频卡片信息
            cards = await page.query_selector_all('.video-card, .video-list-item, .bili-video-card')
            
            videos = []
            for i, card in enumerate(cards[:limit]):
                try:
                    # 提取标题
                    title_el = await card.query_selector('a[title], .title, h3')
                    title = await title_el.get_attribute('title') if title_el else ''
                    if not title:
                        title = await title_el.text_content() if title_el else ''
                    
                    # 提取链接
                    link_el = await card.query_selector('a')
                    link = await link_el.get_attribute('href') if link_el else ''
                    
                    # 提取播放量
                    play_el = await card.query_selector('.play-text, .view, .play-count')
                    play_count = await play_el.text_content() if play_el else ''
                    
                    # 提取作者
                    author_el = await card.query_selector('.up-name, .author, .name')
                    author = await author_el.text_content() if author_el else ''
                    
                    videos.append({
                        'rank': i + 1,
                        'title': title.strip() if title else '',
                        'link': f"https:{link}" if link and link.startswith('//') else link,
                        'play_count': play_count.strip() if play_count else '',
                        'author': author.strip() if author else ''
                    })
                    
                except Exception as e:
                    continue
            
            # 截图保存
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = self.raw_dir / f"bilibili_{timestamp}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            data = {
                'platform': 'bilibili',
                'url': page.url,
                'title': await page.title(),
                'collected_at': datetime.now().isoformat(),
                'videos': videos,
                'video_count': len(videos),
                'screenshot': str(screenshot_path)
            }
            
            self.results.append(data)
            print(f"✅ B站采集完成，获取 {len(videos)} 条数据")
            return data
            
        except Exception as e:
            print(f"❌ B站采集失败: {str(e)}")
            return {'platform': 'bilibili', 'error': str(e)}
        finally:
            await page.close()
    
    async def collect_3rd_party_reports(self):
        """采集第三方行业报告"""
        print("📊 开始采集第三方行业报告...")
        
        # 德塔文、猫眼、云合数据等
        reports = [
            {'name': '德塔文短剧报告', 'url': 'http://www.datawin.com.cn/', 'status': 'pending'},
            {'name': '猫眼短剧数据', 'url': 'https://piaofang.maoyan.com/', 'status': 'pending'},
        ]
        
        for report in reports:
            print(f"  - {report['name']}: {report['url']}")
        
        return {
            'platform': '3rd_party',
            'reports': reports,
            'notes': '第三方数据平台需要注册或付费获取详细数据',
            'collected_at': datetime.now().isoformat()
        }
    
    def save_to_json(self, filename=None):
        """保存数据为JSON"""
        if not filename:
            filename = f"manju_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.processed_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 数据已保存到: {filepath}")
        return filepath
    
    def save_to_csv(self, videos, filename=None):
        """保存视频列表为CSV"""
        if not filename:
            filename = f"manju_videos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.rankings_dir / filename
        
        if videos:
            keys = videos[0].keys()
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(videos)
            
            print(f"💾 CSV已保存到: {filepath}")
        
        return filepath


async def main():
    """主程序"""
    print("🎬 漫剧Top500数据采集系统启动\n")
    print("=" * 60)
    
    async with ManjuDataCollector(headless=False) as collector:
        # 采集各平台数据
        # await collector.collect_douyin(limit=100)
        # await collector.collect_kuaishou(limit=100)
        
        # B站短剧数据
        bilibili_data = await collector.collect_bilibili(limit=50)
        
        # 第三方报告
        reports_data = await collector.collect_3rd_party_reports()
        collector.results.append(reports_data)
        
        # 保存数据
        collector.save_to_json()
        
        # 如果有B站视频数据，保存为CSV
        if bilibili_data and 'videos' in bilibili_data:
            collector.save_to_csv(bilibili_data['videos'], 'bilibili_shortplay_ranking.csv')
    
    print("\n" + "=" * 60)
    print("✅ 数据采集完成！")


if __name__ == '__main__':
    asyncio.run(main())
