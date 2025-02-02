import ctypes
import ctypes.wintypes

import win32gui
from win32con import STATE_SYSTEM_INVISIBLE


def get_visible_window_titles():
    """
    Retrieves a list of visible window titles.

    Returns
    -------
    list of str
        A sorted list of visible window titles.
    """

    class TITLEBARINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.wintypes.DWORD),
            ("rcTitleBar", ctypes.wintypes.RECT),
            ("rgstate", ctypes.wintypes.DWORD * 6)
        ]

    visible_titles = []

    def callback(hwnd, _):
        # Title bar info initialization
        title_info = TITLEBARINFO()
        title_info.cbSize = ctypes.sizeof(title_info)
        ctypes.windll.user32.GetTitleBarInfo(hwnd, ctypes.byref(title_info))

        # Check if the window is cloaked
        isCloaked = ctypes.c_int(0)
        ctypes.WinDLL("dwmapi").DwmGetWindowAttribute(hwnd, 14, ctypes.byref(isCloaked), ctypes.sizeof(isCloaked))

        # Get window title
        title = win32gui.GetWindowText(hwnd)

        # Append visible windows to list
        if not win32gui.IsIconic(hwnd) and win32gui.IsWindowVisible(hwnd) and title and isCloaked.value == 0:
            if not (title_info.rgstate[0] & STATE_SYSTEM_INVISIBLE):
                visible_titles.append(title)

    win32gui.EnumWindows(callback, None)
    return sorted(visible_titles)
