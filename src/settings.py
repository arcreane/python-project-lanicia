# src/settings.py

# --- COULEURS ---
BG_DARK = "#2b2b2b"
FG_LIGHT = "#f0f0f0"
ACCENT_GREEN = "#00ff00"
ACCENT_RED = "#ff4444"
ACCENT_ORANGE = "#ffaa00"
ACCENT_YELLOW = "#ffff00"
ACCENT_BLUE = "#007acc"
ACCENT_PURPLE = "#880088"

# --- DIMENSIONS ---
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 900
RADAR_WIDTH = 1000
RADAR_HEIGHT = 1000
MODEL_CENTER = 500

# --- CONFIG NIVEAUX ---
LEVELS = {
    1: {"total": 5, "rate": 8.0, "score_min": 300},
    2: {"total": 8, "rate": 7.0, "score_min": 1000},
    3: {"total": 12, "rate": 6.0, "score_min": 2000},
    4: {"total": 15, "rate": 5.0, "score_min": 3500},
    5: {"total": 20, "rate": 4.0, "score_min": 6000}
}

# --- STYLES CSS DES BOUTONS ---
BTN_BASE = "QPushButton {background-color: #404040; color: white; border: 1px solid #666; border-radius: 6px; font-size: 13px; font-weight: bold; padding: 8px; min-height: 25px;} QPushButton:hover {background-color: #505050;} QPushButton:pressed {background-color: #2a2a2a; padding-top: 10px;}"
BTN_BLUE = f"QPushButton {{background-color: {ACCENT_BLUE}; color: white; border-radius: 6px; font-size: 14px; font-weight: bold; padding: 8px; min-height: 25px;}} QPushButton:hover {{background-color: #008be6;}} QPushButton:pressed {{padding-top: 10px;}}"
BTN_GREEN = "QPushButton {background-color: #00AA00; color: white; border: 2px solid #00FF00; border-radius: 8px; font-size: 16px; font-weight: bold; padding: 10px;} QPushButton:hover {background-color: #00CC00;} QPushButton:pressed {padding-top: 12px;}"
BTN_RED = "QPushButton {background-color: #AA0000; color: white; border: 2px solid #FF0000; border-radius: 8px; font-size: 14px; font-weight: bold; padding: 8px;} QPushButton:pressed {padding-top: 10px;}"
BTN_PURPLE = f"QPushButton {{background-color: {ACCENT_PURPLE}; color: white; border: 1px solid #aa00aa; border-radius: 6px; font-size: 14px; font-weight: bold; padding: 8px;}} QPushButton:hover {{background-color: #aa00aa;}} QPushButton:pressed {{padding-top: 10px;}}"
BTN_DISABLED = "QPushButton {background-color: #333; color: #777; border: 2px solid #444; border-radius: 8px; font-size: 12px; font-weight: bold; padding: 5px;}"