import os
import time
from datetime import datetime
import ctypes
from PIL import ImageGrab

# --- CONFIG ---
TRAP_FOLDER = r"C:\SmartFileTrap\Honeypot"
LOG_FILE = r"C:\SmartFileTrap\access_log.txt"
SCREENSHOT_FOLDER = r"C:\SmartFileTrap\screenshots"

# --- CREATE DIRECTORIES IF NEEDED ---
os.makedirs(TRAP_FOLDER, exist_ok=True)
os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)

# --- CHECK LAST MODIFIED TIME ---
file_times = {f: os.path.getmtime(os.path.join(TRAP_FOLDER, f))
              for f in os.listdir(TRAP_FOLDER)}

def alert(msg):
    """Show popup alert"""
    ctypes.windll.user32.MessageBoxW(0, msg, "SmartFileTrap Alert", 1)

def take_screenshot():
    """Take screenshot and save it"""
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.join(SCREENSHOT_FOLDER, f"screenshot_{ts}.png")
    img = ImageGrab.grab()
    img.save(path)
    return path

print("SmartFileTrap Running... Monitoring folder.\n")

while True:
    time.sleep(1)
    current_files = os.listdir(TRAP_FOLDER)

    for f in current_files:
        full_path = os.path.join(TRAP_FOLDER, f)
        last_mod = os.path.getmtime(full_path)

        if f not in file_times:  
            # NEW FILE CREATED
            screenshot = take_screenshot()
            with open(LOG_FILE, "a") as log:
                log.write(f"[{datetime.now()}] NEW FILE ADDED: {f}\nScreenshot: {screenshot}\n\n")
            alert(f"Unauthorized File Created!\nFile: {f}")
            file_times[f] = last_mod

        elif last_mod != file_times[f]:
            # FILE MODIFIED
            screenshot = take_screenshot()
            with open(LOG_FILE, "a") as log:
                log.write(f"[{datetime.now()}] FILE MODIFIED: {f}\nScreenshot: {screenshot}\n\n")
            alert(f"Unauthorized File Modified!\nFile: {f}")
            file_times[f] = last_mod

    # FILE DELETED
    for old_file in list(file_times.keys()):
        if old_file not in current_files:
            screenshot = take_screenshot()
            with open(LOG_FILE, "a") as log:
                log.write(f"[{datetime.now()}] FILE DELETED: {old_file}\nScreenshot: {screenshot}\n\n")
            alert(f"Unauthorized File Deleted!\nFile: {old_file}")
            del file_times[old_file]
