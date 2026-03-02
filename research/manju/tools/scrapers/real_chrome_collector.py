#!/usr/bin/env python3
"""
漫剧数据采集 - 使用真实Chrome（已登录状态）
采集小红书、B站、抖音、快手等平台
"""

import asyncio
import json
import csv
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright


class RealChromeCollector:
    """使用真实Chrome的采集器"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "collected"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        
        # 使用真实Chrome（已登录状态）
        print("🌐 启动真实Chrome浏览器...")
        print("   将使用你的登录状态访问各平台")
        
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # 可见模式，方便观察
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser.close()
        await self.playwright.stop()
    
    async def collect_xiaohongshu(self):
        """采集小红书AI漫剧数据"""
        print("\n" + "="*60)
        print("📕 采集小红书 - AI漫剧搜索")
        print("="*60)
        
        context = await self.browser.new_context(
            viewport={'width': 1440, 'height': 900}
        )
        page = await context.new_page()
        
        try:
            # 访问小红书搜索
            print("🔍 搜索关键词: AI漫剧")
            await page.goto('https://www.xiaohongshu.com/search_result/?keyword=AI%E6%BC%AB%E5%89%A7', 
                          wait_until='networkidle', timeout=60000)
            
            # 等待页面加载
            await page.wait_for_timeout(5000)
            
            # 提取笔记数据
            print("📊 提取笔记数据...")
            
            notes = []
            # 滚动加载更多
            for i in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(2000)
            
            # 获取笔记卡片
            cards = await page.query_selector_all('.note-item, .feeds-page .note, [class*="note"]')
            print(f"   找到 {len(cards)} 个笔记")
            
            for idx, card in enumerate(cards[:30]):  # 限制前30条
                try:
                    # 提取标题
                    title_el = await card.query_selector('.title, .note-title, h3, .content span')
                    title = await title_el.text_content() if title_el else ''
                    
                    # 提取作者
                    author_el = await card.query_selector('.author, .user-name, .nickname')
                    author = await author_el.text_content() if author_el else ''
                    
                    # 提取点赞
                    like_el = await card.query_selector('.like-count, .count, .likes')
                    likes = await like_el.text_content() if like_el else ''
                    
                    if title.strip():
                        notes.append({
                            'rank': idx + 1,
                            'platform': '小红书',
                            'keyword': 'AI漫剧',
                            'title': title.strip()[:100],
                            'author': author.strip()[:50] if author else '',
                            'likes': likes.strip() if likes else '',
                            'collected_at': datetime.now().isoformat()
                        })
                except Exception as e:
                    continue
            
            # 截图
            screenshot_path = self.data_dir / f"xiaohongshu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            result = {
                'platform': '小红书',
                'keyword': 'AI漫剧',
                'url': page.url,
                'notes_count': len(notes),
                'notes': notes,
                'screenshot': str(screenshot_path),
                'collected_at': datetime.now().isoformat()
            }
            
            self.results.append(result)
            print(f"✅ 小红书采集完成: {len(notes)} 条笔记")
            
            # 保存CSV
            if notes:
                csv_path = self.data_dir / 'xiaohongshu_ai_manju.csv'
                with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=notes[0].keys())
                    writer.writeheader()
                    writer.writerows(notes)
                print(f"💾 CSV已保存: {csv_path}")
            
            return result
            
        except Exception as e:
            print(f"❌ 小红书采集失败: {str(e)}")
            return {'platform': '小红书', 'error': str(e)}
        finally:
            await context.close()
    
    async def collect_bilibili(self):
        """采集B站短剧数据"""
        print("\n" + "="*60)
        print("📺 采集B站 - 短剧分区")
        print("="*60)
        
        context = await self.browser.new_context(
            viewport={'width': 1440, 'height': 900}
        )
        page = await context.new_page()
        
        try:
            # 访问B站短剧分区
            print("🌐 访问B站短剧分区...")
            await page.goto('https://www.bilibili.com/v/channel/shortplay',
                          wait_until='networkidle', timeout=60000)
            
            await page.wait_for_timeout(5000)
            
            # 检查是否需要验证
            if '验证码' in await page.title() or await page.query_selector('.geetest'):
                print("⚠️  遇到验证码，请手动完成验证...")
                print("   你有30秒时间完成验证")
                await page.wait_for_timeout(30000)  # 等待30秒让用户手动验证
            
            print("📊 提取视频数据...")
            
            videos = []
            # 滚动加载
            for i in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(2000)
            
            # 获取视频卡片
            cards = await page.query_selector_all('.video-card, .bili-video-card, .video-list-item')
            print(f"   找到 {len(cards)} 个视频")
            
            for idx, card in enumerate(cards[:30]):
                try:
                    # 提取标题
                    title_el = await card.query_selector('h3, .title, a[title]')
                    title = await title_el.get_attribute('title') if title_el else ''
                    if not title:
                        title = await title_el.text_content() if title_el else ''
                    
                    # 提取播放量
                    play_el = await card.query_selector('.play-text, .view, .play-count')
                    plays = await play_el.text_content() if play_el else ''
                    
                    # 提取UP主
                    author_el = await card.query_selector('.up-name, .author, .name')
                    author = await author_el.text_content() if author_el else ''
                    
                    if title.strip():
                        videos.append({
                            'rank': idx + 1,
                            'platform': 'B站',
                            'title': title.strip()[:100],
                            'author': author.strip()[:50] if author else '',
                            'plays': plays.strip() if plays else '',
                            'collected_at': datetime.now().isoformat()
                        })
                except Exception as e:
                    continue
            
            # 截图
            screenshot_path = self.data_dir / f"bilibili_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            result = {
                'platform': 'B站',
                'url': page.url,
                'videos_count': len(videos),
                'videos': videos,
                'screenshot': str(screenshot_path),
                'collected_at': datetime.now().isoformat()
            }
            
            self.results.append(result)
            print(f"✅ B站采集完成: {len(videos)} 个视频")
            
            # 保存CSV
            if videos:
                csv_path = self.data_dir / 'bilibili_shortplay.csv'
                with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnotes=videos[0].keys())
                    writer.writeheader()
                    writer.writerows(videos)
                print(f"💾 CSV已保存: {csv_path}")
            
            return result
            
        except Exception as e:
            print(f"❌ B站采集失败: {str(e)}")
            return {'platform': 'B站', 'error': str(e)}
        finally:
            await context.close()
    
    async def collect_douyin(self):
        """采集抖音短剧数据"""
        print("\n" + "="*60)
        print("🎵 采集抖音 - AI短剧")
        print("="*60)
        
        context = await self.browser.new_context(
            viewport={'width': 1440, 'height': 900}
        )
        page = await context.new_page()
        
        try:
            print("🌐 访问抖音搜索...")
            await page.goto('https://www.douyin.com/search/AI%E6%BC%AB%E5%89%A7',
                          wait_until='domcontentloaded', timeout=60000)
            
            await page.wait_for_timeout(8000)  # 抖音加载较慢
            
            print("📊 提取视频数据...")
            
            videos = []
            # 滚动加载
            for i in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(3000)
            
            # 获取视频卡片
            cards = await page.query_selector_all('[class*="card"], [class*="item"], .search-card')
            print(f"   找到 {len(cards)} 个视频")
            
            for idx, card in enumerate(cards[:30]):
                try:
                    # 提取标题
                    title_el = await card.query_selector('h3, .title, span[class*="title"], [class*="desc"]')
                    title = await title_el.text_content() if title_el else ''
                    
                    # 提取点赞
                    like_el = await card.query_selector('[class*="like"], [class*="count"], [class*="stats"]')
                    likes = await like_el.text_content() if like_el else ''
                    
                    if title.strip() and len(title.strip()) > 5:
                        videos.append({
                            'rank': idx + 1,
                            'platform': '抖音',
                            'title': title.strip()[:100],
                            'likes': likes.strip()[:30] if likes else '',
                            'collected_at': datetime.now().isoformat()
                        })
                except Exception as e:
                    continue
            
            # 截图
            screenshot_path = self.data_dir / f"douyin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            result = {
                'platform': '抖音',
                'url': page.url,
                'videos_count': len(videos),
                'videos': videos,
                'screenshot': str(screenshot_path),
                'collected_at': datetime.now().isoformat()
            }
            
            self.results.append(result)
            print(f"✅ 抖音采集完成: {len(videos)} 个视频")
            
            # 保存CSV
            if videos:
                csv_path = self.data_dir / 'douyin_ai_manju.csv'
                with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnotes=videos[0].keys())
                    writer.writeheader()
                    writer.writerows(videos)
                print(f"💾 CSV已保存: {csv_path}")
            
            return result
            
        except Exception as e:
            print(f"❌ 抖音采集失败: {str(e)}")
            return {'platform': '抖音', 'error': str(e)}
        finally:
            await context.close()
    
    async def collect_kuaishou(self):
        """采集快手短剧数据"""
        print("\n" + "="*60)
        print("📱 采集快手 - 短剧")
        print("="*60)
        
        context = await self.browser.new_context(
            viewport={'width': 1440, 'height': 900}
        )
        page = await context.new_page()
        
        try:
            print("🌐 访问快手搜索...")
            await page.goto('https://www.kuaishou.com/search?searchKey=AI%E6%BC%AB%E5%89%A7',
                          wait_until='networkidle', timeout=60000)
            
            await page.wait_for_timeout(5000)
            
            print("📊 提取视频数据...")
            
            videos = []
            # 滚动加载
            for i in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(2000)
            
            # 获取视频卡片
            cards = await page.query_selector_all('.video-item, .search-item, [class*="item"]')
            print(f"   找到 {len(cards)} 个视频")
            
            for idx, card in enumerate(cards[:30]):
                try:
                    # 提取标题
                    title_el = await card.query_selector('.title, h3, [class*="title"], [class*="desc"]')
                    title = await title_el.text_content() if title_el else ''
                    
                    # 提取作者
                    author_el = await card.query_selector('.author, .user-name, [class*="user"]')
                    author = await author_el.text_content() if author_el else ''
                    
                    if title.strip() and len(title.strip()) > 5:
                        videos.append({
                            'rank': idx + 1,
                            'platform': '快手',
                            'title': title.strip()[:100],
                            'author': author.strip()[:50] if author else '',
                            'collected_at': datetime.now().isoformat()
                        })
                except Exception as e:
                    continue
            
            # 截图
            screenshot_path = self.data_dir / f"kuaishou_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            result = {
                'platform': '快手',
                'url': page.url,
                'videos_count': len(videos),
                'videos': videos,
                'screenshot': str(screenshot_path),
                'collected_at': datetime.now().isoformat()
            }
            
            self.results.append(result)
            print(f"✅ 快手采集完成: {len(videos)} 个视频")
            
            # 保存CSV
            if videos:
                csv_path = self.data_dir / 'kuaishou_ai_manju.csv'
                with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnotes=videos[0].keys())
                    writer.writeheader()
                    writer.writerows(videos)
                print(f"💾 CSV已保存: {csv_path}")
            
            return result
            
        except Exception as e:
            print(f"❌ 快手采集失败: {str(e)}")
            return {'platform': '快手', 'error': str(e)}
        finally:
            await context.close()
    
    def save_summary(self):
        """保存采集汇总"""
        summary_path = self.data_dir / f"collection_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 汇总报告已保存: {summary_path}")
        return summary_path


async def main():
    """主程序"""
    print("🎬 漫剧数据采集系统 - 真实Chrome模式")
    print("="*60)
    print("⚠️  将使用你的Chrome浏览器和登录状态")
    print("   请勿在采集过程中操作浏览器")
    print("="*60)
    
    async with RealChromeCollector() as collector:
        # 采集各平台
        await collector.collect_xiaohongshu()
        await collector.collect_bilibili()
        await collector.collect_douyin()
        await collector.collect_kuaishou()
        
        # 保存汇总
        collector.save_summary()
    
    print("\n" + "="*60)
    print("✅ 所有平台采集完成！")
    print("="*60)
    print(f"\n📁 数据保存位置: {collector.data_dir}")


if __name__ == '__main__':
    asyncio.run(main())
