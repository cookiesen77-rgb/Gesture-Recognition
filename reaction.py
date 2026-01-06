import time
import platform

# 跨平台兼容处理
SYSTEM = platform.system()

# 初始化输入控制器
k = None
m = None

if SYSTEM == 'Windows':
    try:
        import win32gui
        from pymouse import PyMouse
        from pykeyboard import PyKeyboard
        k = PyKeyboard()
        m = PyMouse()
    except ImportError as e:
        print(f"Windows 输入模块加载失败: {e}")
        print("请安装: pip install pyuserinput pywin32")
        
elif SYSTEM == 'Darwin':  # macOS
    try:
        from pynput.mouse import Button, Controller as MouseController
        from pynput.keyboard import Key, Controller as KeyboardController
        m = MouseController()
        k = KeyboardController()
    except ImportError:
        print("请安装 pynput: pip install pynput")
        print("并在系统设置中授予辅助功能权限")
        
else:  # Linux
    try:
        from pynput.mouse import Button, Controller as MouseController
        from pynput.keyboard import Key, Controller as KeyboardController
        m = MouseController()
        k = KeyboardController()
    except ImportError:
        print("请安装 pynput: pip install pynput")


def get_app_name():
    """获取当前活动窗口名称"""
    if SYSTEM == 'Windows':
        try:
            import win32gui
            appName = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            print(f"当前窗口: {appName}")
            return appName
        except Exception as e:
            print(f"获取窗口名失败: {e}")
            return "Unknown"
    else:
        # macOS/Linux 暂不支持获取窗口名
        return "Unknown"


def get_app_index():
    """根据窗口名称返回应用索引"""
    name = get_app_name()
    if "照片" in name or "Photos" in name or "Preview" in name or "预览" in name:
        return 1
    elif "PowerPoint" in name or "Keynote" in name:
        return 2
    else:
        print("未在支持程序内执行手势")
        return 99


def catch():
    """抓取动作"""
    print('Done: 抓取')


def tap():
    """模拟鼠标点击"""
    if m is None:
        print("鼠标控制器未初始化")
        return
        
    try:
        if SYSTEM == 'Windows':
            pos = m.position()
            m.click(pos[0], pos[1])
        else:
            from pynput.mouse import Button
            m.click(Button.left)
        print('Done: 点击')
    except Exception as e:
        print(f"点击失败: {e}")


def rotate(app_index: int):
    """模拟旋转操作"""
    if k is None:
        print("键盘控制器未初始化")
        return
        
    try:
        if app_index == 1:
            if SYSTEM == 'Windows':
                k.press_key(k.control_key)
                k.tap_key('r')
                k.release_key(k.control_key)
            else:
                from pynput.keyboard import Key
                mod_key = Key.cmd if SYSTEM == 'Darwin' else Key.ctrl
                k.press(mod_key)
                k.press('r')
                k.release('r')
                k.release(mod_key)
        print('Done: 旋转')
    except Exception as e:
        print(f"旋转失败: {e}")


def move(app_index: int):
    """模拟平移（下一页）"""
    if k is None:
        print("键盘控制器未初始化")
        return
        
    try:
        if app_index == 1 or app_index == 2:
            if SYSTEM == 'Windows':
                k.tap_key(k.right_key)
            else:
                from pynput.keyboard import Key
                k.press(Key.right)
                k.release(Key.right)
        print('Done: 平移')
    except Exception as e:
        print(f"平移失败: {e}")


def zoom(app_index: int, signal: str):
    """模拟缩放"""
    if k is None:
        print("键盘控制器未初始化")
        return
        
    try:
        if app_index == 1:
            if SYSTEM == 'Windows':
                k.press_key(k.control_key)
                k.tap_key(signal)
                k.release_key(k.control_key)
            else:
                from pynput.keyboard import Key
                mod_key = Key.cmd if SYSTEM == 'Darwin' else Key.ctrl
                k.press(mod_key)
                k.press(signal)
                k.release(signal)
                k.release(mod_key)
        elif app_index == 2:
            if SYSTEM == 'Windows':
                k.tap_key(signal)
            else:
                k.press(signal)
                k.release(signal)
        print('Done:', "缩放" if signal == '-' else "放大")
    except Exception as e:
        print(f"缩放失败: {e}")


def screenshot():
    """模拟截图"""
    if k is None:
        print("键盘控制器未初始化")
        return
        
    try:
        if SYSTEM == 'Windows':
            k.press_key(k.windows_l_key)
            k.tap_key(k.print_screen_key)
            k.release_key(k.windows_l_key)
        elif SYSTEM == 'Darwin':
            # macOS: Cmd+Shift+4 (区域截图)
            from pynput.keyboard import Key
            k.press(Key.cmd)
            k.press(Key.shift)
            k.press('4')
            k.release('4')
            k.release(Key.shift)
            k.release(Key.cmd)
        else:
            # Linux: 尝试使用 gnome-screenshot 或 scrot
            import subprocess
            try:
                subprocess.run(['gnome-screenshot', '-a'], check=False)
            except FileNotFoundError:
                try:
                    subprocess.run(['scrot', '-s'], check=False)
                except FileNotFoundError:
                    print("请安装 gnome-screenshot 或 scrot")
        print("Done: 截图")
    except Exception as e:
        print(f"截图失败: {e}")


class Reaction:
    """手势响应类"""
    
    def __init__(self):
        self.enabled = (k is not None or m is not None)
        if not self.enabled:
            print("警告: 输入控制器未初始化，手势响应功能不可用")

    def react(self, target: str):
        """响应手势指令"""
        if not self.enabled:
            print(f"忽略指令 '{target}': 输入控制器未初始化")
            return
            
        app_index = get_app_index()
        
        if target == "点击":
            tap()
        elif target == "平移":
            move(app_index)
        elif target == "旋转":
            rotate(app_index)
        elif target == "抓取":
            catch()
        elif target == "缩放":
            zoom(app_index, '-')
        elif target == "放大":
            zoom(app_index, '+')
        elif target == "截图":
            screenshot()
        else:
            print(f"未知动作: {target}")


if __name__ == '__main__':
    print("3秒后执行测试...")
    time.sleep(3)
    react = Reaction()
    react.react("放大")
