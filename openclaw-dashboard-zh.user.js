// ==UserScript==
// @name         OpenClaw Dashboard 中文汉化
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  将 OpenClaw Dashboard 界面汉化为中文
// @author       OpenClaw Agent
// @match        http://127.0.0.1:18789/*
// @match        http://localhost:18789/*
// @include      http://127.0.0.1:18789/*
// @include      http://localhost:18789/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    // 翻译字典
    const translations = {
        // 通用
        'Dashboard': '仪表盘',
        'Overview': '概览',
        'Settings': '设置',
        'Sessions': '会话',
        'Skills': '技能',
        'Memory': '记忆',
        'Status': '状态',
        'Agents': '代理',
        'Channels': '频道',
        'Logs': '日志',
        'Help': '帮助',
        
        // 状态页面
        'System': '系统',
        'Gateway': '网关',
        'Node': '节点',
        'Online': '在线',
        'Offline': '离线',
        'Connected': '已连接',
        'Disconnected': '未连接',
        'Active': '活跃',
        'Inactive': '非活跃',
        
        // 操作按钮
        'Start': '启动',
        'Stop': '停止',
        'Restart': '重启',
        'Refresh': '刷新',
        'Save': '保存',
        'Cancel': '取消',
        'Delete': '删除',
        'Edit': '编辑',
        'Create': '创建',
        'Add': '添加',
        'Remove': '移除',
        'Configure': '配置',
        
        // 会话相关
        'Session': '会话',
        'New Session': '新会话',
        'History': '历史',
        'Messages': '消息',
        'Tokens': 'Token',
        'Model': '模型',
        
        // 记忆相关
        'Search': '搜索',
        'Files': '文件',
        'Chunks': '片段',
        'Sources': '来源',
        
        // 技能相关
        'Available': '可用',
        'Installed': '已安装',
        'Ready': '就绪',
        'Missing': '缺失',
        'Description': '描述',
        
        // 网关相关
        'Port': '端口',
        'Mode': '模式',
        'Auth': '认证',
        'Tailscale': 'Tailscale',
        'Local': '本地',
        'Public': '公开',
        
        // 状态信息
        'Healthy': '健康',
        'Warning': '警告',
        'Error': '错误',
        'Critical': '严重',
        'Info': '信息',
        
        // 时间相关
        'Just now': '刚刚',
        'minutes ago': '分钟前',
        'hours ago': '小时前',
        'days ago': '天前',
        'Last updated': '最后更新',
        
        // 其他
        'Workspace': '工作区',
        'Version': '版本',
        'Update': '更新',
        'Available': '可用',
        'Required': '必需',
        'Optional': '可选',
        'Enabled': '已启用',
        'Disabled': '已禁用',
        'Loading': '加载中...',
        'Processing': '处理中...',
        'Success': '成功',
        'Failed': '失败',
        'Done': '完成',
    };

    // 替换文本的函数
    function translateText(text) {
        if (!text || typeof text !== 'string') return text;
        
        let result = text;
        for (const [en, zh] of Object.entries(translations)) {
            // 使用正则进行全局替换，忽略大小写
            const regex = new RegExp(en.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
            result = result.replace(regex, zh);
        }
        return result;
    }

    // 遍历并翻译 DOM 元素
    function translatePage() {
        // 翻译所有文本节点
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        const textNodes = [];
        let node;
        while (node = walker.nextNode()) {
            if (node.textContent.trim()) {
                textNodes.push(node);
            }
        }

        textNodes.forEach(node => {
            const translated = translateText(node.textContent);
            if (translated !== node.textContent) {
                node.textContent = translated;
            }
        });

        // 翻译 placeholder 属性
        document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(el => {
            if (el.placeholder) {
                el.placeholder = translateText(el.placeholder);
            }
        });

        // 翻译 title 属性
        document.querySelectorAll('[title]').forEach(el => {
            if (el.title) {
                el.title = translateText(el.title);
            }
        });

        // 翻译按钮文本
        document.querySelectorAll('button').forEach(btn => {
            if (btn.textContent.trim()) {
                btn.textContent = translateText(btn.textContent);
            }
        });
    }

    // 初始化翻译
    function init() {
        // 页面加载完成后翻译
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                translatePage();
                // 监听 DOM 变化，处理动态加载的内容
                observeChanges();
            });
        } else {
            translatePage();
            observeChanges();
        }
    }

    // 监听 DOM 变化
    function observeChanges() {
        const observer = new MutationObserver((mutations) => {
            let shouldTranslate = false;
            mutations.forEach(mutation => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    shouldTranslate = true;
                }
            });
            
            if (shouldTranslate) {
                // 使用 requestAnimationFrame 避免频繁翻译
                requestAnimationFrame(() => {
                    translatePage();
                });
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // 启动
    init();
    
    // 添加手动翻译按钮（调试用）
    function addManualButton() {
        const btn = document.createElement('button');
        btn.textContent = '🌐 切换中文';
        btn.style.cssText = 'position:fixed;top:10px;right:10px;z-index:99999;padding:8px 16px;background:#007acc;color:white;border:none;border-radius:4px;cursor:pointer;font-size:14px;';
        btn.onclick = function() {
            translatePage();
            alert('翻译完成！如果界面没有变化，请刷新页面。');
        };
        document.body.appendChild(btn);
    }
    
    // 延迟添加按钮，确保 body 已存在
    if (document.body) {
        addManualButton();
    } else {
        setTimeout(addManualButton, 1000);
    }
    
    console.log('[OpenClaw 汉化脚本] 已加载 - 当前URL:', location.href);
    console.log('[OpenClaw 汉化脚本] 等待2秒后自动翻译...');
    
    // 延迟翻译，确保页面完全加载
    setTimeout(() => {
        translatePage();
        console.log('[OpenClaw 汉化脚本] 自动翻译完成');
    }, 2000);
})();