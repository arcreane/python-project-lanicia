from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QGridLayout, QLabel, QListWidget, QListWidgetItem, QFrame
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt, Signal
from src.settings import *


class StatusPanel(QWidget):
    selection_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(300)
        self.layout = QVBoxLayout(self)

        # --- STYLE DES BOITES (DIGITAL LOOK) ---
        # Fond très sombre, bordure grise, texte centré
        base_style = """
            background-color: #151515;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 2px;
            font-weight: bold;
            qproperty-alignment: AlignCenter;
        """

        # --- GROUPE PROGRESSION ---
        gb = QGroupBox("PROGRESSION")
        gb.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #f0f0f0;
                left: 10px;
            }
        """)

        gl = QGridLayout(gb)
        gl.setVerticalSpacing(8)

        # --- 1. Indicateurs Haut (Niveau, Temps...) ---

        # Niveau (Jaune)
        self.lbl_lvl = QLabel("1")
        self.lbl_lvl.setStyleSheet(base_style + f"color: {ACCENT_YELLOW}; font-size: 16px;")

        # Temps (Cyan)
        self.lbl_tmr = QLabel("WAIT")
        self.lbl_tmr.setStyleSheet(base_style + "color: cyan;")

        # Reste (Blanc)
        self.lbl_rem = QLabel("0")
        self.lbl_rem.setStyleSheet(base_style + "color: white;")

        # Objectif (Gris clair)
        self.lbl_obj = QLabel("0")
        self.lbl_obj.setStyleSheet(base_style + "color: #ccc;")

        gl.addWidget(QLabel("⭐ NIVEAU:"), 0, 0)
        gl.addWidget(self.lbl_lvl, 0, 1)

        gl.addWidget(QLabel("⏱️ Spawn:"), 1, 0)
        gl.addWidget(self.lbl_tmr, 1, 1)

        gl.addWidget(QLabel("✈️ Reste:"), 2, 0)
        gl.addWidget(self.lbl_rem, 2, 1)

        gl.addWidget(QLabel("🎯 But:"), 3, 0)
        gl.addWidget(self.lbl_obj, 3, 1)

        # --- SÉPARATEUR ---
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #444; margin-top: 5px; margin-bottom: 5px;")
        gl.addWidget(line, 4, 0, 1, 2)

        # --- 2. Indicateurs Bas (Stats) ---

        # Posés (Vert)
        self.lbl_s_land = QLabel("0")
        self.lbl_s_land.setStyleSheet(base_style + f"color: {ACCENT_GREEN}; font-size: 14px;")

        # Crashs (Rouge)
        self.lbl_s_crash = QLabel("0")
        self.lbl_s_crash.setStyleSheet(base_style + f"color: {ACCENT_RED}; font-size: 14px;")

        # Score (Orange et Gros)
        self.lbl_score = QLabel("0")
        self.lbl_score.setStyleSheet(base_style + f"color: {ACCENT_ORANGE}; font-size: 18px;")

        gl.addWidget(QLabel("✅ Posés:"), 5, 0)
        gl.addWidget(self.lbl_s_land, 5, 1)

        gl.addWidget(QLabel("💥 Crashs:"), 6, 0)
        gl.addWidget(self.lbl_s_crash, 6, 1)

        gl.addWidget(QLabel("🏆 SCORE:"), 7, 0)
        gl.addWidget(self.lbl_score, 7, 1)

        self.layout.addWidget(gb)

        # --- GROUPE RADAR ---
        gb2 = QGroupBox("RADAR")
        gb2.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        v = QVBoxLayout(gb2)
        self.lst = QListWidget()
        self.lst.setStyleSheet("background-color: #1e1e1e; border: 1px solid #444; font-size: 12px;")
        self.lst.itemClicked.connect(self._on_item_click)
        v.addWidget(self.lst)
        self.layout.addWidget(gb2)

    def _on_item_click(self, item):
        uid = item.text().split(' ')[0]
        self.selection_changed.emit(uid)

    def highlight_aircraft(self, uid):
        if not uid:
            self.lst.clearSelection()
            return
        items = self.lst.findItems(uid, Qt.MatchFlag.MatchStartsWith)
        if items:
            self.lst.setCurrentItem(items[0])
        else:
            self.lst.clearSelection()

    def update_stats(self, score, stats, info, aircrafts):
        self.lbl_lvl.setText(str(info["current"]))
        self.lbl_tmr.setText(f"{info['next']}s" if info['next'] > 0 else "---")
        rem = info["total"] - info["spawned"]
        self.lbl_rem.setText(str(rem) if rem > 0 else "Fin")
        self.lbl_obj.setText(f"> {info['min']}")
        self.lbl_score.setText(str(score))
        self.lbl_s_land.setText(str(stats["landed"]))
        self.lbl_s_crash.setText(str(stats["crashed"]))

        # Mise à jour liste
        current_sel = self.lst.currentItem().text().split(' ')[0] if self.lst.currentItem() else None
        self.lst.clear()

        for ac in aircrafts:
            st = {"OUT_OF_BOUNDS": "SORTI", "CRASHED": "CRASH", "LANDED": "SOL", "LANDING": "APP",
                  "HOLDING": "HOLD"}.get(ac.state, "")
            evt = "[PANNE]" if ac.event == "MAYDAY" else ("[URG]" if ac.event == "URGENCY" else "")

            item_txt = f"{ac.id} | V:{int(ac.speed)} A:{int(ac.altitude)} F:{int(ac.fuel)}% {st} {evt}"
            it = QListWidgetItem(item_txt)

            if ac.state == "CRASHED":
                it.setForeground(QColor(ACCENT_RED))
            elif ac.event == "MAYDAY":
                it.setForeground(QColor(ACCENT_ORANGE))
            elif ac.state == "HOLDING":
                it.setForeground(QColor(ACCENT_PURPLE))

            self.lst.addItem(it)
            if current_sel and ac.id == current_sel:
                self.lst.setCurrentItem(it)