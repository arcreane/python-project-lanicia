import sys
from PySide6.QtWidgets import QApplication
from src.controller.game_controller import GameController

if __name__ == "__main__":
    app = QApplication(sys.argv)

    controller = GameController()
    controller.start()

    sys.exit(app.exec())