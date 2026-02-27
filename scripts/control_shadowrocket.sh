#!/bin/bash
# Shadowrocket 控制器脚本
# 用途：启动 Shadowrocket 并选择新加坡2节点

# 检查 Shadowrocket 是否运行
if ! pgrep -x "Shadowrocket" > /dev/null; then
    echo "启动 Shadowrocket..."
    open -a "Shadowrocket"
    sleep 3
fi

# 使用 AppleScript 控制 Shadowrocket
osascript << 'APPLESCRIPT'
tell application "System Events"
    tell process "Shadowrocket"
        -- 等待窗口加载
        delay 2
        
        -- 尝试点击菜单栏图标
        try
            click menu bar item 1 of menu bar 2
            delay 1
            
            -- 尝试找到"新加坡2"节点
            -- 注意：这取决于实际UI结构，可能需要调整
            click menu item "新加坡2" of menu 1 of menu bar item 1 of menu bar 2
        on error errMsg
            display notification "无法自动选择节点，请手动选择" with title "Shadowrocket 控制器"
        end try
    end tell
end tell
APPLESCRIPT

echo "Shadowrocket 控制脚本执行完成"
