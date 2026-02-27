#!/bin/bash
# Shadowrocket 自动化控制脚本 v2.0
# 支持：启动、检查状态、断开/重连

COMMAND="${1:-status}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

check_running() {
    if pgrep -x "Shadowrocket" > /dev/null; then
        return 0
    else
        return 1
    fi
}

get_status() {
    osascript -e '
    tell application "System Events"
        tell process "Shadowrocket"
            try
                click menu bar item 1 of menu bar 2
                delay 0.5
                set menuItems to name of every menu item of menu 1 of menu bar item 1 of menu bar 2
                return menuItems as string
            on error errMsg
                return "ERROR: " & errMsg
            end try
        end tell
    end tell' 2>&1
}

start_shadowrocket() {
    log "启动 Shadowrocket..."
    open -a "Shadowrocket"
    sleep 3
    
    if check_running; then
        log "✅ Shadowrocket 已启动"
        return 0
    else
        log "❌ 启动失败"
        return 1
    fi
}

case "$COMMAND" in
    start)
        if check_running; then
            log "Shadowrocket 已在运行"
        else
            start_shadowrocket
        fi
        ;;
        
    status)
        if ! check_running; then
            log "❌ Shadowrocket 未运行"
            exit 1
        fi
        
        status=$(get_status)
        log "当前状态: $status"
        
        if echo "$status" | grep -q "已连接"; then
            log "✅ VPN 已连接"
            echo "$status" | grep -o "已连接: [^ ]*"
        elif echo "$status" | grep -q "未连接"; then
            log "⚠️ VPN 未连接"
        else
            log "⚠️ 状态未知"
        fi
        ;;
        
    stop|disconnect)
        if ! check_running; then
            log "Shadowrocket 未运行"
            exit 0
        fi
        
        log "断开 VPN 连接..."
        osascript -e '
        tell application "System Events"
            tell process "Shadowrocket"
                click menu bar item 1 of menu bar 2
                delay 0.5
                -- 尝试找到断开/关闭选项
                try
                    click menu item "关闭 Shadowrocket" of menu 1 of menu bar item 1 of menu bar 2
                on error
                    try
                        click menu item "断开" of menu 1 of menu bar item 1 of menu bar 2
                    on error
                        return "未找到断开选项"
                    end try
                end try
            end tell
        end tell' 2>&1
        
        log "已执行断开操作"
        ;;
        
    restart|reconnect)
        log "重新连接 VPN..."
        $0 stop
        sleep 2
        $0 start
        ;;
        
    select)
        NODE="${2:-新加坡2}"
        log "尝试选择节点: $NODE"
        
        # 打开主窗口
        osascript -e '
        tell application "System Events"
            tell process "Shadowrocket"
                click menu bar item 1 of menu bar 2
                delay 0.5
                click menu item "打开 Shadowrocket" of menu 1 of menu bar item 1 of menu bar 2
            end tell
        end tell' 2>&1
        
        log "已打开 Shadowrocket 主窗口，请手动选择节点: $NODE"
        log "💡 提示: 建议将 '$NODE' 设为默认节点，这样启动后自动连接"
        ;;
        
    *)
        echo "用法: $0 [start|stop|restart|status|select <节点名>]"
        echo ""
        echo "命令说明:"
        echo "  start              - 启动 Shadowrocket"
        echo "  stop/disconnect    - 断开连接"
        echo "  restart/reconnect  - 重新连接"
        echo "  status             - 查看当前状态"
        echo "  select <节点名>    - 选择指定节点（需要手动配合）"
        echo ""
        echo "当前状态:"
        $0 status 2>/dev/null || echo "无法获取状态"
        ;;
esac
