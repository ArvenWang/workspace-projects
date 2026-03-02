#!/usr/bin/env python3
"""
Playwright 爬虫脚本示例
用于演示网页数据采集功能
"""

import asyncio
import json
from playwright.async_api import async_playwright
from datetime import datetime


class WebCrawler:
    """网页爬虫类"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.results = []
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()
    
    async def crawl_page(self, url, wait_for=None, extract_selectors=None):
        """
        爬取单个页面
        
        Args:
            url: 要爬取的URL
            wait_for: 等待的元素选择器
            extract_selectors: 要提取数据的CSS选择器字典
        """
        page = await self.context.new_page()
        
        try:
            print(f"🌐 正在访问: {url}")
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 等待特定元素加载
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=10000)
            
            # 提取数据
            data = {
                'url': url,
                'title': await page.title(),
                'timestamp': datetime.now().isoformat(),
            }
            
            # 根据选择器提取自定义数据
            if extract_selectors:
                for key, selector in extract_selectors.items():
                    try:
                        elements = await page.query_selector_all(selector)
                        texts = []
                        for el in elements[:10]:  # 限制数量
                            text = await el.text_content()
                            if text:
                                texts.append(text.strip())
                        data[key] = texts
                    except Exception as e:
                        data[key] = f"提取失败: {str(e)}"
            
            # 截图保存
            screenshot_path = f"crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            data['screenshot'] = screenshot_path
            
            self.results.append(data)
            print(f"✅ 成功爬取: {data['title']}")
            return data
            
        except Exception as e:
            print(f"❌ 爬取失败: {str(e)}")
            return {'url': url, 'error': str(e)}
        finally:
            await page.close()
    
    async def search_and_extract(self, keyword, search_engine='google'):
        """
        搜索关键词并提取结果
        """
        if search_engine == 'google':
            url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}"
            selectors = {
                'results': 'div[data-header-feature] h3, div.g h3',
                'descriptions': 'div[data-content-feature] span, div.g span'
            }
        elif search_engine == 'bing':
            url = f"https://www.bing.com/search?q={keyword.replace(' ', '+')}"
            selectors = {
                'results': 'h2 a',
                'descriptions': '.b_caption p'
            }
        else:
            raise ValueError(f"不支持的搜索引擎: {search_engine}")
        
        return await self.crawl_page(url, wait_for='body', extract_selectors=selectors)
    
    def save_results(self, filename='crawl_results.json'):
        """保存结果到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"💾 结果已保存到: {filename}")


async def demo():
    """演示爬虫功能"""
    print("🚀 启动 Playwright 爬虫演示\n")
    
    async with WebCrawler(headless=False) as crawler:
        # 示例1: 爬取示例网站
        print("=" * 50)
        print("示例 1: 爬取 httpbin.org")
        print("=" * 50)
        
        result = await crawler.crawl_page(
            url='https://httpbin.org/html',
            extract_selectors={
                'headers': 'h1',
                'paragraphs': 'p'
            }
        )
        print(f"提取的数据: {json.dumps(result, ensure_ascii=False, indent=2)}\n")
        
        # 示例2: 爬取 GitHub 首页
        print("=" * 50)
        print("示例 2: 爬取 GitHub 首页")
        print("=" * 50)
        
        result = await crawler.crawl_page(
            url='https://github.com',
            wait_for='.application-main',
            extract_selectors={
                'headings': 'h1, h2, h3',
                'links': 'a[href^="/"]'
            }
        )
        print(f"提取的数据: {json.dumps(result, ensure_ascii=False, indent=2)}\n")
        
        # 保存结果
        crawler.save_results('demo_crawl_results.json')
    
    print("\n✅ 爬虫演示完成！")


if __name__ == '__main__':
    asyncio.run(demo())
