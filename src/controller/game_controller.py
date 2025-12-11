from PySide6.QtCore import QTimer
from src.model.simulation import SimulationModel
from src.view.main_window import MainWindow

class GameController:
    def __init__(self):
        self.view = MainWindow()
        self.model = SimulationModel(1000, 1000)
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)

        self.view.command_signal.connect(self.handle_command)
        self.view.start_game_signal.connect(self.start_game)
        self.view.next_level_signal.connect(self.start_next_level)
        self.view.restart_game_signal.connect(self.restart_game)
        self.view.surrender_signal.connect(self.surrender_game)

    def start(self):
        self.view.show()
        self.update_view()

    def start_game(self):
        self.model.is_running = True
        self.view.set_playing_state()
        self.timer.start(30)

    def start_next_level(self):
        self.model.start_next_level()
        self.timer.start(30)

    def restart_game(self):
        self.model.reset_game()
        self.view.reset_ui_state()
        self.view.radar.update_data([], self.model.landing_zone)
        self.update_view()

    def surrender_game(self):
        self.timer.stop()
        self.model.reset_game()
        self.model.is_running = False
        self.view.reset_ui_state()
        self.view.radar.update_data([], self.model.landing_zone)
        self.update_view()

    def game_loop(self):
        dt = 0.03 #temps de rafraichissement
        if self.model.level_complete:
            self.timer.stop()
            self.view.show_level_popup(self.model.current_level, self.model.score)
            return
        if self.model.game_over:
            self.timer.stop()
            self.view.show_game_over_popup(self.model.current_level, self.model.score)
            return

        self.model.update(dt)
        self.view.radar.update_data(self.model.aircrafts, self.model.landing_zone)
        self.update_view()

    def update_view(self):
        cfg = self.model.get_level_cfg()
        info = {
            "current": self.model.current_level,
            "spawned": self.model.planes_spawned,
            "total": cfg["total"],
            "min": cfg["score_min"],
            "next": self.model.get_time_before_next_spawn()
        }
        self.view.update_ui(self.model.score, self.model.stats, info, self.model.aircrafts)

    def handle_command(self, ac_id, cmd_type, value):
        target = next((a for a in self.model.aircrafts if a.id == ac_id), None)
        if target:
            if target.event == "MAYDAY" and cmd_type in ["ALTITUDE", "SPEED", "HOLD"]:
                print("REFUS : Panne moteur.")
                return

            if cmd_type == "HEADING":
                target.target_heading = value
                if target.state == "HOLDING": target.state = "FLYING"
            elif cmd_type == "ALTITUDE":
                target.altitude += value
                target.altitude = max(0, target.altitude)
            elif cmd_type == "SPEED":
                target.speed += value
                target.speed = max(150, min(800, target.speed))
            elif cmd_type == "HOLD":
                if target.state == "FLYING": target.state = "HOLDING"
                else: target.state = "FLYING"
            elif cmd_type == "LAND":
                target.state = "LANDING"