#!/usr/bin/env python3
"""
第三方数据平台采集
蝉妈妈 / 灰豚数据 / 新榜 / 飞瓜数据
"""

import asyncio
import json
import csv
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright


class ThirdPartyDataCollector:
    """第三方数据平台采集器"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "collected"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser.close()
        await self.playwright.stop()
    
    async def collect_channmama(self):
        """采集蝉妈妈数据"""
        print("\n" + "="*60)
        print("🌟 采集蝉妈妈 - 抖音数据")
        print("="*60)
        
        context = await self.browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()
        
        try:
            print("🌐 访问蝉妈妈官网...")
            await page.goto('https://www.chanmama.com/', wait_until='networkidle', timeout=60000)
            await page.wait_for_timeout(3000)
            
            # 检查是否已登录
            if '登录' in await page.title() or await page.query_selector('.login'):
                print("⚠️  蝉妈妈需要登录")
                print("   请在浏览器中完成登录，等待20秒...")
                await page.wait_for_timeout(20000)
            
            # 访问短剧数据页面
            print("🔍 搜索短剧相关数据...")
            
            # 尝试访问热门视频榜
            await page.goto('https://www.chanmama.com/promotion/douyin/rank', timeout=60000)
            await page.wait_for_timeout(5000)
            
            screenshot_path = self.data_dir / f"channmama_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            print(f"📸 截图已保存: {screenshot_path}")
            
            result = {
                'platform': '蝉妈妈',
                'url': page.url,
                'screenshot': str(screenshot_path),
                'collected_at': datetime.now().isoformat()
            }
            self.results.append(result)
            return result
            
        except Exception as e:
            print(f"❌ 蝉妈妈采集失败: {str(e)}")
            return {'platform': '蝉妈妈', 'error': str(e)}
        finally:
            await context.close()
    
    async def collect_huitun(self):
        """采集灰豚数据"""
        print("\n" + "="*60)
        print("🐋 采集灰豚数据 - 小红书数据")
        print("="*60)
        
        context = await self.browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()
        
        try:
            print("🌐 访问灰豚数据官网...")
            await page.goto('https://www.huitun.com/', wait_until='networkidle', timeout=60000)
            await page.wait_for_timeout(3000)
            
            screenshot_path = self.data_dir / f"huitun_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            print(f"📸 截图已保存: {screenshot_path}")
            
            result = {
                'platform': '灰豚数据',
                'url': page.url,
                'screenshot': str(screenshot_path),
                'collected_at': datetime.now().isoformat()
            }
            self.results.append(result)
            return result
            
        except Exception as e:
            print(f"❌ 灰豚数据采集失败: {str(e)}")
            return {'platform': '灰豚数据', 'error': str(e)}
        finally:
            await context.close()
    
    async def collect_newrank(self):
        """采集新榜数据"""
        print("\n" + "="*60)
        print("📈 采集新榜数据 - 全平台")
        print("="*60)
        
        context = await self.browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()
        
        try:
            print("🌐 访问新榜官网...")
            await page.goto('https://www.newrank.cn/', wait_until='networkidle', timeout=60000)
            await page.wait_for_timeout(3000)
            
            # 检查登录状态
            if '登录' in await page.title() or await page.query_selector('.login-btn'):
                print("⚠️  新榜需要登录")
                print("   请在浏览器中完成登录，等待20秒...")
                await page.wait_for_timeout(20000)
            
            # 访问短视频榜单
            print("🔍 访问短视频榜单...")
            await page.goto('https://www.newrank.cn/public/info/list.html?period=day&dataType=shortvideo', timeout=60000)
            await page.wait_for_timeout(5000)
            
            # 提取数据
            print("📊 提取榜单数据...")
            rows = await page.query_selector_all('.rank-item, .list-item, tr')
            print(f"   找到 {len(rows)} 条数据")
            
            data = []
            for idx, row in enumerate(rows[:20]):
                try:
                    cells = await row.query_selector_all('td, .cell, .item')
                    if len(cells) >= 3:
                        rank = await cells[0].text_content() if len(cells) > 0 else ''
                        title = await cells[1].text_content() if len(cells) > 1 else ''
                        author = await cells[2].text_content() if len(cells) > 2 else ''
                        
                        if title.strip():
                            data.append({
                                'rank': rank.strip() if rank else str(idx + 1),
                                'platform': '新榜',
                                'title': title.strip()[:100],
                                'author': author.strip()[:50] if author else '',
                                'collected_at': datetime.now().isoformat()
                            })
                except:
                    continue
            
            screenshot_path = self.data_dir / f"newrank_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            print(f"✅ 新榜采集完成: {len(data)} 条数据")
            
            # 保存CSV
            if data:
                csv_path = self.data_dir / 'newrank_shortvideo.csv'
                with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                print(f"💾 CSV已保存: {csv_path}")
            
            result = {
                'platform': '新榜',
                'url': page.url,
                'data_count': len(data),
                'data': data,
                'screenshot': str(screenshot_path),
                'collected_at': datetime.now().isoformat()
            }
            self.results.append(result)
            return result
            
        except Exception as e:
            print(f"❌ 新榜采集失败: {str(e)}")
            return {'platform': '新榜', 'error': str(e)}
        finally:
            await context.close()
    
    async def collect_feigua(self):
        """采集飞瓜数据"""
        print("\n" + "="*60)
        print("🍉 采集飞瓜数据 - 抖音版")
        print("="*60)
        
        context = await self.browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()
        
        try:
            print("🌐 访问飞瓜数据官网...")
            await page.goto('https://www.feigua.cn/', wait_until='networkidle', timeout=60000)
            await page.wait_for_timeout(3000)
            
            screenshot_path = self.data_dir / f"feigua_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            print(f"📸 截图已保存: {screenshot_path}")
            
            result = {
                'platform': '飞瓜数据',
                'url': page.url,
                'screenshot': str(screenshot_path),
                'collected_at': datetime.now().isoformat()
            }
            self.results.append(result)
            return result
            
        except Exception as e:
            print(f"❌ 飞瓜数据采集失败: {str(e)}")
            return {'platform': '飞瓜数据', 'error': str(e)}
        finally:
            await context.close()
    
    def save_summary(self):
        """保存汇总"""
        summary_path = self.data_dir / f"third_party_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 汇总报告已保存: {summary_path}")


async def main():
    """主程序"""
    print("🎬 第三方数据平台采集")
    print("="*60)
    print("⚠️  请确保已登录各数据平台")
    print("   如果未登录，请在浏览器中完成登录")
    print("="*60)
    
    async with ThirdPartyDataCollector() as collector:
        # 采集各平台
        await collector.collect_channmama()
        await collector.collect_huitun()
        await collector.collect_newrank()
        await collector.collect_feigua()
        
        # 保存汇总
        collector.save_summary()
    
    print("\n" + "="*60)
    print("✅ 第三方数据采集完成！")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(main())
