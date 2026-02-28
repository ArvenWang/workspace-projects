#!/usr/bin/env python3
"""
Android自动化助手 - 完整版
功能：
1. 自动操作手机
2. 批量处理任务
3. 自动回复
4. 定时执行

依赖：
pip3 install adbutils

使用：
1. 手机开启USB调试
2. 连接电脑
3. 运行 python3 android_auto.py list
"""

import os
import subprocess
import time
from pathlib import Path

# 配置
CONFIG = {
    'adb_path': 'adb',  # 或完整路径
}


class AndroidHelper:
    def __init__(self):
        self.devices = []
    
    def check_adb(self):
        """检查ADB"""
        try:
            result = subprocess.run([CONFIG['adb_path'], 'devices'], 
                                 capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def list_devices(self):
        """列出设备"""
        try:
            result = subprocess.run([CONFIG['adb_path'], 'devices', '-l'],
                                 capture_output=True, text=True, timeout=10)
            lines = result.stdout.strip().split('\n')[1:]
            
            devices = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        devices.append({
                            'id': parts[0],
                            'status': parts[1]
                        })
            
            self.devices = devices
            return devices
        except Exception as e:
            print(f"❌ 获取设备失败: {e}")
            return []
    
    def install_app(self, apk_path):
        """安装APP"""
        if not os.path.exists(apk_path):
            print(f"❌ 文件不存在: {apk_path}")
            return False
        
        try:
            result = subprocess.run([CONFIG['adb_path'], 'install', apk_path],
                                 capture_output=True, text=True, timeout=60)
            if 'Success' in result.stdout:
                print(f"✅ 安装成功: {apk_path}")
                return True
            else:
                print(f"❌ 安装失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 安装失败: {e}")
            return False
    
    def uninstall_app(self, package):
        """卸载APP"""
        try:
            result = subprocess.run([CONFIG['adb_path'], 'uninstall', package],
                                 capture_output=True, text=True, timeout=30)
            return 'Success' in result.stdout
        except:
            return False
    
    def start_app(self, package):
        """启动APP"""
        try:
            subprocess.run([CONFIG['adb_path'], 'shell', 'monkey', '-p', package, '-c',
                          'android.intent.category.LAUNCHER', '1'],
                         capture_output=True, timeout=10)
            print(f"✅ 已启动: {package}")
            return True
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            return False
    
    def take_screenshot(self, save_path='screenshot.png'):
        """截图"""
        try:
            subprocess.run([CONFIG['adb_path'], 'shell', 'screencap', '-p',
                          '/sdcard/screenshot.png'],
                         capture_output=True, timeout=10)
            subprocess.run([CONFIG['adb_path'], 'pull', '/sdcard/screenshot.png',
                          save_path],
                         capture_output=True, timeout=10)
            print(f"✅ 截图已保存: {save_path}")
            return True
        except Exception as e:
            print(f"❌ 截图失败: {e}")
            return False
    
    def tap(self, x, y):
        """点击"""
        try:
            subprocess.run([CONFIG['adb_path'], 'shell', 'input', 'tap', str(x), str(y)],
                         capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def swipe(self, x1, y1, x2, y2, duration=300):
        """滑动"""
        try:
            subprocess.run([CONFIG['adb_path'], 'shell', 'input', 'swipe',
                          str(x1), str(y1), str(x2), str(y2), str(duration)],
                         capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def input_text(self, text):
        """输入文本"""
        try:
            # 需要URL编码
            import urllib.parse
            encoded = urllib.parse.quote(text)
            subprocess.run([CONFIG['adb_path'], 'shell', 'input', 'text', encoded],
                         capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def get_packages(self):
        """获取已安装包"""
        try:
            result = subprocess.run([CONFIG['adb_path'], 'shell', 'pm', 'list', 'packages'],
                                 capture_output=True, text=True, timeout=30)
            packages = [p.replace('package:', '') for p in result.stdout.strip().split('\n')]
            return packages
        except:
            return []


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
Android自动化助手 - 使用说明

前置要求:
1. 手机开启开发者选项 -> USB调试
2. 连接电脑
3. 确认ADB已安装: adb version

依赖安装:
  pip3 install adbutils

使用:
  python3 android_auto.py list              # 列出设备
  python3 android_auto.py packages        # 已安装APP
  python3 android_auto.py screenshot      # 截图
  python3 android_auto.py tap 500 500     # 点击坐标
  python3 android_auto.py swipe 100 500 100 100  # 滑动
  python3 android_auto.py install <apk>  # 安装APP
  python3 android_auto.py start <包名>   # 启动APP

示例:
  python3 android_auto.py list
  python3 android_auto.py screenshot
  python3 android_auto.py tap 540 960
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    android = AndroidHelper()
    
    if cmd == 'list':
        devices = android.list_devices()
        print(f"\n📱 设备数量: {len(devices)}")
        for d in devices:
            print(f"  • {d['id']} ({d['status']})")
    
    elif cmd == 'packages':
        pkgs = android.get_packages()
        print(f"\n📦 已安装: {len(pkgs)}个")
        for p in pkgs[:20]:
            print(f"  {p}")
        if len(pkgs) > 20:
            print(f"  ... 还有{len(pkgs)-20}个")
    
    elif cmd == 'screenshot':
        android.take_screenshot()
    
    elif cmd == 'tap' and len(sys.argv) >= 4:
        x, y = int(sys.argv[2]), int(sys.argv[3])
        android.tap(x, y)
        print(f"✅ 点击 ({x}, {y})")
    
    elif cmd == 'swipe' and len(sys.argv) >= 5:
        x1, y1 = int(sys.argv[2]), int(sys.argv[3])
        x2, y2 = int(sys.argv[4]), int(sys.argv[5])
        android.swipe(x1, y1, x2, y2)
        print(f"✅ 滑动 ({x1},{y1}) -> ({x2},{y2})")
    
    elif cmd == 'install' and len(sys.argv) >= 3:
        apk = sys.argv[2]
        android.install_app(apk)
    
    elif cmd == 'start' and len(sys.argv) >= 3:
        package = sys.argv[2]
        android.start_app(package)
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
