from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QGroupBox, QGridLayout
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton, QSpinBox
from PySide6.QtCore import Qt, Signal
from src.settings import *


class ControlPanel(QWidget):
    command_signal = Signal(str, float)  # Type, Valeur
    surrender_signal = Signal()
    start_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setFixedWidth(350)
        self.layout = QVBoxLayout(self)

        # Variable pour retenir quel avion était sélectionné juste avant
        # Cela permet d'éviter d'écraser la saisie de l'utilisateur
        self.last_selected_id = None

        # --- GROUPE COMMANDES ---
        self.gb = QGroupBox("TOUR DE CONTRÔLE")
        self.gb.setStyleSheet("font-weight: bold; font-size: 14px;")
        v = QVBoxLayout(self.gb)

        self.lbl_sel = QLabel("Aucun avion sélectionné")
        self.lbl_sel.setAlignment(Qt.AlignCenter)
        self.lbl_sel.setStyleSheet(f"color: {ACCENT_ORANGE}; border: 1px solid #444; padding: 5px;")
        v.addWidget(self.lbl_sel)

        # CAP
        h1 = QHBoxLayout()
        self.spin_head = QSpinBox()
        self.spin_head.setRange(0, 360)
        self.spin_head.setWrapping(True)  # Permet de passer de 360 à 0 direct
        self.spin_head.setStyleSheet("color: black; background: white;")

        b_head = QPushButton("Virer")
        b_head.setStyleSheet(BTN_BLUE)
        # Envoie la valeur saisie par l'utilisateur quand on clique
        b_head.clicked.connect(lambda: self.command_signal.emit("HEADING", float(self.spin_head.value())))

        h1.addWidget(QLabel("Cap:"))
        h1.addWidget(self.spin_head)
        h1.addWidget(b_head)
        v.addLayout(h1)

        # ALTITUDE
        h2 = QHBoxLayout() #
        b_up = QPushButton("Monter (+500 m)") # création d'un bouton
        b_up.setStyleSheet(BTN_BASE)
        b_up.clicked.connect(lambda: self.command_signal.emit("ALTITUDE", 500))
        b_dn = QPushButton("Descendre (-500 m)")
        b_dn.setStyleSheet(BTN_BASE)
        b_dn.clicked.connect(lambda: self.command_signal.emit("ALTITUDE", -500))
        h2.addWidget(b_up)
        h2.addWidget(b_dn)
        v.addLayout(h2)

        # VITESSE
        h3 = QHBoxLayout()
        b_fast = QPushButton("Vitesse (+50 km/h)")
        b_fast.setStyleSheet(BTN_BASE)
        b_fast.clicked.connect(lambda: self.command_signal.emit("SPEED", 50))
        b_slow = QPushButton("Vitesse (-50 km/h)")
        b_slow.setStyleSheet(BTN_BASE)
        b_slow.clicked.connect(lambda: self.command_signal.emit("SPEED", -50))
        h3.addWidget(b_fast)
        h3.addWidget(b_slow)
        v.addLayout(h3)

        # HOLD / LAND
        self.btn_hold = QPushButton("✋ MISE EN ATTENTE")
        self.btn_hold.setStyleSheet(BTN_PURPLE)
        self.btn_hold.clicked.connect(lambda: self.command_signal.emit("HOLD", 0))
        v.addWidget(self.btn_hold)

        self.btn_land = QPushButton("🛬 AUTORISER ATTERRISSAGE")
        self.btn_land.setStyleSheet(BTN_DISABLED)
        self.btn_land.clicked.connect(lambda: self.command_signal.emit("LAND", 0))
        v.addWidget(self.btn_land)

        self.gb.setEnabled(False)
        self.layout.addWidget(self.gb)

        self.layout.addStretch()

        # BOUTONS JEU
        self.btn_surrender = QPushButton("🏳️ ABANDONNER")
        self.btn_surrender.setStyleSheet(BTN_RED)
        self.btn_surrender.setEnabled(False)
        self.btn_surrender.clicked.connect(self.surrender_signal.emit)
        self.layout.addWidget(self.btn_surrender)

        self.btn_start = QPushButton("LANCER LA PARTIE")
        self.btn_start.setMinimumHeight(70)
        self.btn_start.setStyleSheet(BTN_GREEN)
        self.btn_start.clicked.connect(self.start_signal.emit)
        self.layout.addWidget(self.btn_start)

    def set_game_running(self, running):
        self.btn_start.setEnabled(not running)
        self.btn_start.setText("EN COURS..." if running else "LANCER LA PARTIE")
        self.btn_start.setStyleSheet(BTN_DISABLED if running else BTN_GREEN)
        self.btn_surrender.setEnabled(running)

    def update_selection(self, ac, errors):
        """
        ac : L'objet avion sélectionné (ou None)
        errors : Liste de chaines de caractères (ex: ["Trop Haut", "Trop Vite"])
        """
        if not ac:
            self.lbl_sel.setText("Aucun avion sélectionné")
            self.gb.setEnabled(False)
            self.last_selected_id = None  # Reset
            return

        self.gb.setEnabled(True)
        self.lbl_sel.setText(f"Avion: {ac.id}")

        # --- CORRECTIF POUR LE CAP ---
        # On ne met à jour la case 'Cap' QUE si on vient de changer d'avion.
        # Sinon, on laisse l'utilisateur modifier la valeur tranquillement.
        if self.last_selected_id != ac.id:
            self.spin_head.setValue(int(ac.target_heading))
            self.last_selected_id = ac.id

        # Le reste (boutons) peut être mis à jour en continu
        self.btn_hold.setText("SORTIR D'ATTENTE" if ac.state == "HOLDING" else "✋ MISE EN ATTENTE")

        # Gestion bouton Atterrissage
        if not errors:
            self.btn_land.setEnabled(True)
            self.btn_land.setStyleSheet(BTN_GREEN)
            self.btn_land.setText("AUTORISER ATTERRISSAGE")
        else:
            self.btn_land.setEnabled(False)
            self.btn_land.setStyleSheet(BTN_DISABLED)
            # Affiche les erreurs proprement
            error_text = ", ".join(errors)
            self.btn_land.setText(f"REFUSÉ\n({error_text})")