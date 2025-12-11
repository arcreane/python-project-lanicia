import random
from .base import Aircraft

class FighterJet(Aircraft):
    def __init__(self, uid, x, y, heading, altitude):
        super().__init__(uid, x, y, heading, altitude)
        self.type_label = "FIGHTER"
        self.speed = random.randint(600, 850)
        self.base_score = 300
        self.fuel = 60.0
        self.consumption = 0.8