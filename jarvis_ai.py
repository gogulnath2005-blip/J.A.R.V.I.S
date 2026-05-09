"""
╔══════════════════════════════════════════════════════════════╗
║           J.A.R.V.I.S  —  FINAL YEAR PROJECT                 ║
║     Just A Rather Very Intelligent System  v3.0              ║
║                                                              ║
║  REQUIREMENTS:                                               ║
║    pip install SpeechRecognition pyttsx3 opencv-python       ║
║                pillow wikipedia psutil pyautogui             ║
║                                                              ║
║  USAGE:  python jarvis_ai.py                                 ║
║          Place your  jarvis.gif  in the same folder          ║
╚══════════════════════════════════════════════════════════════╝
"""

import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import threading
import subprocess
import random
import sys
import platform
import time

# ── Optional OpenCV ────────────────────────────────────────────────────────────
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Warning: opencv-python not found.  pip install opencv-python")

# ── Optional Pillow (for GIF fallback) ────────────────────────────────────────
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ── Optional Wikipedia ─────────────────────────────────────────────────────────
try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
except ImportError:
    WIKIPEDIA_AVAILABLE = False

# ── Optional psutil ────────────────────────────────────────────────────────────
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# ── OS detection ───────────────────────────────────────────────────────────────
OS = platform.system()   # 'Windows' | 'Darwin' | 'Linux'

# ── Global state ───────────────────────────────────────────────────────────────
jarvis_text     = "INITIALIZING..."
status_text     = "SYSTEM ONLINE"
exit_flag       = False
listening_flag  = False
text_lock       = threading.Lock()


# ══════════════════════════════════════════════════════════════════════════════
#  VOICE ENGINE
# ══════════════════════════════════════════════════════════════════════════════
engine = None

def init_engine():
    global engine
    for backend in ['sapi5', 'espeak', None]:
        try:
            engine = pyttsx3.init(backend) if backend else pyttsx3.init()
            voices = engine.getProperty('voices')
            # Prefer a male voice for JARVIS feel
            male_voice = None
            for v in (voices or []):
                if any(k in v.name.lower() for k in ('david', 'mark', 'male', 'george', 'zira')):
                    if 'zira' not in v.name.lower():   # skip female
                        male_voice = v.id
                        break
            engine.setProperty('voice', male_voice or (voices[0].id if voices else ''))
            engine.setProperty('rate', 160)
            engine.setProperty('volume', 1.0)
            return
        except Exception:
            continue
    print("Warning: No TTS backend found. Running silently.")
    engine = None

init_engine()

_tts_lock = threading.Lock()

def speak(text: str):
    global jarvis_text, status_text
    print(f"\n[JARVIS] {text}")
    with text_lock:
        jarvis_text = text.upper()[:60]
    if engine:
        with _tts_lock:
            try:
                engine.say(text)
                engine.runAndWait()
            except RuntimeError:
                pass
            except Exception as e:
                print(f"[TTS Error] {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  NATIVE APP LAUNCHER
# ══════════════════════════════════════════════════════════════════════════════

def _win_system32(exe):
    root = os.environ.get("SystemRoot", r"C:\Windows")
    return os.path.join(root, "System32", exe)

def _pf(*parts):
    """Build path under Program Files, fallback to x86."""
    pf = os.environ.get("ProgramFiles", r"C:\Program Files")
    pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    p1 = os.path.join(pf,   *parts)
    p2 = os.path.join(pf86, *parts)
    return p1 if os.path.exists(p1) else p2

def _appdata(*parts):
    return os.path.join(os.environ.get("APPDATA", ""), *parts)

def _localappdata(*parts):
    return os.path.join(os.environ.get("LOCALAPPDATA", ""), *parts)


WINDOWS_APPS = {
    # ── System32 ──────────────────────────────────────────────────────────────
    "calculator":     (_win_system32("calc.exe"),      []),
    "calc":           (_win_system32("calc.exe"),      []),
    "notepad":        (_win_system32("notepad.exe"),   []),
    "paint":          (_win_system32("mspaint.exe"),   []),
    "task manager":   (_win_system32("taskmgr.exe"),   []),
    "taskmgr":        (_win_system32("taskmgr.exe"),   []),
    "cmd":            (_win_system32("cmd.exe"),       []),
    "command prompt": (_win_system32("cmd.exe"),       []),
    "powershell":     (_win_system32("powershell.exe"),[]),
    "control panel":  (_win_system32("control.exe"),  []),
    "file explorer":  (_win_system32("explorer.exe"), []),
    "explorer":       (_win_system32("explorer.exe"), []),
    "snipping tool":  (_win_system32("SnippingTool.exe"), []),
    "sticky notes":   (_win_system32("StikyNot.exe"), []),
    "wordpad":        (_pf("Windows NT","Accessories","wordpad.exe"), []),
    "clock":          (None, ["ms-clock:"]),      # UWP
    "settings":       (None, ["ms-settings:"]),
    "camera":         (None, ["microsoft.windows.camera:"]),
    "photos":         (None, ["ms-photos:"]),
    "maps":           (None, ["bingmaps:"]),
    "mail":           (None, ["ms-mail:"]),
    "weather":        (None, ["bingweather:"]),
    "store":          (None, ["ms-windows-store:"]),
    "xbox":           (None, ["xbox:"]),
    # ── Installed apps ────────────────────────────────────────────────────────
    "chrome":         (_pf("Google","Chrome","Application","chrome.exe"),          []),
    "firefox":        (_pf("Mozilla Firefox","firefox.exe"),                       []),
    "edge":           (_pf("Microsoft","Edge","Application","msedge.exe"),         []),
    "vlc":            (_pf("VideoLAN","VLC","vlc.exe"),                            []),
    "spotify":        (_appdata("Spotify","Spotify.exe"),                          []),
    "discord":        (_localappdata("Discord","Update.exe"),                      ["--processStart", "Discord.exe"]),
    "zoom":           (_appdata("Zoom","bin","Zoom.exe"),                          []),
    "teams":          (_localappdata("Microsoft","Teams","current","Teams.exe"),   []),
    "whatsapp":       (_localappdata("WhatsApp","WhatsApp.exe"),                   []),
    "telegram":       (_appdata("Telegram Desktop","Telegram.exe"),                []),
    "steam":          (_pf("Steam","Steam.exe"),                                   []),
    "vs code":        (_localappdata("Programs","Microsoft VS Code","Code.exe"),   []),
    "vscode":         (_localappdata("Programs","Microsoft VS Code","Code.exe"),   []),
    "visual studio code": (_localappdata("Programs","Microsoft VS Code","Code.exe"), []),
    "pycharm":        (_pf("JetBrains","PyCharm Community Edition","bin","pycharm64.exe"), []),
    "word":           (_pf("Microsoft Office","root","Office16","WINWORD.EXE"),    []),
    "excel":          (_pf("Microsoft Office","root","Office16","EXCEL.EXE"),      []),
    "powerpoint":     (_pf("Microsoft Office","root","Office16","POWERPNT.EXE"),   []),
    "outlook":        (_pf("Microsoft Office","root","Office16","OUTLOOK.EXE"),    []),
    "access":         (_pf("Microsoft Office","root","Office16","MSACCESS.EXE"),   []),
    "skype":          (_appdata("Microsoft","Skype for Desktop","Skype.exe"),      []),
    "obs":            (_pf("obs-studio","bin","64bit","obs64.exe"),                []),
    "blender":        (_pf("Blender Foundation","Blender","blender.exe"),          []),
    "gimp":           (_pf("GIMP 2","bin","gimp-2.10.exe"),                        []),
    "7zip":           (_pf("7-Zip","7zFM.exe"),                                    []),
    "winrar":         (_pf("WinRAR","WinRAR.exe"),                                 []),
    "adobe reader":   (_pf("Adobe","Acrobat DC","Acrobat","Acrobat.exe"),          []),
    "acrobat":        (_pf("Adobe","Acrobat DC","Acrobat","Acrobat.exe"),          []),
}

MACOS_APPS = {
    "calculator":"Calculator","calc":"Calculator","notepad":"TextEdit",
    "textedit":"TextEdit","safari":"Safari","chrome":"Google Chrome",
    "firefox":"Firefox","finder":"Finder","terminal":"Terminal",
    "calendar":"Calendar","contacts":"Contacts","maps":"Maps",
    "photos":"Photos","music":"Music","spotify":"Spotify","vlc":"VLC",
    "discord":"Discord","zoom":"Zoom","teams":"Microsoft Teams",
    "word":"Microsoft Word","excel":"Microsoft Excel",
    "powerpoint":"Microsoft PowerPoint","vs code":"Visual Studio Code",
    "vscode":"Visual Studio Code","visual studio code":"Visual Studio Code",
    "mail":"Mail","notes":"Notes","preview":"Preview",
    "activity monitor":"Activity Monitor","whatsapp":"WhatsApp",
    "telegram":"Telegram","steam":"Steam","skype":"Skype",
}

LINUX_APPS = {
    "calculator":["gnome-calculator","galculator","kcalc","xcalc"],
    "calc":      ["gnome-calculator","galculator","kcalc"],
    "notepad":   ["gedit","mousepad","kate","xed","nano"],
    "terminal":  ["gnome-terminal","xterm","konsole","xfce4-terminal"],
    "files":     ["nautilus","thunar","dolphin","nemo"],
    "file explorer":["nautilus","thunar","dolphin"],
    "vlc":       ["vlc"],
    "chrome":    ["google-chrome","google-chrome-stable","chromium-browser"],
    "firefox":   ["firefox"],
    "vs code":   ["code"],"vscode":["code"],
    "spotify":   ["spotify"],"discord":["discord"],"steam":["steam"],
    "gimp":      ["gimp"],"obs":["obs"],"blender":["blender"],
}

# Apps to close (kill) by process name
CLOSE_MAP_WINDOWS = {
    "chrome":"chrome.exe","firefox":"firefox.exe","edge":"msedge.exe",
    "notepad":"notepad.exe","calculator":"calculator.exe","calc":"calculator.exe",
    "spotify":"Spotify.exe","discord":"Discord.exe","vlc":"vlc.exe",
    "word":"WINWORD.EXE","excel":"EXCEL.EXE","powerpoint":"POWERPNT.EXE",
    "vs code":"Code.exe","vscode":"Code.exe","teams":"Teams.exe",
    "whatsapp":"WhatsApp.exe","zoom":"Zoom.exe","telegram":"Telegram.exe",
    "steam":"Steam.exe","obs":"obs64.exe","blender":"blender.exe",
    "skype":"Skype.exe","task manager":"Taskmgr.exe","cmd":"cmd.exe",
}
CLOSE_MAP_MAC = {k: v.lower().replace(".exe","") for k,v in CLOSE_MAP_WINDOWS.items()}


def launch_windows_app(key: str) -> bool:
    key = key.lower().strip()
    if key not in WINDOWS_APPS:
        return False
    exe, args = WINDOWS_APPS[key]
    # UWP deep-link
    if exe is None and args:
        try:
            os.startfile(args[0])
            return True
        except Exception as e:
            print(f"[UWP error] {e}")
            return False
    if exe and os.path.exists(exe):
        try:
            subprocess.Popen([exe] + args)
            return True
        except Exception as e:
            print(f"[Launch error] {e}")
    # Last-resort: use Windows shell (works for calc, notepad, etc.)
    try:
        base = os.path.basename(exe) if exe else ""
        if base:
            os.startfile(base)
            return True
    except Exception:
        pass
    return False


def launch_macos_app(key: str) -> bool:
    app = MACOS_APPS.get(key.lower().strip())
    if not app:
        return False
    try:
        return subprocess.run(["open","-a",app], capture_output=True).returncode == 0
    except Exception:
        return False


def launch_linux_app(key: str) -> bool:
    candidates = LINUX_APPS.get(key.lower().strip(), [key])
    for cmd in candidates:
        try:
            subprocess.Popen([cmd])
            return True
        except FileNotFoundError:
            continue
    return False


def open_native_app(key: str) -> bool:
    key = key.lower().strip()
    if OS == "Windows":
        return launch_windows_app(key)
    elif OS == "Darwin":
        return launch_macos_app(key)
    elif OS == "Linux":
        return launch_linux_app(key)
    return False


def close_app(key: str) -> bool:
    """Kill a running application by name."""
    key = key.lower().strip()
    if OS == "Windows":
        proc = CLOSE_MAP_WINDOWS.get(key)
        if proc:
            try:
                subprocess.run(["taskkill","/F","/IM", proc],
                               capture_output=True)
                return True
            except Exception:
                pass
    elif OS == "Darwin":
        app = MACOS_APPS.get(key)
        if app:
            try:
                subprocess.run(["pkill","-x", app], capture_output=True)
                return True
            except Exception:
                pass
    elif OS == "Linux":
        candidates = LINUX_APPS.get(key, [key])
        for c in candidates:
            try:
                subprocess.run(["pkill","-x", c], capture_output=True)
                return True
            except Exception:
                pass
    return False


# ══════════════════════════════════════════════════════════════════════════════
#  WEBSITE HELPERS
# ══════════════════════════════════════════════════════════════════════════════
WEBSITES = {
    "youtube":       "https://youtube.com",
    "google":        "https://google.com",
    "instagram":     "https://instagram.com",
    "facebook":      "https://facebook.com",
    "twitter":       "https://twitter.com",
    "x":             "https://twitter.com",
    "github":        "https://github.com",
    "gmail":         "https://mail.google.com",
    "linkedin":      "https://linkedin.com",
    "netflix":       "https://netflix.com",
    "amazon":        "https://amazon.in",
    "wikipedia":     "https://wikipedia.org",
    "reddit":        "https://reddit.com",
    "stackoverflow": "https://stackoverflow.com",
    "chatgpt":       "https://chat.openai.com",
    "claude":        "https://claude.ai",
    "hotstar":       "https://hotstar.com",
    "flipkart":      "https://flipkart.com",
    "whatsapp web":  "https://web.whatsapp.com",
    "maps":          "https://maps.google.com",
    "drive":         "https://drive.google.com",
    "meet":          "https://meet.google.com",
}

NATIVE_FIRST = set(WINDOWS_APPS.keys()) | set(MACOS_APPS.keys()) | \
               set(LINUX_APPS.keys())

def smart_open(phrase: str):
    phrase = phrase.lower().strip()
    for key in sorted(NATIVE_FIRST, key=len, reverse=True):
        if key in phrase:
            if open_native_app(key):
                return True, f"app:{key}"
            break
    for site, url in WEBSITES.items():
        if site in phrase:
            webbrowser.open(url)
            return True, f"web:{site}"
    clean = phrase.replace(" ","")
    if clean:
        webbrowser.open(f"https://{clean}.com")
        return True, f"web:{clean}"
    return False, "none"


# ══════════════════════════════════════════════════════════════════════════════
#  YOUTUBE DIRECT PLAY
# ══════════════════════════════════════════════════════════════════════════════
def play_on_youtube(song: str):
    import urllib.request, re
    query = song.strip()
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    try:
        req = urllib.request.Request(search_url, headers={
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36")
        })
        with urllib.request.urlopen(req, timeout=8) as r:
            html = r.read().decode("utf-8", errors="ignore")
        m = re.search(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        if m:
            webbrowser.open(f"https://www.youtube.com/watch?v={m.group(1)}&autoplay=1")
            speak(f"Playing {query} on YouTube")
            return
    except Exception as e:
        print(f"[YouTube error] {e}")
    webbrowser.open(search_url)
    speak(f"Showing YouTube results for {query}")


# ══════════════════════════════════════════════════════════════════════════════
#  SYSTEM CONTROLS
# ══════════════════════════════════════════════════════════════════════════════
def system_shutdown():
    speak("Initiating system shutdown. Goodbye.")
    if OS == "Windows":
        subprocess.run(["shutdown","/s","/t","5"])
    elif OS in ("Darwin","Linux"):
        subprocess.run(["shutdown","-h","now"])

def system_restart():
    speak("Restarting the system.")
    if OS == "Windows":
        subprocess.run(["shutdown","/r","/t","5"])
    elif OS in ("Darwin","Linux"):
        subprocess.run(["shutdown","-r","now"])

def system_sleep():
    speak("Putting the system to sleep.")
    if OS == "Windows":
        subprocess.run(["rundll32","powrprof.dll,SetSuspendState","0,1,0"])
    elif OS == "Darwin":
        subprocess.run(["pmset","sleepnow"])
    elif OS == "Linux":
        subprocess.run(["systemctl","suspend"])

def lock_screen():
    speak("Locking the screen.")
    if OS == "Windows":
        subprocess.run(["rundll32","user32.dll,LockWorkStation"])
    elif OS == "Darwin":
        subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/"
                        "Contents/Resources/CGSession","-suspend"])
    elif OS == "Linux":
        for cmd in [["gnome-screensaver-command","--lock"],
                    ["xdg-screensaver","lock"],["xscreensaver-command","-lock"]]:
            try:
                subprocess.run(cmd); break
            except Exception:
                pass

def get_battery():
    if not PSUTIL_AVAILABLE:
        return None
    b = psutil.sensors_battery()
    return b

def get_cpu_ram():
    if not PSUTIL_AVAILABLE:
        return None, None
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    return cpu, ram

def take_screenshot():
    try:
        import pyautogui
        fn = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pyautogui.screenshot(fn)
        return fn
    except ImportError:
        return None

def get_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unavailable"


# ══════════════════════════════════════════════════════════════════════════════
#  HUD DISPLAY  (OpenCV + GIF)
# ══════════════════════════════════════════════════════════════════════════════

# All your system-generated app keys for recognizing "close" commands
ALL_APP_KEYS = sorted(
    set(WINDOWS_APPS.keys()) | set(MACOS_APPS.keys()) | set(LINUX_APPS.keys()),
    key=len, reverse=True
)

def draw_hud_overlay(frame):
    """Draw a sleek cyan HUD overlay on the frame."""
    h, w = frame.shape[:2]

    # ── Semi-transparent dark overlay strips ──────────────────────────────────
    overlay = frame.copy()
    # Top bar
    cv2.rectangle(overlay, (0,0), (w, 55), (0,0,0), -1)
    # Bottom bar
    cv2.rectangle(overlay, (0, h-70), (w, h), (0,0,0), -1)
    # Side panels (subtle)
    cv2.rectangle(overlay, (0,55), (12, h-70), (0,10,10), -1)
    cv2.rectangle(overlay, (w-12,55), (w, h-70), (0,10,10), -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    cyan  = (255, 230, 0)    # BGR cyan-gold
    teal  = (200, 200, 0)
    white = (255, 255, 255)
    dim   = (120, 120, 0)

    font  = cv2.FONT_HERSHEY_COMPLEX
    mono  = cv2.FONT_HERSHEY_PLAIN

    # ── Top bar ───────────────────────────────────────────────────────────────
    cv2.line(frame, (0,55), (w,55), cyan, 1)
    # Logo
    cv2.putText(frame, "J.A.R.V.I.S", (12,38), font, 1.0, cyan, 2)
    # Time
    now = datetime.datetime.now()
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%d %b %Y")
    cv2.putText(frame, time_str, (w-165,28), font, 0.65, white, 1)
    cv2.putText(frame, date_str, (w-165,48), mono, 1.2, dim, 1)

    # OS label
    cv2.putText(frame, f"SYS: {OS.upper()}", (280,35), mono, 1.1, teal, 1)

    # ── Bottom bar ────────────────────────────────────────────────────────────
    cv2.line(frame, (0, h-70), (w, h-70), cyan, 1)

    with text_lock:
        msg = jarvis_text[:58]

    # Blinking cursor effect
    blink = int(time.time() * 2) % 2 == 0
    if blink:
        msg += "█"

    # Main output text
    cv2.putText(frame, msg, (16, h-40), font, 0.65, cyan, 2)
    cv2.putText(frame, msg, (15, h-41), font, 0.65, white, 1)

    # Status indicator
    global listening_flag
    with text_lock:
        lf = listening_flag
    status_color = (0, 255, 80) if lf else (0, 120, 255)
    status_label = "● LISTENING" if lf else "● STANDBY"
    cv2.putText(frame, status_label, (16, h-15), mono, 1.1, status_color, 1)

    # Battery (if available)
    if PSUTIL_AVAILABLE:
        bat = psutil.sensors_battery()
        if bat:
            pct = int(bat.percent)
            plug = "⚡" if bat.power_plugged else "🔋"
            bat_str = f"BAT: {pct}%"
            cv2.putText(frame, bat_str, (w-130, h-15), mono, 1.1, teal, 1)

    # Corner decorations
    bracket_len = 18
    thickness = 2
    corners = [(15,65),(w-15,65),(15,h-80),(w-15,h-80)]
    for (cx,cy) in corners:
        dx = -1 if cx > w//2 else 1
        dy = -1 if cy > h//2 else 1
        cv2.line(frame,(cx,cy),(cx+dx*bracket_len,cy),cyan,thickness)
        cv2.line(frame,(cx,cy),(cx,cy+dy*bracket_len),cyan,thickness)

    return frame


def run_jarvis_ui():
    global jarvis_text, exit_flag, listening_flag

    if not CV2_AVAILABLE:
        print("[UI] Console-only mode. Install opencv-python for the HUD.")
        while not exit_flag:
            time.sleep(0.5)
        return

    gif_path = "jarvis.gif"
    alt_paths = ["ironman.gif", os.path.join(os.path.dirname(__file__), "jarvis.gif")]

    cap = None
    for gp in [gif_path] + alt_paths:
        if os.path.exists(gp):
            cap = cv2.VideoCapture(gp)
            if cap.isOpened():
                print(f"[UI] Loaded GIF: {gp}")
                break
            cap = None

    if cap is None:
        print("[UI] GIF not found — using animated dark background.")

    WIN_W, WIN_H = 820, 540

    cv2.namedWindow("J.A.R.V.I.S", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("J.A.R.V.I.S", WIN_W, WIN_H)

    # Try to set a dark title bar (Windows only)
    try:
        import ctypes
        hwnd = int(cv2.getWindowProperty("J.A.R.V.I.S", cv2.WND_PROP_FULLSCREEN))
        # dark mode DWMWA flag
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4)
    except Exception:
        pass

    frame_delay = 33   # ~30 fps

    while not exit_flag:
        if cap and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            frame = cv2.resize(frame, (WIN_W, WIN_H))
        else:
            # Animated fallback: gradient + scan-line
            frame = np.zeros((WIN_H, WIN_W, 3), dtype=np.uint8)
            t = time.time()
            for y in range(WIN_H):
                val = int(15 + 10 * abs((y - WIN_H//2) / WIN_H))
                frame[y, :] = [val, val//2, 0]
            # Scan-line
            sl = int((t * 120) % WIN_H)
            cv2.line(frame, (0, sl), (WIN_W, sl), (0, 60, 60), 1)

        frame = draw_hud_overlay(frame)

        cv2.imshow("J.A.R.V.I.S", frame)

        key = cv2.waitKey(frame_delay) & 0xFF
        if key == ord('q') or key == 27:   # q or ESC
            exit_flag = True
            break

    if cap:
        cap.release()
    cv2.destroyAllWindows()


# ══════════════════════════════════════════════════════════════════════════════
#  JOKES
# ══════════════════════════════════════════════════════════════════════════════
JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the computer go to the doctor? It had a virus!",
    "I told my computer I needed a break. Now it won't stop sending me Kit Kat ads.",
    "Why was the math book sad? It had too many problems.",
    "What do you call a computer that sings? A Dell!",
    "How do you comfort a JavaScript bug? You console it.",
    "Why do Java developers wear glasses? Because they don't C sharp.",
    "A SQL query walks into a bar, walks up to two tables and asks: Can I join you?",
    "Why did the developer go broke? Because he used up all his cache.",
]


# ══════════════════════════════════════════════════════════════════════════════
#  COMMAND HANDLER
# ══════════════════════════════════════════════════════════════════════════════
def handle_command(command: str) -> bool:
    global jarvis_text, exit_flag

    def set_display(txt):
        with text_lock:
            jarvis_text = txt.upper()[:60]

    # ── PLAY YOUTUBE ──────────────────────────────────────────────────────────
    if command.startswith("play "):
        song = command[5:].strip()
        if song:
            set_display(f"PLAYING: {song}")
            threading.Thread(target=play_on_youtube, args=(song,), daemon=True).start()
        else:
            speak("What would you like me to play?")

    # ── CLOSE / STOP APP ──────────────────────────────────────────────────────
    elif any(w in command for w in ("close ", "stop ", "kill ", "terminate ")):
        target = (command.replace("close ","").replace("stop ","")
                         .replace("kill ","").replace("terminate ","")).strip()
        if target:
            set_display(f"CLOSING: {target}")
            speak(f"Closing {target}")
            if not close_app(target):
                speak(f"Could not find a running process for {target}.")
        else:
            speak("What application should I close?")

    # ── WIKIPEDIA / WEB KNOWLEDGE ─────────────────────────────────────────────
    elif command.startswith("who is ") or command.startswith("what is "):
        query = command.replace("who is ","").replace("what is ","").strip()
        if not query:
            speak("Please specify what you want to know about."); return True
        set_display(f"SEARCHING: {query}")
        speak("Checking my database...")
        if WIKIPEDIA_AVAILABLE:
            try:
                result = wikipedia.summary(query, sentences=2, auto_suggest=False)
                speak(result)
            except wikipedia.exceptions.DisambiguationError:
                speak("Multiple results found. Please be more specific.")
            except wikipedia.exceptions.PageError:
                speak(f"No Wikipedia page found for {query}.")
            except Exception as e:
                print(f"[Wikipedia] {e}")
                speak("I couldn't retrieve that information.")
        else:
            speak("Wikipedia module is not installed. Run: pip install wikipedia")

    # ── TIME ──────────────────────────────────────────────────────────────────
    elif "time" in command:
        t = datetime.datetime.now().strftime("%I:%M %p")
        set_display(f"TIME: {t}")
        speak(f"The current time is {t}")

    # ── DATE ──────────────────────────────────────────────────────────────────
    elif "date" in command:
        d = datetime.datetime.now().strftime("%A, %B %d, %Y")
        set_display(f"DATE: {d}")
        speak(f"Today is {d}")

    # ── BATTERY ───────────────────────────────────────────────────────────────
    elif "battery" in command:
        b = get_battery()
        if b:
            pct = int(b.percent)
            plug = "charging" if b.power_plugged else "not charging"
            set_display(f"BATTERY: {pct}% - {plug}")
            speak(f"Battery is at {pct} percent and is {plug}.")
        else:
            speak("Battery information is unavailable." if PSUTIL_AVAILABLE
                  else "psutil not installed. Run: pip install psutil")

    # ── CPU / RAM ─────────────────────────────────────────────────────────────
    elif "cpu" in command or "ram" in command or "memory" in command:
        cpu, ram = get_cpu_ram()
        if cpu is not None:
            set_display(f"CPU: {cpu}%  RAM: {ram}%")
            speak(f"CPU usage is {cpu} percent. RAM usage is {ram} percent.")
        else:
            speak("System stats unavailable. Install psutil.")

    # ── IP ADDRESS ────────────────────────────────────────────────────────────
    elif "ip" in command or "ip address" in command:
        ip = get_ip()
        set_display(f"IP: {ip}")
        speak(f"Your IP address is {ip}")

    # ── SCREENSHOT ────────────────────────────────────────────────────────────
    elif "screenshot" in command:
        fn = take_screenshot()
        if fn:
            set_display(f"SCREENSHOT: {fn}")
            speak(f"Screenshot saved as {fn}")
        else:
            speak("pyautogui not installed. Run: pip install pyautogui")

    # ── SYSTEM INFO ───────────────────────────────────────────────────────────
    elif "system info" in command or "system information" in command:
        set_display(f"SYSTEM: {OS}")
        speak(f"Running {OS} with Python {sys.version.split()[0]}.")

    # ── SHUTDOWN ──────────────────────────────────────────────────────────────
    elif "shutdown" in command or "shut down" in command or "power off" in command:
        set_display("SHUTDOWN INITIATED")
        exit_flag = True
        system_shutdown()
        return False

    # ── RESTART ───────────────────────────────────────────────────────────────
    elif "restart" in command or "reboot" in command:
        set_display("RESTARTING...")
        exit_flag = True
        system_restart()
        return False

    # ── SLEEP ─────────────────────────────────────────────────────────────────
    elif "sleep" in command and "mode" not in command:
        system_sleep()

    # ── LOCK ──────────────────────────────────────────────────────────────────
    elif "lock" in command and ("screen" in command or "computer" in command or "pc" in command):
        lock_screen()

    # ── VOLUME ───────────────────────────────────────────────────────────────
    elif "volume up" in command or "increase volume" in command:
        if OS == "Windows":
            try:
                import ctypes
                wshell = __import__("win32com.client", fromlist=["Dispatch"]).Dispatch("WScript.Shell")
                for _ in range(5): wshell.SendKeys(chr(0xAF))   # VK_VOLUME_UP
                speak("Volume increased.")
            except Exception:
                speak("Volume control unavailable. Install pywin32.")
        else:
            speak("Volume control is Windows-only in this version.")

    elif "volume down" in command or "decrease volume" in command:
        if OS == "Windows":
            try:
                import ctypes
                wshell = __import__("win32com.client", fromlist=["Dispatch"]).Dispatch("WScript.Shell")
                for _ in range(5): wshell.SendKeys(chr(0xAE))   # VK_VOLUME_DOWN
                speak("Volume decreased.")
            except Exception:
                speak("Volume control unavailable. Install pywin32.")
        else:
            speak("Volume control is Windows-only in this version.")

    elif "mute" in command:
        if OS == "Windows":
            try:
                wshell = __import__("win32com.client", fromlist=["Dispatch"]).Dispatch("WScript.Shell")
                wshell.SendKeys(chr(0xAD))
                speak("Muted.")
            except Exception:
                speak("Mute unavailable. Install pywin32.")
        else:
            speak("Mute is Windows-only in this version.")

    # ── GOOGLE SEARCH ─────────────────────────────────────────────────────────
    elif "search" in command or command.startswith("google "):
        q = command.replace("search","").replace("google","").strip()
        if q:
            set_display(f"SEARCHING: {q}")
            speak(f"Searching Google for {q}")
            webbrowser.open(f"https://www.google.com/search?q={q.replace(' ','+')}")
        else:
            speak("What should I search for?")

    # ── OPEN (generic) ────────────────────────────────────────────────────────
    elif command.startswith("open "):
        target = command[5:].strip()
        if not target:
            speak("What should I open?"); return True
        set_display(f"OPENING: {target}")
        speak(f"Opening {target}")
        success, method = smart_open(target)
        if not success:
            speak(f"I could not find or open {target}.")

    # ── SPECIFIC NAMED APPS (direct shortcuts for clarity) ───────────────────
    elif "calculator" in command or "calc" in command:
        set_display("OPENING CALCULATOR")
        speak("Opening Calculator")
        if not open_native_app("calculator"):
            webbrowser.open("https://www.google.com/search?q=calculator")

    elif "notepad" in command:
        set_display("OPENING NOTEPAD"); speak("Opening Notepad"); open_native_app("notepad")

    elif "vs code" in command or "vscode" in command:
        set_display("OPENING VS CODE"); speak("Opening Visual Studio Code"); open_native_app("vs code")

    elif "spotify" in command:
        set_display("OPENING SPOTIFY"); speak("Opening Spotify")
        if not open_native_app("spotify"):
            webbrowser.open("https://open.spotify.com")

    elif "discord" in command:
        set_display("OPENING DISCORD"); speak("Opening Discord")
        if not open_native_app("discord"):
            webbrowser.open("https://discord.com/app")

    elif "whatsapp" in command:
        set_display("OPENING WHATSAPP"); speak("Opening WhatsApp")
        if not open_native_app("whatsapp"):
            webbrowser.open("https://web.whatsapp.com")

    elif "chrome" in command:
        set_display("OPENING CHROME"); speak("Opening Chrome"); open_native_app("chrome")

    elif "firefox" in command:
        set_display("OPENING FIREFOX"); speak("Opening Firefox"); open_native_app("firefox")

    elif "word" in command:
        set_display("OPENING WORD"); speak("Opening Microsoft Word"); open_native_app("word")

    elif "excel" in command:
        set_display("OPENING EXCEL"); speak("Opening Microsoft Excel"); open_native_app("excel")

    elif "powerpoint" in command:
        set_display("OPENING POWERPOINT"); speak("Opening PowerPoint"); open_native_app("powerpoint")

    elif "teams" in command:
        set_display("OPENING TEAMS"); speak("Opening Microsoft Teams"); open_native_app("teams")

    elif "steam" in command:
        set_display("OPENING STEAM"); speak("Opening Steam"); open_native_app("steam")

    elif "telegram" in command:
        set_display("OPENING TELEGRAM"); speak("Opening Telegram"); open_native_app("telegram")

    elif "task manager" in command:
        set_display("OPENING TASK MANAGER"); speak("Opening Task Manager"); open_native_app("task manager")

    elif "file explorer" in command or "explorer" in command:
        set_display("OPENING FILE EXPLORER"); speak("Opening File Explorer"); open_native_app("file explorer")

    elif "paint" in command:
        set_display("OPENING PAINT"); speak("Opening Paint"); open_native_app("paint")

    elif "command prompt" in command or "cmd" in command:
        set_display("OPENING CMD"); speak("Opening Command Prompt"); open_native_app("cmd")

    elif "powershell" in command:
        set_display("OPENING POWERSHELL"); speak("Opening PowerShell"); open_native_app("powershell")

    # ── JOKES ─────────────────────────────────────────────────────────────────
    elif "joke" in command:
        joke = random.choice(JOKES)
        set_display("TELLING JOKE...")
        speak(joke)

    # ── GREETINGS ─────────────────────────────────────────────────────────────
    elif any(w in command for w in ("hello","hi","hey","good morning","good evening","good afternoon")):
        hour = datetime.datetime.now().hour
        if hour < 12:   g = "Good morning! Systems are fully operational. How can I assist?"
        elif hour < 17: g = "Good afternoon! All systems nominal. What do you need?"
        else:           g = "Good evening! Ready and at your service."
        set_display("HELLO!")
        speak(g)

    # ── HOW ARE YOU ───────────────────────────────────────────────────────────
    elif "how are you" in command:
        set_display("STATUS: OPTIMAL")
        speak("All systems are running at optimal efficiency. Thank you for asking, sir.")

    # ── WHAT CAN YOU DO ───────────────────────────────────────────────────────
    elif "what can you do" in command or "help" in command:
        set_display("CAPABILITIES LIST")
        speak("I can open and close applications, search the web, play YouTube videos, "
              "check battery and system stats, take screenshots, tell jokes, "
              "get the time and date, lock your screen, and much more. Just ask.")

    # ── EXIT JARVIS ───────────────────────────────────────────────────────────
    elif any(w in command for w in ("bye","exit","quit","goodbye","jarvis off","power down","stop jarvis")):
        set_display("POWERING OFF...")
        speak("Shutting down J.A.R.V.I.S. It was a pleasure, sir. Goodbye.")
        exit_flag = True
        return False

    # ── UNKNOWN ───────────────────────────────────────────────────────────────
    else:
        set_display("UNKNOWN COMMAND")
        speak(f"I heard: {command}. I am not programmed to handle that yet.")

    return True


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════════════════════════════════════
def start_jarvis_brain():
    global jarvis_text, exit_flag, listening_flag

    with text_lock:
        jarvis_text = "INITIALIZING..."
    speak("J.A.R.V.I.S. Version 3.0 activated. All systems online and ready, sir.")

    r = sr.Recognizer()
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True

    while not exit_flag:
        try:
            with sr.Microphone() as source:
                with text_lock:
                    jarvis_text = "LISTENING..."
                    listening_flag = True
                print("\n[JARVIS] Listening...")
                r.adjust_for_ambient_noise(source, duration=0.4)
                try:
                    audio = r.listen(source, timeout=8, phrase_time_limit=10)
                except sr.WaitTimeoutError:
                    with text_lock:
                        listening_flag = False
                    continue

                with text_lock:
                    jarvis_text = "PROCESSING..."
                    listening_flag = False
                print("[JARVIS] Processing...")

                try:
                    command = r.recognize_google(audio).lower().strip()
                    print(f"[JARVIS] Recognized: '{command}'")
                except sr.UnknownValueError:
                    print("[JARVIS] Could not understand audio.")
                    continue
                except sr.RequestError as e:
                    print(f"[Google API] {e}")
                    speak("Speech service unavailable. Please check your internet connection.")
                    continue

        except OSError as e:
            print(f"[Microphone error] {e}")
            speak("Microphone not detected. Please connect a microphone and restart.")
            break
        except Exception as e:
            print(f"[Unexpected error] {e}")
            continue

        if not command:
            continue

        # Strip wake word
        for wake in ("hey jarvis", "jarvis"):
            if command.startswith(wake):
                command = command[len(wake):].strip()
                break

        if not command:
            speak("Yes? I'm listening.")
            continue

        print(f"[JARVIS] Command: '{command}'")
        if not handle_command(command):
            break


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # ── Print startup banner ──────────────────────────────────────────────────
    print("""
╔══════════════════════════════════════════════════════════════╗
║         J.A.R.V.I.S  — Voice AI Assistant v3.0              ║
║         Final Year Project                                   ║
╠══════════════════════════════════════════════════════════════╣
║  COMMANDS:  "Hey Jarvis, open chrome"                        ║
║             "Play Believer"                                  ║
║             "What is Python"                                 ║
║             "Close spotify"                                  ║
║             "Battery status" / "CPU status"                  ║
║             "Take screenshot" / "Lock screen"                ║
║             "Shutdown" / "Restart" / "Sleep"                 ║
║             "Tell me a joke" / "What time is it"             ║
║             "Bye" / "Exit" — quit JARVIS                     ║
║                                                              ║
║  REQUIRED:  jarvis.gif  in the same folder                   ║
║  PRESS Q or ESC in the window to quit                        ║
╚══════════════════════════════════════════════════════════════╝
""")

    # ── Start UI on background thread ─────────────────────────────────────────
    ui_thread = threading.Thread(target=run_jarvis_ui, daemon=True)
    ui_thread.start()

    # Give the UI a moment to open before speaking
    time.sleep(1.2)

    # ── Start brain on main thread ────────────────────────────────────────────
    try:
        start_jarvis_brain()
    except KeyboardInterrupt:
        print("\n[JARVIS] Interrupted by user.")
    finally:
        exit_flag = True
        ui_thread.join(timeout=3)
        print("[JARVIS] Shut down cleanly.")
