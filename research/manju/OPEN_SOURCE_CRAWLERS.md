# 国内社交平台开源爬虫方案汇总

> 研究日期: 2026-02-28
> 整理: OpenClaw AI

---

## 📊 方案总览

| 平台 | 最佳开源库 | Stars | 安装方式 | 推荐指数 |
|------|-----------|-------|---------|---------|
| **抖音** | TikTokDownloader | 13.2k | `pip install` | ⭐⭐⭐⭐⭐ |
| **抖音** | Douyin_TikTok_Download_API | 16.4k | 源码运行 | ⭐⭐⭐⭐ |
| **小红书** | XHS-Downloader | 10.1k | 源码运行 | ⭐⭐⭐⭐⭐ |
| **B站** | bilibili-api | 3.5k | `pip install bilibili-api-python` | ⭐⭐⭐⭐⭐ |
| **微博** | weibo-crawler | 4.3k | 源码运行 | ⭐⭐⭐⭐⭐ |
| **知乎** | ZhihuSpider | 249 | 源码运行 | ⭐⭐⭐ |
| **快手** | videodl | 1.1k | 源码运行 | ⭐⭐⭐⭐ |

---

## 🎵 抖音方案

### 方案1: TikTokDownloader (推荐)
```bash
# 安装
git clone https://github.com/JoeanAmier/TikTokDownloader.git
cd TikTokDownloader
pip install -r requirements.txt

# 使用
python main.py
```
**特点**:
- ✅ 支持抖音、TikTok、快手
- ✅ 批量下载视频/音频/数据
- ✅ 支持API调用
- ✅ 图形界面 + 命令行

### 方案2: Douyin_TikTok_Download_API
```bash
# 安装
pip install douyin-tiktok-scraper

# 使用
python -c "
from douyin_tiktok_scraper.scraper import Scraper
import asyncio

async def main():
    api = Scraper()
    result = await api.hybrid_parsing('https://v.douyin.com/xxx')
    print(result)

asyncio.run(main())
"
```
**特点**:
- ✅ API方式调用
- ✅ 异步高性能
- ✅ 支持多平台

---

## 📕 小红书方案

### 方案1: XHS-Downloader (推荐)
```bash
# 下载
git clone https://github.com/JoeanAmier/XHS-Downloader.git
cd XHS-Downloader

# 安装依赖
pip install -r requirements.txt

# 配置Cookie后运行
python main.py
```
**功能**:
- ✅ 笔记批量下载
- ✅ 图片无水印下载
- ✅ 评论采集
- ✅ 博主数据采集

**配置说明**:
1. 登录小红书网页版
2. F12打开开发者工具
3. 复制Cookie到配置文件
4. 运行程序

---

## 📺 B站方案

### bilibili-api (已安装✅)
```bash
# 安装
pip install bilibili-api-python aiohttp

# 使用示例
import asyncio
from bilibili_api import video, search

async def main():
    # 搜索视频
    results = await search.search_by_type(
        keyword="短剧",
        search_type="video",
        page=1
    )
    
    # 获取视频信息
    v = video.Video(bvid="BV1vE421j7NR")
    info = await v.get_info()
    print(info['title'])

asyncio.run(main())
```
**功能**:
- ✅ 400+ API接口
- ✅ 视频/弹幕/评论/用户
- ✅ 直播/专栏/番剧
- ✅ 异步高性能

---

## 📝 微博方案

### weibo-crawler (已下载✅)
```bash
# 位置
/tmp/weibo-crawler/

# 配置
编辑 config.json:
{
    "user_id_list": "user_id_list.txt",
    "cookie": "你的微博Cookie",
    "write_mode": ["csv", "json"],
    "output_directory": "weibo_data"
}

# 运行
python weibo.py
```
**功能**:
- ✅ 用户信息采集
- ✅ 微博内容采集
- ✅ 图片/视频下载
- ✅ 评论采集
- ✅ 支持多种数据库

---

## 🎯 快速部署方案

### 方案A: 全平台采集 (推荐)
```bash
# 1. 创建采集环境
mkdir ~/social_crawlers && cd ~/social_crawlers

# 2. 安装Python库
pip install douyin-tiktok-scraper bilibili-api-python aiohttp pandas

# 3. 下载微博爬虫
git clone https://github.com/dataabc/weibo-crawler.git

# 4. 下载小红书爬虫
git clone https://github.com/JoeanAmier/XHS-Downloader.git

# 5. 下载抖音爬虫
git clone https://github.com/JoeanAmier/TikTokDownloader.git
```

### 方案B: 使用TikHub统一API (商业)
```bash
pip install tikhub-api-python-sdk

# 一个SDK覆盖多平台
# 需要注册获取API Key
```

---

## 🔧 Cookie获取方法

### 通用方法 (适用于所有平台)
1. 用Chrome登录目标平台
2. 按F12打开开发者工具
3. 切换到 Application/应用 标签
4. 左侧选择 Cookies
5. 复制需要的Cookie字段

### 抖音Cookie字段
```
sessionid
ttwid
msToken
xg_device_score
```

### 小红书Cookie字段
```
web_session
xsec_token
```

### B站Cookie字段
```
SESSDATA
bili_jct
```

### 微博Cookie字段
```
SCF
SUB
SUBP
```

---

## 📋 已安装库清单

✅ **douyin-tiktok-scraper** - 抖音/TikTok/B站
✅ **bilibili-api-python** - B站API
✅ **aiohttp** - 异步HTTP请求

📁 **已下载项目**:
- /tmp/weibo-crawler/ - 微博爬虫

---

## 🚀 下一步操作

### 1. 配置Cookie (必需)
- 登录各平台网页版
- 获取Cookie
- 填入配置文件

### 2. 测试单个平台
```bash
# 测试B站
cd /Users/wangjingwen/.openclaw/workspace
python3 test_bilibili_api.py

# 测试微博
cd /tmp/weibo-crawler
python3 weibo.py

# 测试抖音
python3 test_douyin_scraper.py
```

### 3. 批量采集
- 配置用户ID列表
- 设置输出格式
- 启动采集任务

---

## ⚠️ 注意事项

1. **Cookie有效期** - 定期更新Cookie
2. **请求频率** - 控制速度，避免封号
3. **数据存储** - 注意磁盘空间
4. **法律合规** - 仅用于学习研究

---

## 📚 参考链接

- 抖音: https://github.com/JoeanAmier/TikTokDownloader
- 小红书: https://github.com/JoeanAmier/XHS-Downloader
- B站: https://github.com/Nemo2011/bilibili-api
- 微博: https://github.com/dataabc/weibo-crawler

---

*报告完成*
