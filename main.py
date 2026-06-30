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
    return {
        "titre": titre, "artiste": artiste,
        "pochette": pochette, "position": position,
        "duree": duree, "status": status,
        "color":color
    }

def update_loop(window: webview.Window):
    while (True):
        data = get_metadata()
        window.evaluate_js(f"updateInfo({json.dumps(data)})")
        time.sleep(0.5)

class Api():
    def change_color(self, color):
        global window
        settings["color"] = color
        with open(f"{os.getcwd()}/settings.json", "w") as fichier:
            json.dump({"x":window.x, "y":window.y, "color":settings["color"]}, fichier)

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
        global window
        with open(f"{os.getcwd()}/settings.json", "w") as fichier:
            json.dump({"x":window.x, "y":window.y, "color":settings["color"]}, fichier)
        window.destroy()
        os._exit(0)


if __name__ == '__main__':

    api = Api()

    html = """
        <!DOCTYPE html>
        <html>
            <head>
                <link rel="preconnect" href="https://fonts.googleapis.com">
                <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                <link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap" rel="stylesheet">
                <meta charset="utf-8">
                <title>Mini player</title>
                <style>
                    :root {
                        --color: #1DB954;
                        --c-rgb: 29, 185, 84;
                    }
                    * { box-sizing: border-box;}
                    html, body {
                        width: 100%;
                        height: 100%;
                        margin: 0;
                        padding: 0;
                        overflow: hidden;

                    }
                    html {
                        margin: 0;
                        padding: 0;
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        border-radius: 20px;
                    }
                    body {
                        margin: 0;
                        position: relative;
                        background: linear-gradient(0deg, #131418, #27282B);
                    }
                    @property --pos {
                        syntax: '<percentage>';
                        initial-value: 0%;
                        inherits: false;
                    }

                    #ray {
                        border-radius: 20px;
                        height: 100%;
                        background: linear-gradient(60deg,
                            rgba(255,255,255,0) calc(var(--pos) - 20%),
                            rgba(var(--c-rgb), 0.4) var(--pos),
                            rgba(255,255,255,0) calc(var(--pos) + 20%)
                        );
                        animation: movePos 6s linear infinite;
                    }

                    @keyframes movePos {
                        0% { --pos: 200%; }
                        100%   { --pos: -20%; }
                    }
                    #close-container {
                        position: absolute;
                        left: 344px;
                        top: 8px;
                        width: 24px;
                        height: 24px;
                        background: rgb(255,255,255,0.07);
                        border-radius:100%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        transition: background 300ms;
                    }
                    #close-container:hover {
                        background: rgb(255,255,255,0.15);
                        cursor: pointer;
                    }
                    #close {
                        --1m973uw: rgb(255,255,255,0.72);
                        position: relative;
                        width: 13px;
                        height: 13px;
                        transition: transform 300ms;
                    }
                    #close-container:hover #close {
                        transform: scale(120%);
                        cursor: pointer;
                    }
                    #close-container:active #close {
                        transform: scale(80%);
                    }
                    #sett-container {
                        position: absolute;
                        left: 315px;
                        top: 8px;
                        width: 24px;
                        height: 24px;
                        background: rgb(255,255,255,0.07);
                        border-radius:100%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        transition: background 300ms;
                    }
                    #sett-container:hover {
                        background: rgb(255,255,255,0.15);
                        cursor: pointer;
                    }
                    #sett {
                        position: relative;
                        width: 13px;
                        height: 13px;
                        transition: transform 300ms;
                    }
                    #sett-container:hover #sett{
                        transform: scale(120%);
                        cursor: pointer;
                    }
                    #sett-container:active #sett {
                        transform: scale(80%);
                    }
                    #popup-color {
                        position: absolute;
                        width : 150px;
                        height : 30px;
                        z-index: 1;
                        left : 220px;
                        top : 45px;
                        background: linear-gradient(0deg, #131418, #27282B);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        border-radius: 20px;
                        display: flex;
                        flex-direction: row;
                        justify-content: center;
                        align-items: center;

                        opacity: 0;
                        visibility: hidden;
                        transform: translateY(-15px);
                        transition: opacity 250ms ease, transform 250ms ease, visibility 250ms;
                        pointer-events: none;
                    }
                    #popup-color.visible {
                        opacity: 1;
                        visibility: visible;
                        transform: translateY(0);
                        pointer-events: auto;
                    }
                    #popup-color-circle {
                        position: absolute;
                        fill: #27282B;
                        left: 317px;
                        top: 35px;
                        opacity: 0;
                        visibility: hidden;
                        transition: opacity 250ms ease, visibility 250ms;
                    }
                    #popup-color-circle.visible {
                        opacity: 1;
                        visibility: visible;
                    }
                    #popup-color-circle circle {
                        stroke : rgba(255, 255, 255, 0.1);
                        stroke-width: 1px;
                    }
                    #input-color {
                        margin-left: 5px;
                        margin-right : 5px;
                        width : 30px;
                        height: 30px;
                        border: none;
                        -webkit-appearance: none;
                        -moz-appearance: none;
                        appearance: none;
                        background-color: transparent;
                        transition : transform 300ms;
                    }
                    #input-color:hover {
                        transform: scale(110%);
                    }
                    #color-text {
                        text-align: center;
                        font-family : "Inter", sans-serif;
                        font-weight: 600;
                        font-size: 12px;
                        color: white;
                        width: 80px;
                        height: 20px;
                        background: linear-gradient(90deg, #131418, #27282B);
                        border: 1px solid rgb(255,255,255,0.1);
                        border-radius: 15px;
                    }
                    #color-text-container2 {
                        width: 80px;
                        height: 20px;
                        border-radius: 15px;
                        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.4),-2px -2px 5px rgba(255, 255, 255, 0.1);
                    }
                    #color-text-container {
                        margin-right : 5px;
                        border-radius: 15px;
                        width: 80px;
                        height: 20px;
                        display: flex;
                        align-items: center;
                        transition: transform 300ms;
                    }
                    #color-text-container:hover {
                        transform: scale(110%);
                    }
                    #miniplayer {
                        display: flex;
                        flex-direction: row;
                        padding : 12px;
                    }
                    #info {
                        margin-left: 12px;
                        display: flex;
                        flex-direction: column;
                    }
                    #pochette {
                        position: relative;
                        display: block;
                        width: 64px;
                        height: 64px;
                        border-radius: 12px;
                        background: linear-gradient(146deg,rgba(232, 179, 179, 1) 0%, rgba(255, 255, 255, 1) 100%);
                        object-fit: cover;
                    }
                    #titre {
                        position: relative;
                        height: 15.4px;
                        font-family : "Inter", sans-serif;
                        font-weight: 600;
                        font-size: 14px;
                        color: rgb(255,255,255,0.96);
                    }
                    #controls {
                        display: flex;
                        flex-direction: row;
                        align-items: center;
                        gap: 8px;
                        height: 26px;
                    }
                    #artiste {
                        height: 12;
                        font-family : "Inter", sans-serif;
                        font-size: 12px;
                        color: rgb(255,255,255,0.57);

                    }
                    .btn-container {
                        width: 24px;
                        height: 24px;
                        background: rgb(255,255,255,0.07);
                        border-radius:100%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        transition: background 300ms;
                    }
                    .btn-container:hover {
                        background: rgb(255,255,255,0.15);
                        cursor: pointer;
                    }
                    .btn {
                        --1m973uw: rgb(255,255,255,0.72);
                        position: relative;
                        width: 13px;
                        height: 13px;
                        transition: transform 300ms;
                    }
                    .btn:hover {
                        transform: scale(120%);
                        cursor: pointer;
                    }
                    .btn:active {
                        transform: scale(80%);
                    }
                    #pause-container {
                        width: 24px;
                        height: 24px;
                        background: rgba(var(--c-rgb), 0.9);
                        border-radius:100%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        transition: background 300ms;
                    }
                    #pause-container:hover {
                        background: rgba(var(--c-rgb), 0.6);
                        cursor: pointer;
                    }
                    #icon-pause {
                        position: relative;
                        width: 13px;
                        height: 13px;
                        transition: transform 300ms;
                    }
                    #pause-container:hover #icon-pause {
                        transform: scale(120%);
                        cursor: pointer;
                    }
                    #icon-play {
                        position: relative;
                        width: 13px;
                        height: 13px;
                        transition: transform 300ms;
                    }
                    #pause-container:hover #icon-play {
                        transform: scale(120%);
                        cursor: pointer;
                    }
                    #volume-icon {
                        --1m973uw: rgb(255,255,255,0.48);
                        position: relative;
                        width: 14px;
                        height: 14px;
                        margin-left: 5px;
                    }
                    #volume {
                        -webkit-appearance: none;
                        appearance: none;
                        width: 60px;
                        height: 6px;
                        border-radius: 2px;
                        background: linear-gradient(to right, 
                            var(--color) 0%, 
                            var(--color) var(--val, 70%), 
                            rgb(255,255,255,0.12) var(--val, 70%), 
                            rgb(255,255,255,0.12) 100%);
                        outline: none;
                        cursor: pointer;
                    }
                    #volume::-webkit-slider-thumb {
                        -webkit-appearance: none;
                        width: 10px;
                        height: 10px;
                        border-radius: 50%;
                        background: var(--color);
                        cursor: pointer;
                    }
                    #volume::-moz-range-thumb {
                        width: 10px;
                        height: 10px;
                        border-radius: 50%;
                        background: var(--color);
                        border: none;
                        cursor: pointer;
                    }
                    #volume::-moz-range-track {
                        background: rgb(255,255,255,0.12);
                        height: 6px;
                        border-radius: 2px;
                    }
                    #volume::-moz-range-progress {
                        background: var(--color);
                        height: 6px;
                        border-radius: 2px;
                    }
                    #barre {
                        height: 6px;
                        background: rgb(255,255,255,0.12);
                        border-radius: 2px;
                        margin-top: 8px;
                        overflow: hidden;
                    }
                    #progression {
                        height: 100%;
                        background: var(--color);
                        width: 0%;
                        transition: width 0.3s linear;
                    }
                </style>
            </head>
            <body class="pywebview-drag-region">
                <div id="sett-container" onclick="color()">
                    <svg id="sett" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="15.17263" height="15.17462" viewBox="0,0,15.17263,15.17462"><g transform="translate(-232.41368,-172.41268)"><g fill="rgb(255,255,255,0.72)" stroke="none" stroke-width="0" stroke-miterlimit="10"><path d="M246.99117,175.88752l-3.31435,3.31435l0.34117,0.34117c0.07112,0.07118 0.12892,0.1506 0.1734,0.2352c0.02962,0.05642 0.05334,0.11509 0.07112,0.1752c0.01778,0.06011 0.02962,0.12155 0.03556,0.1835c0.01189,0.1239 0,0.2496 -0.03556,0.36976c-0.04443,0.15024 -0.12595,0.29182 -0.24453,0.4104c-0.02373,0.02373 -0.04832,0.04596 -0.07379,0.06672c-0.10177,0.08301 -0.21645,0.1423 -0.33661,0.17786c-0.08875,0.02629 -0.18042,0.03941 -0.2722,0.03981c-0.00149,0 -0.00297,0.00021 -0.00446,0.00021c-0.15542,0 -0.31084,-0.03705 -0.45185,-0.11114c-0.05642,-0.02967 -0.11053,-0.06523 -0.16141,-0.10674c-0.02542,-0.02075 -0.05006,-0.04299 -0.07379,-0.06672l-0.22126,-0.22126l-5.79145,5.79145c-0.07343,0.07343 -0.16105,0.13128 -0.25749,0.16992l-2.06952,0.82961c-0.16633,0.06672 -0.33979,0.10048 -0.51565,0.10048c-0.45544,0 -0.88157,-0.22793 -1.13983,-0.60973c-0.25529,-0.3774 -0.30592,-0.85651 -0.13548,-1.28172l0.82961,-2.06952c0.03859,-0.09644 0.09644,-0.18401 0.16992,-0.25749l5.79135,-5.79145l-0.22132,-0.22132c-0.07112,-0.07118 -0.12892,-0.1506 -0.1734,-0.2352c-0.04448,-0.0846 -0.07558,-0.17438 -0.09336,-0.26626c-0.01184,-0.06124 -0.01778,-0.12339 -0.01778,-0.18555c0,-0.03105 0.00149,-0.06216 0.00446,-0.09311c0.00892,-0.09285 0.03116,-0.18473 0.06672,-0.27245c0.01184,-0.02926 0.02521,-0.05806 0.04002,-0.08624c0.04448,-0.08465 0.10228,-0.16408 0.1734,-0.2352c0.1423,-0.14225 0.31775,-0.2312 0.50146,-0.26677c0.03064,-0.00589 0.06149,-0.01035 0.09244,-0.01332c0.03095,-0.00297 0.06205,-0.00446 0.09311,-0.00446c0.03105,0 0.06216,0.00149 0.09311,0.00446c0.03095,0.00297 0.0618,0.00738 0.09244,0.01332c0.18375,0.03556 0.35916,0.12447 0.50146,0.26677l0.34117,0.34117l3.3144,-3.31435c0.38447,-0.38447 0.89566,-0.5962 1.43934,-0.5962c0.54368,0 1.05487,0.21173 1.43934,0.5962c0.79364,0.79369 0.79364,2.0851 0.0001,2.87864z"/></g></g></svg>    
                </div>
                <div id="close-container" onclick="closeWindow()">
                    <svg id="close" display="block" role="presentation" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M 12 0 L 0 12" fill="transparent" height="12px" id="qMvRy61Gj" stroke-dasharray="" stroke-linecap="round" stroke-linejoin="round" stroke-width="var(--js9iwy, 2)" stroke="var(--1m973uw, rgb(0,0,0))" transform="translate(6 6)" width="12px"></path><path d="M 0 0 L 12 12" fill="transparent" height="12px" id="YX0AMSC6b" stroke-dasharray="" stroke-linecap="round" stroke-linejoin="round" stroke-width="var(--js9iwy, 2)" stroke="var(--1m973uw, rgb(0,0,0))" transform="translate(6 6)" width="12px"></path></svg>
                </div>
                <svg id="popup-color-circle" width="20" height="20" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="10" cy="10" r="10"></circle>
                </svg>
                <div id="popup-color">
                    <input type="color" id="input-color">
                    <div id="color-text-container2">
                        <div id="color-text-container">
                            <input type="text" id="color-text">
                        </div>
                    </div>
                </div>
                <div id="ray">
                    <div id="miniplayer" class="pywebview-drag-region">
                        <img src="" id="pochette">
                        <div id="info">
                            <span id="titre">--</span>
                            <div id="controls">
                                <span id="artiste">--</span>
                                <div class="btn-container no-drag"><svg class="btn" id="prev" onclick="prev()" display="block" role="presentation" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M 10.971 0.285 C 11.589 -0.086 12.359 -0.095 12.986 0.26 C 13.613 0.615 14 1.279 14 2 L 14 14 C 14 14.721 13.613 15.385 12.986 15.74 C 12.359 16.095 11.589 16.086 10.971 15.715 L 0.974 9.717 C 0.371 9.356 0.001 8.705 0 8.002 C -0.001 7.299 0.368 6.647 0.971 6.285 Z" fill="transparent" height="16.000038879233593px" id="qhguYrO07" stroke-dasharray="" stroke-linecap="round" stroke-linejoin="round" stroke-width="var(--js9iwy, 2)" stroke="var(--1m973uw, rgb(0,0,0))" transform="translate(7 4)" width="14.000202118669932px"></path><path d="M 0 16 L 0 0" fill="transparent" height="16px" id="T5Z3GygRE" stroke-dasharray="" stroke-linecap="round" stroke-linejoin="round" stroke-width="var(--js9iwy, 2)" stroke="var(--1m973uw, rgb(0,0,0))" transform="translate(3 4)" width="1px"></path></svg></div>
                                <div id="pause-container" class="no-drag" onclick="pause();">
                                    <svg id="icon-pause" class="pause-state" viewBox="0 0 24 24" width="13" height="13">
                                        <rect x='6' y='4' width='4' height='16' rx='1' fill='black'/>
                                        <rect x='14' y='4' width='4' height='16' rx='1' fill='black'/>
                                    </svg>
                                    <svg id="icon-play" class="play-state" viewBox="0 0 24 24" width="13" height="13" style="display: none;">
                                        <path d='M7 4 L19 12 L7 20 Z' fill='black' stroke='black' stroke-width='1' stroke-linejoin='round'/>
                                    </svg>
                                </div>
                                <div class="btn-container no-drag"><svg class="btn" id="skip" onclick="next()" display="block" role="presentation" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M 0 0 L 0 16" fill="transparent" height="16px" id="WDqicuhsL" stroke-dasharray="" stroke-linecap="round" stroke-linejoin="round" stroke-width="var(--js9iwy, 2)" stroke="var(--1m973uw, rgb(0,0,0))" transform="translate(21 4)" width="1px"></path><path d="M 3.029 0.285 C 2.411 -0.086 1.642 -0.095 1.015 0.26 C 0.388 0.615 0 1.279 0 2 L 0 14 C 0 14.721 0.388 15.385 1.015 15.74 C 1.642 16.095 2.411 16.086 3.029 15.715 L 13.026 9.717 C 13.63 9.356 14 8.705 14 8.002 C 14.001 7.299 13.632 6.647 13.029 6.285 Z" fill="transparent" height="16.000038879233582px" id="NuQ9n6JYX" stroke-dasharray="" stroke-linecap="round" stroke-linejoin="round" stroke-width="var(--js9iwy, 2)" stroke="var(--1m973uw, rgb(0,0,0))" transform="translate(3 4)" width="14.000202118669932px"></path></svg></div>
                                <svg id="volume-icon" display="block" role="presentation" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M 9 0.704 C 9 0.419 8.828 0.163 8.565 0.054 C 8.301 -0.055 7.999 0.005 7.797 0.206 L 4.413 3.589 C 4.149 3.854 3.79 4.003 3.416 4.002 L 1 4.002 C 0.448 4.002 0 4.45 0 5.002 L 0 11.002 C 0 11.554 0.448 12.002 1 12.002 L 3.416 12.002 C 3.79 12.001 4.149 12.15 4.413 12.415 L 7.796 15.799 C 7.998 16.001 8.301 16.062 8.565 15.952 C 8.829 15.843 9 15.585 9 15.3 Z" fill="transparent" height="16.00600250841202px" id="s0tCc1eHQ" stroke-dasharray="" stroke-linecap="round" stroke-linejoin="round" stroke-width="var(--js9iwy, 2)" stroke="var(--1m973uw, rgb(0,0,0))" transform="translate(2 3.998)" width="9.000000686837511px"></path><path d="M 0 0 C 1.333 1.778 1.333 4.222 0 6" fill="transparent" height="6px" id="LN2zp297f" stroke-dasharray="" stroke-linecap="round" stroke-linejoin="round" stroke-width="var(--js9iwy, 2)" stroke="var(--1m973uw, rgb(0,0,0))" transform="translate(16 9)" width="1px"></path><path d="M 0 12.728 C 1.688 11.04 2.636 8.751 2.636 6.364 C 2.636 3.977 1.688 1.688 0 0" fill="transparent" height="12.728px" id="BnNyTt9vh" stroke-dasharray="" stroke-linecap="round" stroke-linejoin="round" stroke-width="var(--js9iwy, 2)" stroke="var(--1m973uw, rgb(0,0,0))" transform="translate(19.364 5.636)" width="2.6360779388807742px"></path></svg>
                                <input type="range" id="volume" min="0" max="100" value="70" class="no-drag">
                            </div>
                            <div id="barre"><div id="progression"></div></div>
                        </div>
                    </div>
                </div>
            </body>
            <script>
                let can_change_icon = true;

                const miniplayer = document.getElementById('miniplayer');
                        document.querySelectorAll('.no-drag').forEach(e => { e.addEventListener('mousedown', () => miniplayer.classList.remove('pywebview-drag-region')); });

                document.addEventListener('mouseup', () => {
                    setTimeout(() => { miniplayer.classList.add('pywebview-drag-region'); }, 50);
                });

                function prev() { pywebview.api.previous_track(); }
                function pause() {
                    can_change_icon = false;
                    setTimeout(() => {
                        can_change_icon = true;
                    }, 100);
                    pywebview.api.play_pause();
                    if (document.getElementById("icon-play").style.display == "none") { document.getElementById("icon-play").style.display = "block"; document.getElementById("icon-pause").style.display = "none"; }
                    else { document.getElementById("icon-play").style.display = "none"; document.getElementById("icon-pause").style.display = "block"; }
                }
                function next() { pywebview.api.next_track(); }
                function closeWindow() { pywebview.api.close_window(); }

                const volumeSlider = document.getElementById('volume');
                function updateSliderFill(el) {
                    const percent = (el.value - el.min) / (el.max - el.min) * 100;
                    el.style.setProperty('--val', percent + '%');
                }
                volumeSlider.addEventListener('input', () => {
                    updateSliderFill(volumeSlider);
                    pywebview.api.set_volume(volumeSlider.value);
                });
                async function initVolume() {
                    const vol = await pywebview.api.get_volume();
                    volumeSlider.value = Math.round(parseFloat(vol) * 100);
                    updateSliderFill(volumeSlider);
                }
                window.addEventListener('pywebviewready', initVolume);

                function hexToRgb(hex) {
                    hex = hex.replace('#', '');
                    if (hex.length === 3) {
                        hex = hex.split('').map(c => c + c).join('');
                    }
                    const r = parseInt(hex.substring(0, 2), 16);
                    const g = parseInt(hex.substring(2, 4), 16);
                    const b = parseInt(hex.substring(4, 6), 16);
                    return `${r}, ${g}, ${b}`;
                }

                function setColor(hex) {
                    document.documentElement.style.setProperty('--color', hex);
                    document.documentElement.style.setProperty('--c-rgb', hexToRgb(hex));
                }

                function color() {
                    const popup = document.getElementById("popup-color");
                    const circle = document.getElementById("popup-color-circle");
                    popup.classList.toggle("visible");
                    circle.classList.toggle("visible");
                }

                const inputColor = document.getElementById('input-color');
                const colorText = document.getElementById('color-text');

                inputColor.addEventListener('input', () => {
                    colorText.value = inputColor.value;
                });
                colorText.addEventListener('input', () => {
                    const val = colorText.value.trim();
                    if (/^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$/.test(val)) {
                        inputColor.value = val;
                    }
                });
                colorText.addEventListener('change', () => {
                    let val = colorText.value.trim();
                    if (/^#([0-9A-Fa-f]{3})$/.test(val)) {
                        val = '#' + val.slice(1).split('').map(c => c + c).join('');
                    }
                    if (/^#([0-9A-Fa-f]{6})$/.test(val)) {
                        inputColor.value = val;
                        colorText.value = val;
                    } else {
                        colorText.value = inputColor.value;
                    }
                });

                let last_value = "";

                function updateInfo(data) {
                    
                    if (document.getElementById("color-text").value != last_value) {
                        setColor(document.getElementById("color-text").value)
                        last_value = document.getElementById("color-text").value;
                        pywebview.api.change_color(document.getElementById("color-text").value);
                    }

                    if (!document.getElementById("popup-color").classList.contains("visible")) {
                        document.getElementById("input-color").value = data.color;
                        document.getElementById("color-text").value = data.color;
                    }
                    if (data.pochette) {
                        document.getElementById("pochette").src = data.pochette;
                        document.getElementById("pochette").style.background = "rgb(0,0,0,0)";
                    } else { document.getElementById("pochette").style.background = "linear-gradient(146deg,rgba(232, 179, 179, 1) 0%, rgba(255, 255, 255, 1) 100%)";}
                    if (data.titre) document.getElementById('titre').innerText = data.titre;
                    if (data.artiste) document.getElementById('artiste').innerText = data.artiste;
                    if (can_change_icon) {
                        if (data.status == "Paused") { document.getElementById("icon-play").style.display = "block"; document.getElementById("icon-pause").style.display = "none"; }
                        else { document.getElementById("icon-play").style.display = "none"; document.getElementById("icon-pause").style.display = "block"; } 
                    }
                    const pos = parseFloat(data.position) || 0;
                    const duree = (parseFloat(data.duree) || 0) / 1000000;
                    const pct = duree > 0 ? (pos / duree) * 100 : 0;
                    if (pct>0) document.getElementById('progression').style.width = pct + '%';
                }
            </script>
        </html>
    """

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
