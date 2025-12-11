from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPixmap
from PySide6.QtCore import Qt, Signal
import math
import time
from src.settings import BG_DARK, MODEL_CENTER


class RadarWidget(QWidget):
    aircraft_clicked = Signal(str)

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: #1e1e1e;")
        self.aircrafts = []
        self.landing_zone = (0, 0, 0, 0)
        self.selected_id = None

        self.img_runway = QPixmap("assets/runway.png")
        self.plane_images = {
            "COMMERCIAL": QPixmap("assets/plane_comm.png"),
            "PRIVATE": QPixmap("assets/plane_jet.png"),
            "FIGHTER": QPixmap("assets/plane_mil.png")
        }
        self.default_plane = QPixmap("assets/plane.png")

    def update_data(self, aircrafts, landing_zone):
        self.aircrafts = aircrafts
        self.landing_zone = landing_zone
        self.update()

    def set_selected(self, ac_id):
        self.selected_id = ac_id
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        W, H = self.width(), self.height()
        CX, CY = W / 2, H / 2
        R = min(W, H) / 2 - 35

        SCALE = R / 520.0
        if SCALE <= 0: SCALE = 0.01

        # --- 1. RADAR (Fond) ---
        p.setPen(QPen(QColor(50, 50, 50), 2))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(int(CX - R), int(CY - R), int(R * 2), int(R * 2))

        p.setPen(QPen(QColor(60, 60, 60), 1, Qt.DotLine))
        for fac in [0.75, 0.50, 0.25]:
            rad_dist = int(R * fac)
            p.drawEllipse(int(CX - rad_dist), int(CY - rad_dist), int(rad_dist * 2), int(rad_dist * 2))

        # --- 2. ROSE DES VENTS ---
        cardinals = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S", 225: "SW", 270: "W", 315: "NW"}
        p.setFont(QFont("Consolas", 10, QFont.Bold))

        for angle in range(0, 360, 15):
            rad = math.radians(angle - 90)
            x_edge = CX + R * math.cos(rad)
            y_edge = CY + R * math.sin(rad)
            x_text = CX + (R + 20) * math.cos(rad)
            y_text = CY + (R + 20) * math.sin(rad)

            if angle in cardinals:
                p.setPen(QColor(0, 255, 0))
                p.drawText(int(x_text) - 10, int(y_text) + 5, cardinals[angle])
                p.drawLine(int(CX + (R - 10) * math.cos(rad)), int(CY + (R - 10) * math.sin(rad)), int(x_edge),
                           int(y_edge))
            elif angle % 30 == 0:
                p.setPen(QColor(150, 150, 150))
                p.drawText(int(x_text) - 10, int(y_text) + 5, str(angle))
                p.drawLine(int(CX + (R - 5) * math.cos(rad)), int(CY + (R - 5) * math.sin(rad)), int(x_edge),
                           int(y_edge))
            else:
                p.setPen(QColor(80, 80, 80))
                p.drawLine(int(CX + (R - 3) * math.cos(rad)), int(CY + (R - 3) * math.sin(rad)), int(x_edge),
                           int(y_edge))

        # --- 3. MONDE VIRTUEL ---
        p.save()  # SAUVEGARDE DE L'ÉTAT INITIAL (ÉCRAN)

        # Application du Zoom et du Centrage
        p.translate(CX, CY)
        p.scale(SCALE, SCALE)
        p.translate(-MODEL_CENTER, -MODEL_CENTER)

        # Dessin Piste
        lx, ly, lw, lh = self.landing_zone
        if not self.img_runway.isNull():
            p.drawPixmap(int(lx), int(ly), int(lw), int(lh), self.img_runway)
        else:
            p.setBrush(QColor(80, 80, 80))
            p.drawRect(lx, ly, lw, lh)

        # Dessin Avions
        blink = int(time.time() * 5) % 2 == 0
        for ac in self.aircrafts:
            self._draw_aircraft(p, ac, blink, SCALE)

        p.restore()  # RESTAURATION DE L'ÉTAT INITIAL (FIN DU ZOOM)

    def _draw_aircraft(self, p, ac, blink, global_scale):
        is_sel = (ac.id == self.selected_id)

        color = QColor(0, 255, 255)
        if ac.state == "CRASHED":
            color = QColor(255, 0, 0)
        elif ac.state == "OUT_OF_BOUNDS":
            color = QColor(80, 80, 80)
        elif ac.event == "MAYDAY":
            color = QColor(255, 0, 0) if blink else QColor(255, 255, 0)
        elif ac.event == "URGENCY":
            color = QColor(255, 140, 0) if blink else QColor(255, 255, 0)
        elif is_sel:
            color = QColor(255, 255, 0)

        # 1. On se déplace à la position de l'avion
        p.save()
        p.translate(ac.x, ac.y)

        # 2. Rotation pour l'image de l'avion
        p.save()
        p.rotate(ac.heading)

        sz = 45
        img = self.plane_images.get(ac.type_label, self.default_plane)

        if img and not img.isNull():
            p.drawPixmap(-sz // 2, -sz // 2, sz, sz, img)
        else:
            p.setBrush(color)
            p.drawEllipse(-10, -10, 20, 20)

        if is_sel:
            p.setPen(QPen(color, 2, Qt.DashLine))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(-sz // 2 - 5, -sz // 2 - 5, sz + 10, sz + 10)

        p.restore()  # Fin de la rotation

        # 3. Vecteur CAP (Indépendant de la rotation de l'image)
        if is_sel:
            p.setPen(QPen(color, 2))
            rad = math.radians(ac.heading - 90)
            p.drawLine(0, 0, int(80 * math.cos(rad)), int(80 * math.sin(rad)))

        # 4. Textes (On annule le zoom global pour que le texte reste lisible)
        p.scale(1 / global_scale, 1 / global_scale)
        p.setFont(QFont("Consolas", 9, QFont.Bold))

        if ac.event == "MAYDAY":
            p.setPen(QColor(255, 0, 0)); p.drawText(25, -35, "⚠️ PANNE")
        elif ac.event == "URGENCY":
            p.setPen(QColor(255, 0, 255)); p.drawText(25, -35, "✚ URGENCE")

        p.setPen(Qt.white);
        p.drawText(25, -20, ac.id)
        p.setPen(QColor(255, 100, 100) if ac.altitude < 500 else QColor(200, 200, 200))
        p.drawText(25, -5, f"A:{int(ac.altitude)}")
        p.setPen(QColor(200, 200, 200))
        p.drawText(25, 10, f"V:{int(ac.speed)}")
        if is_sel: p.setPen(Qt.yellow); p.drawText(25, 25, f"C:{int(ac.heading)}°")

        # C'ÉTAIT ICI L'ERREUR : Il y avait deux p.restore() !
        p.restore()  # Fin de la translation (Retour à l'origine du monde virtuel)

    def mousePressEvent(self, event):
        W, H = self.width(), self.height()
        CX, CY = W / 2, H / 2
        R = min(W, H) / 2 - 35
        SCALE = R / 520.0
        if SCALE <= 0: SCALE = 0.01

        mx = (event.position().x() - CX) / SCALE + MODEL_CENTER
        my = (event.position().y() - CY) / SCALE + MODEL_CENTER

        clicked = False
        for ac in self.aircrafts:
            if abs(ac.x - mx) < 60 and abs(ac.y - my) < 60:
                self.selected_id = ac.id
                self.aircraft_clicked.emit(ac.id)
                self.update()
                clicked = True
                break

        if not clicked:
            self.selected_id = None
            self.aircraft_clicked.emit("")
            self.update()