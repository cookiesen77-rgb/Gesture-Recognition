import time
import platform

# 跨平台兼容处理
SYSTEM = platform.system()

if SYSTEM == 'Windows':
    import win32gui
    from pymouse import PyMouse
    from pykeyboard import PyKeyboard
    k = PyKeyboard()
    m = PyMouse()
elif SYSTEM == 'Darwin':  # macOS
    try:
        from pynput.mouse import Button, Controller as MouseController
        from pynput.keyboard import Key, Controller as KeyboardController
        m = MouseController()
        k = KeyboardController()
    except ImportError:
        print("请安装 pynput: pip install pynput")
        m = None
        k = None
else:  # Linux
    try:
        from pynput.mouse import Button, Controller as MouseController
        from pynput.keyboard import Key, Controller as KeyboardController
        m = MouseController()
        k = KeyboardController()
    except ImportError:
        print("请安装 pynput: pip install pynput")
        m = None
        k = None


def get_app_name():
    """获取当前活动窗口名称"""
    if SYSTEM == 'Windows':
        appName = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        print(appName)
        return appName
    else:
        # macOS/Linux 暂不支持获取窗口名
        return "Unknown"


def get_app_index():
    name = get_app_name()
    if "照片" in name or "Photos" in name or "Preview" in name:
        return 1
    elif "PowerPoint" in name or "Keynote" in name:
        return 2
    else:
        print("未在支持程序内执行手势")
        return 99


def catch():
    print('Done：抓取')


def tap():
    """模拟鼠标点击"""
    if SYSTEM == 'Windows':
        m.click(m.position()[0], m.position()[1])
    elif m is not None:
        m.click(Button.left)
    print('Done：点击')


def rotate(app_index: int):
    """模拟旋转操作"""
    if app_index == 1:
        if SYSTEM == 'Windows':
            k.press_key(k.control_key)
            k.tap_key('r')
            k.release_key(k.control_key)
        elif k is not None:
            if SYSTEM == 'Darwin':
                k.press(Key.cmd)
                k.press('r')
                k.release('r')
                k.release(Key.cmd)
            else:
                k.press(Key.ctrl)
                k.press('r')
                k.release('r')
                k.release(Key.ctrl)
    print('Done：旋转')


def move(app_index: int):
    """模拟平移（下一页）"""
    if app_index == 1 or app_index == 2:
        if SYSTEM == 'Windows':
            k.tap_key(k.right_key)
        elif k is not None:
            k.press(Key.right)
            k.release(Key.right)
    print('Done：平移')


def zoom(app_index: int, signal: str):
    """模拟缩放"""
    if app_index == 1:
        if SYSTEM == 'Windows':
            k.press_key(k.control_key)
            k.tap_key(signal)
            k.release_key(k.control_key)
        elif k is not None:
            mod_key = Key.cmd if SYSTEM == 'Darwin' else Key.ctrl
            k.press(mod_key)
            k.press(signal)
            k.release(signal)
            k.release(mod_key)
    elif app_index == 2:
        if SYSTEM == 'Windows':
            k.tap_key(signal)
        elif k is not None:
            k.press(signal)
            k.release(signal)
    print('Done：', "缩放" if signal == '-' else "放大")


def screenshot():
    """模拟截图"""
    if SYSTEM == 'Windows':
        k.press_key(k.windows_l_key)
        k.tap_key(k.print_screen_key)
        k.release_key(k.windows_l_key)
    elif SYSTEM == 'Darwin' and k is not None:
        # macOS: Cmd+Shift+4
        k.press(Key.cmd)
        k.press(Key.shift)
        k.press('4')
        k.release('4')
        k.release(Key.shift)
        k.release(Key.cmd)
    elif k is not None:
        # Linux: Print Screen
        k.press(Key.print_screen)
        k.release(Key.print_screen)
    print("Done：截图")


class Reaction:
    def __init__(self):
        pass

    def react(self, target: str):
        appIndex = get_app_index()
        if target == "点击":
            tap()
        elif target == "平移":
            move(appIndex)
        elif target == "旋转":
            rotate(appIndex)
        elif target == "抓取":
            catch()
        elif target == "缩放":
            zoom(appIndex, '-')
        elif target == "放大":
            zoom(appIndex, '+')
        elif target == "截图":
            screenshot()
        else:
            print("未添加此动作")


if __name__ == '__main__':
    time.sleep(3)
    react = Reaction()
    react.react("放大")
