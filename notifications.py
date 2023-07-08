import ctypes
import ctypes.wintypes
import threading

# Load required Windows API functions
user32 = ctypes.WinDLL('user32')
shell32 = ctypes.WinDLL('shell32')
kernel32 = ctypes.WinDLL('kernel32')
w = ctypes.wintypes


message_loop_running = False
# Constants for Windows API functions and structures
NIM_ADD = 0x00000000
NIF_INFO = 0x00000010
NIM_DELETE = 0x00000002
WM_USER = 0x0400
MSG = w.MSG()
CLICKED = False
NID = 0
# Callback function for notification click event
def notification_callback(hwnd, msg, wparam, lparam):
    global message_loop_running,CLICKED
    print(f"{lparam=} from callback, {message_loop_running=}")
    if lparam == 1029:  # Notification clicked
        print("Notification clicked!")
        CLICKED = True
        message_loop_running = False
        user32.PostMessageW (hwnd, msg,wparam,lparam)
        return user32.DefWindowProcW(hwnd, msg, wparam, ctypes.c_void_p(lparam))
    if lparam == 1028:
        CLICKED = False
        message_loop_running = False
        user32.PostMessageW (hwnd, msg,wparam,lparam)
        return user32.DefWindowProcW(hwnd, msg, wparam, ctypes.c_void_p(lparam))
    return user32.DefWindowProcW(hwnd, msg, wparam, ctypes.c_void_p(lparam))

def PostThreadMessage(tid):
    user32.PostThreadMessageW(tid, 0x0012, 0, 0)

def start_message_loop():
    msg = MSG
    global message_loop_running
    message_loop_running = True

    print(f"{message_loop_running=} from line 31")
    while message_loop_running:
        print('insid while')
        print(f"{message_loop_running=} {msg=} {msg.message=}, {msg.lParam=} {msg.wParam=}")
        if msg.lParam == 13371337:
            break
        if not message_loop_running:
            return 1
        if msg.message == 2 or msg.message == 0x0002:
            break
        if user32.GetMessageW(ctypes.byref(msg), None, 0, 0):
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
            
       
    print('exited_message_loop')
    return 1

def show_notification(title, message):
    # Define WNDPROC callback function type
    
    WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_long, w.HWND, w.UINT, w.WPARAM, ctypes.c_void_p)
    HCURSOR = ctypes.c_void_p
    global message_loop_running
    global NID
    global CLICKED
    CLICKED = False

    # Define the WNDCLASS structure
    class WNDCLASS(ctypes.Structure):
        _fields_ = [
            ("style", w.UINT),
            ("lpfnWndProc", WNDPROC),
            ("cbClsExtra", ctypes.c_int),
            ("cbWndExtra", ctypes.c_int),
            ("hInstance", w.HINSTANCE),
            ("hIcon", w.HICON),
            ("hCursor", HCURSOR),
            ("hbrBackground", w.HBRUSH),
            ("lpszMenuName", w.LPCWSTR),
            ("lpszClassName", w.LPCWSTR)
        ]
    class NOTIFYICONDATA(ctypes.Structure):
        _fields_ = [
            ("cbSize", w.DWORD),
            ("hWnd", w.HWND),
            ("uID", w.UINT),
            ("uFlags", w.UINT),
            ("uCallbackMessage", w.UINT),
            ("hIcon", w.HICON),
            ("szTip", w.WCHAR * 128),
            ("dwState", w.DWORD),
            ("dwStateMask", w.DWORD),
            ("szInfo", w.WCHAR * 256),
            ("uTimeout", w.UINT),
            ("szInfoTitle", w.WCHAR * 64),
            ("dwInfoFlags", w.DWORD),
        ]

    # Register the window class
    wnd_class = WNDPROC(notification_callback)
    CALLBACK_TYPE = ctypes.WINFUNCTYPE(
        ctypes.c_long, w.HWND, w.UINT, w.WPARAM, ctypes.c_void_p
    )
    callback_func = CALLBACK_TYPE(notification_callback)

    wnd_class_name = "PythonNotificationWindowClass"
    wc = WNDCLASS()
    wc.lpfnWndProc = callback_func
    wc.lpszClassName = wnd_class_name
    wc.hInstance = kernel32.GetModuleHandleW(None)
    user32.RegisterClassW(ctypes.byref(wc))

    # Create the window
    hwnd = user32.CreateWindowExW(
        0, wc.lpszClassName, "Python Notification Window", 0, 0, 0, 0, 0,
        None, None, wc.hInstance, None
    )

    # Display the notification using Shell_NotifyIconW
    nid = NOTIFYICONDATA()
    nid.cbSize = ctypes.sizeof(nid)
    nid.hWnd = hwnd
    nid.uID = 0
    nid.uFlags = NIF_INFO
    nid.uCallbackMessage = WM_USER + 20
    nid.hIcon = None
    nid.szInfo = message
    nid.szInfoTitle = title
    nid.dwInfoFlags = 1
    nid.uTimeout = 10
    shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid))

    # Run the message loop to handle the notification
    print(f"{message_loop_running=}")
    if not message_loop_running:
        
        start_message_loop()
        print('after x done?')
    # Clean up
    shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(nid))
   
    user32.UnregisterClassW(wc.lpszClassName, wc.hInstance)
    user32.DestroyWindow(hwnd)
    return CLICKED

