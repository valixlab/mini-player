import webview
import subprocess
import threading
import os
import json
import time

try:
    with open(f"{os.getcwd()}/settings.json","r",encoding="utf-8") as f:
        settings = json.load(f)
except Exception:
    settings={"x":0,"y":0,"color":"#1DB954"}

print(settings)

def save():
    global window
    with open(f"{os.getcwd()}/settings.json", "w") as fichier:
            json.dump({"x":window.x, "y":window.y, "color":settings["color"], "auto":settings["auto"]}, fichier)

def run_playerctl(args, timeout=1):
    try:
        return subprocess.run(["playerctl"] + args,capture_output=True, text=True, timeout=timeout).stdout.strip()
    except Exception:
        return ""

def get_metadata():
    titre = run_playerctl(["metadata", "--format", "{{ title }}"])
    artiste = run_playerctl(["metadata", "--format", "{{ artist }}"])
    pochette = run_playerctl(["metadata", "--format", "{{ mpris:artUrl }}"])
    position = run_playerctl(["position"])
    duree = run_playerctl(["metadata", "--format", "{{ mpris:length }}"])
    status = run_playerctl(["status"])
    color = settings["color"]
    auto = settings["auto"]
    return {
        "titre": titre, "artiste": artiste,
        "pochette": pochette, "position": position,
        "duree": duree, "status": status,
        "color":color,"auto":auto
    }

def update_loop(window: webview.Window):
    while (True):
        data = get_metadata()
        window.evaluate_js(f"updateInfo({json.dumps(data)})")
        time.sleep(0.5)

class Api():
    def change_color(self, color):
        settings["color"] = color
        save()

    def set_auto(self, value):
        settings["auto"] = value
        save()

    def print(self, text):
        print(text)

    def play_pause(self):
        run_playerctl(["play-pause"])

    def next_track(self):
        run_playerctl(["next"])

    def previous_track(self):
        run_playerctl(["previous"])
        
    def set_volume(self, pourcentage):
        volume = float(pourcentage) / 100
        run_playerctl(["volume", str(volume)])

    def get_volume(self):
        return run_playerctl(["volume"])
    
    def close_window(self):
        save()
        window.destroy()
        os._exit(0)


if __name__ == '__main__':

    api = Api()

    with open("index.html", "r") as f:
        html = f.readlines()
    html = "".join(html)

    window = webview.create_window(
        'Mini player', 
        html=html, 
        transparent=True, 
        frameless=True, 
        on_top=True,
        width=380,
        height=88,
        min_size=(380, 88),
        x=settings["x"], y=settings["y"],
        easy_drag=False,
        js_api=api
    )

    threading.Thread(target=update_loop, args=(window,), daemon=True).start()
    webview.start()
