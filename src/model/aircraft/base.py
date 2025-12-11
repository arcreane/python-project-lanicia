import math


class Aircraft:
    """Classe de base : gère la physique, le mouvement et les états."""

    def __init__(self, uid, x, y, heading, altitude):
        self.id = uid
        self.x = x
        self.y = y
        self.heading = float(heading)
        self.target_heading = float(heading)
        self.altitude = altitude

        # Défauts
        self.speed = 250
        self.base_score = 100
        self.fuel = 100.0
        self.consumption = 0.5
        self.type_label = "GENERIC"

        # États
        self.despawn_timer = 0.0
        self.state = "FLYING"
        self.score_counted = False
        self.event = None  # None, "MAYDAY", "URGENCY"

    def update_position(self, dt):
        if self.state in ["CRASHED", "LANDED"]:
            return

        # Gestion Panne
        if self.event == "MAYDAY" and self.state != "LANDING":
            self.altitude -= 120 * dt
            if self.speed > 220: self.speed -= 15 * dt
            if self.state == "HOLDING": self.state = "FLYING"

        # Logique d'état
        if self.state == "LANDING":
            self._handle_landing(dt)
        elif self.state == "HOLDING":
            self.heading = (self.heading + 3.0) % 360
            self.fuel -= self.consumption * dt
        else:
            self._handle_flying(dt)

        # Mouvement physique
        if self.speed > 0:
            px_speed = self.speed * 0.1
            rad = math.radians(self.heading - 90)
            self.x += px_speed * dt * math.cos(rad)
            self.y += px_speed * dt * math.sin(rad)

        # Limites de zone
        if self.state != "LANDING":
            if math.sqrt((self.x - 500) ** 2 + (self.y - 500) ** 2) > 510:
                self.state = "OUT_OF_BOUNDS"

    def _handle_flying(self, dt):
        diff = self.target_heading - self.heading
        diff = (diff + 180) % 360 - 180
        turn_rate = 3.0
        if abs(diff) < turn_rate:
            self.heading = self.target_heading
        else:
            self.heading += turn_rate if diff > 0 else -turn_rate
        self.heading %= 360
        self.fuel -= self.consumption * dt

    def _handle_landing(self, dt):
        RUNWAY_X, RUNWAY_Y = 500, 900
        dx = RUNWAY_X - self.x
        dy = RUNWAY_Y - self.y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        if dist > 300:  # Approche
            tgt = math.degrees(math.atan2(dy, dx))
            self.heading = (tgt + 90) % 360
            if self.event != "MAYDAY" and self.altitude > 1500:
                self.altitude -= 30 * dt
            if self.speed > 300:
                self.speed -= 20 * dt
        elif dist > 10:  # Finale
            tgt = math.degrees(math.atan2(dy, dx))
            self.heading = (tgt + 90) % 360
            min_safe = dist * 2.0
            pot_alt = self.altitude - (400 * dt)
            self.altitude = pot_alt if pot_alt > min_safe else max(self.altitude, min_safe)
            if self.speed > 160: self.speed -= 100 * dt
        else:  # Touché
            self.altitude = 0
            self.speed = max(0, self.speed - 150 * dt)