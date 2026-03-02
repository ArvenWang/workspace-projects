# 案例1: 浏览器自动化

## 功能
- 搜索功能 - 百度、Google搜索
- 网页浏览 - 打开任意网页
- 信息提取 - 提取网页内容/链接
- 截图 - 截取网页截图
- 表单填写 - 自动填表
- 点击操作 - 自动点击按钮/链接

## 依赖安装
```bash
pip3 install playwright requests
playwright install chromium
```

## 使用方法
```bash
# 测试
python3 browser_agent.py test

# 搜索
python3 browser_agent.py search Python
python3 browser_agent.py search 人工智能 google

# 浏览网页
python3 browser_agent.py browse https://www.baidu.com
```

## 代码文件
- `browser_agent.py` - 主程序

## 验证状态
- [x] 依赖已安装
- [x] 语法检查通过
- [x] 基础功能测试通过 (百度页面可打开)
- [ ] 完整交互测试 (需要图形界面)

## 待验证
在有图形界面的机器上运行:
```bash
python3 browser_agent.py test
```
