from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QApplication
from PySide6.QtCore import Signal
import math

from src.view.radar_widget import RadarWidget
from src.view.dialogs import LevelCompleteDialog, GameOverDialog
from src.view.panels import StatusPanel, ControlPanel
from src.settings import BG_DARK, FG_LIGHT, SCREEN_WIDTH, SCREEN_HEIGHT


class MainWindow(QMainWindow):
    # Signaux relayés au Controller
    command_signal = Signal(str, str, float)
    start_game_signal = Signal()
    next_level_signal = Signal()
    restart_game_signal = Signal()
    surrender_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("IPSA ATC Simulator 2025")
        self.resize(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setStyleSheet(f"background-color: {BG_DARK}; color: {FG_LIGHT};")

        # --- COMPOSANTS ---
        self.radar = RadarWidget()
        self.status_panel = StatusPanel()
        self.control_panel = ControlPanel()
        self.selected_id = None
        self.current_aircrafts = []

        # --- LAYOUT PRINCIPAL ---
        main = QWidget()
        self.setCentralWidget(main)
        layout = QHBoxLayout(main)

        layout.addWidget(self.status_panel)
        layout.addWidget(self.radar, 2)
        layout.addWidget(self.control_panel)

        # --- CONNEXIONS INTERNES ---
        self.radar.aircraft_clicked.connect(self.set_selection)
        self.status_panel.selection_changed.connect(self.set_selection)

        self.control_panel.start_signal.connect(self.start_game_signal.emit)
        self.control_panel.surrender_signal.connect(self.surrender_signal.emit)
        self.control_panel.command_signal.connect(self.relay_command)

    def relay_command(self, type, val):
        if self.selected_id:
            self.command_signal.emit(self.selected_id, type, val)

    def set_selection(self, uid):
        self.selected_id = uid if uid else None
        self.radar.set_selected(self.selected_id)
        self.status_panel.highlight_aircraft(self.selected_id)
        self.refresh_control_panel()

    def refresh_control_panel(self):
        """
        Calcule si l'avion sélectionné peut atterrir et pourquoi.
        """
        if not self.selected_id:
            self.control_panel.update_selection(None, [])
            return

        ac = next((a for a in self.current_aircrafts if a.id == self.selected_id), None)
        if not ac: return

        # --- LOGIQUE DE VALIDATION ATTERRISSAGE ---
        errors = []

        # 1. Calcul Cap
        dx, dy = 500 - ac.x, 900 - ac.y
        tgt_head = (math.degrees(math.atan2(dy, dx)) + 90) % 360
        diff = abs(ac.heading - tgt_head)
        if diff > 180: diff = 360 - diff

        # 2. Vérifications
        if ac.state not in ["FLYING", "HOLDING"]:
            errors.append("Etat Invalide")

        if diff >= 20:
            errors.append("Mauvais Cap")

        if ac.altitude >= 1000:
            errors.append("Trop Haut")

        if ac.speed >= 300:
            errors.append("Trop Vite")

        # On envoie l'avion ET la liste des erreurs au panneau
        self.control_panel.update_selection(ac, errors)

    def update_ui(self, score, stats, info, aircrafts):
        self.current_aircrafts = aircrafts
        self.status_panel.update_stats(score, stats, info, aircrafts)
        self.refresh_control_panel()  # Update temps réel pour voir les conditions changer

    def reset_ui_state(self):
        self.control_panel.set_game_running(False)
        self.set_selection(None)

    def set_playing_state(self):
        self.control_panel.set_game_running(True)
        self.set_selection(None)

    def show_level_popup(self, l, s):
        if LevelCompleteDialog(l, s, self).exec(): self.next_level_signal.emit()

    def show_game_over_popup(self, l, s):
        if GameOverDialog(s, l, self).exec():
            self.restart_game_signal.emit()
        else:
            QApplication.quit()
