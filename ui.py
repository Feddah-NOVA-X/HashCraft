

__all__ = ['start', 'exit_program', 'clear', 'custom_time', 'show_progress_bar', 'new_last_percent']

import os
import sys
import time


last_percent = 0


def start():
    from hasher import Hasher
    print('\n'*2)
    print(f"{' '*20}--- Hash calculator ---")
    print('\n'*2)
    
    print("Description:")
    print(f"{' '*5}- You can calculate the hash of any file and specify the type of hash you want.\n\n")
    
    user_input = input("Press any key to start | 0] Exit: ")
    if user_input == '0':
        exit_program()
        clear()
        return None
    
    hash = Hasher()
    res = hash.record_details()
    if res is None:
        hash.clear_log()
        return None
    
    print("\n✨ Thank you for your trust. Would you like to continue?")
    custom_time(1.5)
    return True

def exit_program():
    try:
        user_input = input("Enter 0 to exit | [ENTER] Stay: ")
        if user_input == '0':
            print("user exit.")
            sys.exit(0)
        else:
            return None
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
    except Exception:
        return None
    
def clear():
    '''داله للمسح الكامل'''
    os.system('cls' if os.name == 'nt' else 'clear')

def custom_time(t=2.5):
    '''داله الانتظار - توقف مؤقت للبرنامج'''
    if not isinstance(t, (float,int)): t = 2.5
    time.sleep(float(t))
    
    
def show_progress_bar(percentage, text="Processing"):
    """
    يعرض شريط تقدم مستمر، يكمل من آخر نسبة وصل إليها.
    percentage: النسبة المضافة (وليست المطلقة)
    text: النص الذي يظهر بجانب الشريط
    """
    global last_percent

    # النسبة النهائية بعد الإضافة
    target_percentage = min(100, last_percent + percentage)
    bar_length = 100

    # نبدأ من آخر نسبة وصلنا إليها
    for i in range(last_percent, target_percentage + 1):
        percent = i
        filled_length = int(bar_length * i / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)

        print(f'\r\033[K|{bar}| {percent}% {text}', end="", flush=True)
        time.sleep(0.02)

    # تحديث last_percent
    last_percent = target_percentage
  
def new_last_percent():
    global last_percent
    last_percent = 0