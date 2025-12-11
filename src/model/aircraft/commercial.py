import random
from .base import Aircraft

class CommercialAircraft(Aircraft):
    def __init__(self, uid, x, y, heading, altitude):
        super().__init__(uid, x, y, heading, altitude)
        self.type_label = "COMMERCIAL"
        self.speed = random.randint(240, 360)
        self.base_score = 100
        self.fuel = 100.0
        self.consumption = 0.4