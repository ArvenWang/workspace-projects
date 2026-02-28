#!/usr/bin/env python3
"""
漫剧数据采集 - 使用真实Chrome Profile（已登录状态）
路径: ~/Library/Application Support/Google/Chrome/Default
"""

import asyncio
import json
import csv
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright


class RealProfileCollector:
    """使用真实Chrome Profile的采集器"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "collected"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        
        # Chrome路径
        self.chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        self.user_data_dir = Path.home() / "Library/Application Support/Google/Chrome"
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        
        print("🌐 启动Chrome（使用你的登录状态）...")
        print(f"   Profile路径: {self.user_data_dir}")
        print("   这将打开你日常使用的Chrome浏览器")
        
        # 使用真实Chrome Profile
        self.browser = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=False,  # 可见模式
            executable_path=self.chrome_path,
            args=['--profile-directory=Default'],
            viewport={'width': 1440, 'height': 900}
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
        
        page = await self.browser.new_page()
        
        try:
            print("🔍 搜索关键词: AI漫剧")
            await page.goto('https://www.xiaohongshu.com/search_result/?keyword=AI%E6%BC%AB%E5%89%A7', 
                          wait_until='networkidle', timeout=60000)
            
            await page.wait_for_timeout(5000)
            
            # 检查是否已登录
            login_check = await page.query_selector('.login-btn, .login-container')
            if login_check:
                print("⚠️  检测到未登录，请手动登录后继续...")
                print("   你有60秒时间完成登录")
                await page.wait_for_timeout(60000)
            
            print("📊 提取笔记数据...")
            
            # 滚动加载更多
            for i in range(5):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(2000)
            
            # 获取笔记卡片
            notes = []
            cards = await page.query_selector_all('.note-item, [class*="note-item"], .feeds-page > div > div')
            print(f"   找到 {len(cards)} 个笔记")
            
            for idx, card in enumerate(cards[:50]):  # 采集前50条
                try:
                    # 提取标题
                    title_el = await card.query_selector('.title, h3, .content span, [class*="title"]')
                    title = await title_el.text_content() if title_el else ''
                    
                    # 提取作者
                    author_el = await card.query_selector('.author, .user-name, [class*="author"]')
                    author = await author_el.text_content() if author_el else ''
                    
                    # 提取点赞
                    like_el = await card.query_selector('.like-count, .count, [class*="like"]')
                    likes = await like_el.text_content() if like_el else ''
                    
                    if title.strip() and len(title.strip()) > 3:
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
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = self.data_dir / f"xiaohongshu_logged_in_{timestamp}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            result = {
                'platform': '小红书',
                'keyword': 'AI漫剧',
                'url': page.url,
                'notes_count': len(notes),
                'notes': notes[:30],  # 只保存前30条详细数据
                'screenshot': str(screenshot_path),
                'collected_at': datetime.now().isoformat()
            }
            
            self.results.append(result)
            print(f"✅ 小红书采集完成: {len(notes)} 条笔记")
            
            # 保存CSV
            if notes:
                csv_path = self.data_dir / f'xiaohongshu_ai_manju_{timestamp}.csv'
                with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=notes[0].keys())
                    writer.writeheader()
                    writer.writerows(notes)
                print(f"💾 CSV已保存: {csv_path}")
            
            await page.close()
            return result
            
        except Exception as e:
            print(f"❌ 小红书采集失败: {str(e)}")
            await page.close()
            return {'platform': '小红书', 'error': str(e)}
    
    async def collect_bilibili(self):
        """采集B站短剧数据"""
        print("\n" + "="*60)
        print("📺 采集B站 - 短剧分区")
        print("="*60)
        
        page = await self.browser.new_page()
        
        try:
            print("🌐 访问B站短剧分区...")
            await page.goto('https://www.bilibili.com/v/channel/shortplay',
                          wait_until='networkidle', timeout=60000)
            
            await page.wait_for_timeout(5000)
            
            # 检查是否需要验证
            if '验证码' in await page.title():
                print("⚠️  遇到验证码，请手动完成验证...")
                print("   你有60秒时间完成验证")
                await page.wait_for_timeout(60000)
            
            print("📊 提取视频数据...")
            
            # 滚动加载
            for i in range(5):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(2000)
            
            videos = []
            cards = await page.query_selector_all('.video-card, .bili-video-card, [class*="video-card"]')
            print(f"   找到 {len(cards)} 个视频")
            
            for idx, card in enumerate(cards[:50]):
                try:
                    title_el = await card.query_selector('h3, .title, a[title]')
                    title = await title_el.get_attribute('title') if title_el else ''
                    if not title:
                        title = await title_el.text_content() if title_el else ''
                    
                    play_el = await card.query_selector('.play-text, .view, [class*="play"]')
                    plays = await play_el.text_content() if play_el else ''
                    
                    author_el = await card.query_selector('.up-name, .author, [class*="up"]')
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
                except:
                    continue
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = self.data_dir / f"bilibili_shortplay_{timestamp}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            result = {
                'platform': 'B站',
                'url': page.url,
                'videos_count': len(videos),
                'videos': videos[:30],
                'screenshot': str(screenshot_path),
                'collected_at': datetime.now().isoformat()
            }
            
            self.results.append(result)
            print(f"✅ B站采集完成: {len(videos)} 个视频")
            
            if videos:
                csv_path = self.data_dir / f'bilibili_shortplay_{timestamp}.csv'
                with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=videos[0].keys())
                    writer.writeheader()
                    writer.writerows(videos)
                print(f"💾 CSV已保存: {csv_path}")
            
            await page.close()
            return result
            
        except Exception as e:
            print(f"❌ B站采集失败: {str(e)}")
            await page.close()
            return {'platform': 'B站', 'error': str(e)}
    
    async def collect_douyin(self):
        """采集抖音短剧数据"""
        print("\n" + "="*60)
        print("🎵 采集抖音 - AI短剧")
        print("="*60)
        
        page = await self.browser.new_page()
        
        try:
            print("🌐 访问抖音搜索...")
            await page.goto('https://www.douyin.com/search/AI%E6%BC%AB%E5%89%A7',
                          wait_until='domcontentloaded', timeout=60000)
            
            await page.wait_for_timeout(8000)
            
            # 检查验证
            verify_check = await page.query_selector('.captcha, .verify, [class*="captcha"]')
            if verify_check:
                print("⚠️  遇到验证，请手动完成...")
                print("   你有60秒时间完成验证")
                await page.wait_for_timeout(60000)
            
            print("📊 提取视频数据...")
            
            # 滚动加载
            for i in range(5):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(3000)
            
            videos = []
            cards = await page.query_selector_all('[class*="card"], [class*="item"], .search-card')
            print(f"   找到 {len(cards)} 个视频")
            
            for idx, card in enumerate(cards[:50]):
                try:
                    title_el = await card.query_selector('h3, .title, [class*="title"], [class*="desc"]')
                    title = await title_el.text_content() if title_el else ''
                    
                    like_el = await card.query_selector('[class*="like"], [class*="count"]')
                    likes = await like_el.text_content() if like_el else ''
                    
                    if title.strip() and len(title.strip()) > 5:
                        videos.append({
                            'rank': idx + 1,
                            'platform': '抖音',
                            'title': title.strip()[:100],
                            'likes': likes.strip()[:30] if likes else '',
                            'collected_at': datetime.now().isoformat()
                        })
                except:
                    continue
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = self.data_dir / f"douyin_ai_manju_{timestamp}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            result = {
                'platform': '抖音',
                'url': page.url,
                'videos_count': len(videos),
                'videos': videos[:30],
                'screenshot': str(screenshot_path),
                'collected_at': datetime.now().isoformat()
            }
            
            self.results.append(result)
            print(f"✅ 抖音采集完成: {len(videos)} 个视频")
            
            if videos:
                csv_path = self.data_dir / f'douyin_ai_manju_{timestamp}.csv'
                with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=videos[0].keys())
                    writer.writeheader()
                    writer.writerows(videos)
                print(f"💾 CSV已保存: {csv_path}")
            
            await page.close()
            return result
            
        except Exception as e:
            print(f"❌ 抖音采集失败: {str(e)}")
            await page.close()
            return {'platform': '抖音', 'error': str(e)}
    
    def save_summary(self):
        """保存采集汇总"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_path = self.data_dir / f"real_profile_collection_{timestamp}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 汇总报告已保存: {summary_path}")
        return summary_path


async def main():
    """主程序"""
    print("🎬 漫剧数据采集系统 - 真实Chrome Profile")
    print("="*60)
    print("⚠️  重要提示:")
    print("   1. 请确保Chrome已完全退出（Cmd+Q）")
    print("   2. 脚本会使用你的Chrome Profile（已登录状态）")
    print("   3. 如果看到验证弹窗，请手动完成")
    print("   4. 采集过程中不要操作Chrome")
    print("="*60)
    
    async with RealProfileCollector() as collector:
        # 采集各平台
        await collector.collect_xiaohongshu()
        await collector.collect_bilibili()
        await collector.collect_douyin()
        
        # 保存汇总
        collector.save_summary()
    
    print("\n" + "="*60)
    print("✅ 采集完成！")
    print("="*60)
    print(f"\n📁 数据保存位置: {collector.data_dir}")


if __name__ == '__main__':
    asyncio.run(main())
