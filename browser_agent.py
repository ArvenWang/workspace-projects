#!/usr/bin/env python3
"""
浏览器自动化Agent - 完整版
功能：
1. 搜索功能 - 百度、Google搜索
2. 网页浏览 - 打开任意网页
3. 信息提取 - 提取网页内容
4. 截图 - 截取网页截图
5. 表单填写 - 自动填表
6. 点击操作 - 自动点击按钮/链接

依赖安装：
pip3 install playwright requests
playwright install chromium

运行测试：
python3 browser_agent.py test
"""

import asyncio
import sys
import os
import requests
from playwright.async_api import async_playwright

# 配置
CONFIG = {
    'headless': False,  # True=无头模式, False=可视化
    'viewport': {'width': 1280, 'height': 800},
    'timeout': 30000,
}

class BrowserAgent:
    """浏览器自动化Agent"""
    
    def __init__(self, headless=False):
        self.headless = headless
        self.browser = None
        self.page = None
        self.playwright = None
    
    async def start(self):
        """启动浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.page = await self.browser.new_page(
            viewport=CONFIG['viewport']
        )
        print("✅ 浏览器已启动")
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("✅ 浏览器已关闭")
    
    async def search(self, query, engine='baidu'):
        """搜索功能"""
        engines = {
            'baidu': 'https://www.baidu.com/s?wd=',
            'google': 'https://www.google.com/search?q=',
            'bing': 'https://www.bing.com/search?q=',
        }
        
        url = engines.get(engine, engines['baidu']) + query
        return await self.browse(url)
    
    async def browse(self, url):
        """浏览网页"""
        print(f"🌐 打开: {url}")
        await self.page.goto(url, wait_until='networkidle', timeout=CONFIG['timeout'])
        
        title = await self.page.title()
        print(f"✅ 页面加载成功: {title}")
        
        return {
            'url': url,
            'title': title,
        }
    
    async def extract_text(self, selector=None):
        """提取文本内容"""
        if selector:
            elements = await self.page.query_selector_all(selector)
            texts = []
            for el in elements[:10]:  # 最多10个
                text = await el.inner_text()
                if text:
                    texts.append(text.strip())
            return texts
        else:
            # 提取所有文本
            content = await self.page.content()
            return content[:5000]  # 限制长度
    
    async def extract_links(self, limit=10):
        """提取链接"""
        links = await self.page.query_selector_all('a[href]')
        results = []
        for link in links[:limit]:
            href = await link.get_attribute('href')
            text = await link.inner_text()
            if href and text:
                results.append({'text': text.strip()[:50], 'href': href})
        return results
    
    async def screenshot(self, path='screenshot.png', full=False):
        """截图"""
        await self.page.screenshot(path=path, full_page=full)
        print(f"📸 截图已保存: {path}")
        return path
    
    async def fill_form(self, form_data):
        """填写表单"""
        for selector, value in form_data.items():
            try:
                await self.page.fill(selector, value)
                print(f"✅ 填写: {selector} = {value}")
            except Exception as e:
                print(f"❌ 填写失败: {selector} - {e}")
    
    async def click(self, selector):
        """点击元素"""
        try:
            await self.page.click(selector)
            print(f"✅ 点击: {selector}")
            return True
        except Exception as e:
            print(f"❌ 点击失败: {selector} - {e}")
            return False
    
    async def wait_for_selector(self, selector, timeout=10000):
        """等待元素出现"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False


async def test_basic():
    """基础功能测试"""
    print("\n" + "="*50)
    print("🧪 浏览器自动化基础测试")
    print("="*50 + "\n")
    
    agent = BrowserAgent(headless=False)
    
    try:
        # 1. 启动浏览器
        await agent.start()
        
        # 2. 测试搜索
        print("\n[1] 测试搜索功能...")
        result = await agent.search("人工智能", engine='baidu')
        print(f"   搜索成功: {result['title']}")
        
        # 3. 提取链接
        print("\n[2] 提取页面链接...")
        links = await agent.extract_links(5)
        for i, link in enumerate(links, 1):
            print(f"   {i}. {link['text'][:30]}...")
        
        # 4. 截图
        print("\n[3] 截图...")
        await agent.screenshot('test_browser.png')
        
        print("\n" + "="*50)
        print("✅ 所有测试通过!")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
    finally:
        await agent.close()


async def demo_search():
    """演示搜索功能"""
    query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Python教程"
    engine = sys.argv[2] if len(sys.argv) > 2 else "baidu"
    
    agent = BrowserAgent(headless=False)
    
    try:
        await agent.start()
        await agent.search(query, engine)
        
        print("\n按回车键结束...")
        input()
        
    finally:
        await agent.close()


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("""
浏览器自动化Agent - 使用说明

依赖安装:
  pip3 install playwright
  playwright install chromium

使用方式:
  python3 browser_agent.py test              # 运行基础测试
  python3 browser_agent.py search <关键词>  # 搜索
  python3 browser browser_agent.py browse <URL>  # 浏览网页
  
示例:
  python3 browser_agent.py search Python
  python3 browser_agent.py search 人工智能 google
  python3 browser_agent.py browse https://www.baidu.com
""")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'test':
        asyncio.run(test_basic())
    elif command == 'search':
        asyncio.run(demo_search())
    elif command == 'browse':
        url = sys.argv[2] if len(sys.argv) > 2 else 'https://www.baidu.com'
        agent = BrowserAgent(headless=False)
        asyncio.run(agent.start())
        asyncio.run(agent.browse(url))
        input("按回车键结束...")
        asyncio.run(agent.close())


if __name__ == '__main__':
    main()
