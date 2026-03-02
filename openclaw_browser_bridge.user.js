// ==UserScript==
// @name         OpenClaw Browser Bridge
// @namespace    http://openclaw.ai
// @version      1.0
// @description  让 AI 能控制你的浏览器 - 保留登录状态
// @author       OpenClaw
// @match        *://*/*
// @grant        none
// @connect      localhost
// @run-at       document-start
// ==/UserScript==

(function() {
    'use strict';

    const SERVER_URL = 'ws://localhost:18765';
    const HEARTBEAT_INTERVAL = 5000;

    let ws = null;
    let sessionId = null;
    let pendingRequests = new Map();
    let heartbeatTimer = null;

    // 生成唯一会话ID
    function generateSessionId() {
        return 'oc_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // 连接到后端
    function connect() {
        sessionId = generateSessionId();
        console.log('[OpenClaw] 连接到:', SERVER_URL, '会话:', sessionId);

        ws = new WebSocket(SERVER_URL);

        ws.onopen = function() {
            console.log('[OpenClaw] 已连接');
            // 发送 ready 消息
            send({
                type: 'ready',
                sessionId: sessionId,
                url: window.location.href,
                title: document.title
            });
            startHeartbeat();
        };

        ws.onmessage = function(event) {
            try {
                const msg = JSON.parse(event.data);
                handleMessage(msg);
            } catch (e) {
                console.error('[OpenClaw] 解析消息失败:', e);
            }
        };

        ws.onclose = function() {
            console.log('[OpenClaw] 连接关闭');
            stopHeartbeat();
            // 尝试重连
            setTimeout(connect, 3000);
        };

        ws.onerror = function(err) {
            console.error('[OpenClaw] WebSocket 错误:', err);
        };
    }

    // 发送消息
    function send(data) {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(data));
        }
    }

    // 处理消息
    function handleMessage(msg) {
        const id = msg.id;
        const code = msg.code;

        if (!id || !code) return;

        try {
            // 执行 JS 代码
            const result = eval(code);
            send({
                type: 'result',
                id: id,
                result: result
            });
        } catch (error) {
            send({
                type: 'error',
                id: id,
                error: error.message || String(error)
            });
        }
    }

    // 心跳
    function startHeartbeat() {
        heartbeatTimer = setInterval(() => {
            send({ type: 'ping' });
        }, HEARTBEAT_INTERVAL);
    }

    function stopHeartbeat() {
        if (heartbeatTimer) {
            clearInterval(heartbeatTimer);
            heartbeatTimer = null;
        }
    }

    // 页面加载完成后尝试连接
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', connect);
    } else {
        connect();
    }

    // 导航变化时通知
    let lastUrl = location.href;
    new MutationObserver(() => {
        if (location.href !== lastUrl) {
            lastUrl = location.href;
            send({
                type: 'navigate',
                sessionId: sessionId,
                url: location.href,
                title: document.title
            });
        }
    }).observe(document, { subtree: true, childList: true });

})();
