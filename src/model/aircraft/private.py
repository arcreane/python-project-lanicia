import random
from .base import Aircraft

class PrivateJet(Aircraft):
    def __init__(self, uid, x, y, heading, altitude):
        super().__init__(uid, x, y, heading, altitude)
        self.type_label = "PRIVATE"
        self.speed = random.randint(400, 550)
        self.base_score = 150
        self.fuel = 80.0
        self.consumption = 0.6