# src/model/simulation.py
import math
import random
from src.settings import LEVELS, MODEL_CENTER
from src.model.aircraft import CommercialAircraft, PrivateJet, FighterJet


class SimulationModel:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.aircrafts = []
        self.score = 0
        self.current_level = 1
        self.planes_spawned = 0
        self.level_complete = False
        self.is_running = False
        self.game_over = False
        self.stats = {"landed": 0, "crashed": 0, "out": 0}
        self.spawn_timer = 0
        self.next_id = 1

        # PISTE : Centrée horizontalement par rapport à MODEL_CENTER si besoin,
        # mais ici on utilise width/height passés en arguments (1000x1000)
        self.landing_zone = (width / 2 - 50, height - 150, 100, 100)

    def get_level_cfg(self):
        lvl = self.current_level if self.current_level <= 5 else 5
        return LEVELS[lvl]

    def get_time_before_next_spawn(self):
        cfg = self.get_level_cfg()
        if self.planes_spawned >= cfg["total"]: return 0
        return max(0, int(cfg["rate"] - self.spawn_timer))

    def reset_game(self):
        self.current_level = 1
        self.planes_spawned = 0
        self.score = 0
        self.stats = {"landed": 0, "crashed": 0, "out": 0}
        self.spawn_timer = 0
        self.aircrafts = []
        self.is_running = True
        self.level_complete = False
        self.game_over = False
        self.next_id = 1

    def start_next_level(self):
        if self.current_level < 5:
            self.current_level += 1
            self.planes_spawned = 0
            self.spawn_timer = 0
            self.aircrafts = []
            self.level_complete = False
            self.is_running = True
        else:
            self.game_over = True

    def spawn_aircraft(self):
        cfg = self.get_level_cfg()
        if self.planes_spawned >= cfg["total"]: return

        radius = 450
        # CORRECTION MAJEURE : On utilise MODEL_CENTER pour être synchro avec le Radar
        cx, cy = MODEL_CENTER, MODEL_CENTER

        angle = random.randint(0, 359)
        rad = math.radians(angle - 90)
        x = cx + radius * math.cos(rad)
        y = cy + radius * math.sin(rad)
        heading = (angle + 180 + random.randint(-45, 45)) % 360
        alt = random.randint(2000, 4000)

        rand_val = random.random()
        if rand_val < 0.6:
            ac = CommercialAircraft(f"AF{self.next_id:03d}", x, y, heading, alt)
        elif rand_val < 0.9:
            ac = PrivateJet(f"PJ{self.next_id:03d}", x, y, heading, alt)
        else:
            ac = FighterJet(f"MIL{self.next_id:03d}", x, y, heading, alt)

        self.aircrafts.append(ac)
        self.next_id += 1
        self.planes_spawned += 1

    def update(self, dt):
        if not self.is_running or self.game_over or self.level_complete: return

        cfg = self.get_level_cfg()
        self.spawn_timer += dt
        if self.spawn_timer > cfg["rate"]:
            self.spawn_aircraft()
            self.spawn_timer = 0

        self._trigger_events()
        self._update_aircrafts(dt)
        self._check_collisions()
        self._check_progression(cfg)

    def _trigger_events(self):
        prob = 0.0002 * self.current_level
        for ac in self.aircrafts:
            if ac.state in ["FLYING", "HOLDING"] and ac.event is None:
                if random.random() < prob:
                    if random.randint(1, 3) == 1:
                        ac.event = "MAYDAY"
                    else:
                        ac.event = "URGENCY"

    def _update_aircrafts(self, dt):
        keep = []
        lx, ly, lw, lh = self.landing_zone

        for ac in self.aircrafts:
            if not ac.score_counted:
                if ac.state == "LANDED":
                    bonus = 300 if ac.event == "MAYDAY" else (150 if ac.event == "URGENCY" else 0)
                    self.score += ac.base_score + bonus
                    self.stats["landed"] += 1
                    ac.score_counted = True #donc ton score a bien été compter donc l'ignorer la prochaine fois
                elif ac.state == "CRASHED":
                    self.score -= 50
                    self.stats["crashed"] += 1
                    ac.score_counted = True
                elif ac.state == "OUT_OF_BOUNDS":
                    self.score -= 20
                    self.stats["out"] += 1
                    ac.score_counted = True

            if ac.state in ["CRASHED", "OUT_OF_BOUNDS"]:
                ac.despawn_timer += dt
                if ac.despawn_timer < 2.0: keep.append(ac)
                continue # donc pas prendre en compte le reste de la définition

            if ac.state == "LANDED": continue

            if ac.fuel <= 0 and ac.state != "LANDING": #!= n'est pas en train d'attérrir (continue de planer meme avec 0 de fuel)
                ac.state = "CRASHED"
                keep.append(ac)
                continue

            ac.update_position(dt)

            if ac.altitude <= 0:
                ac.altitude = 0
                on_rw = (lx - 20 <= ac.x <= lx + lw + 20) and (ly - 20 <= ac.y <= ly + lh + 20)
                if on_rw:
                    if ac.state == "LANDING" and ac.speed <= 1:
                        ac.state = "LANDED"
                    elif ac.state != "LANDING":
                        ac.state = "CRASHED"
                else:
                    ac.state = "CRASHED"
            keep.append(ac)

        # Filtre distance par rapport au MODEL_CENTER
        self.aircrafts = [a for a in keep if not (a.state == "OUT_OF_BOUNDS" and math.sqrt(
            (a.x - MODEL_CENTER) ** 2 + (a.y - MODEL_CENTER) ** 2) > 700)]

    def _check_collisions(self):
        for i, a1 in enumerate(self.aircrafts):
            for a2 in self.aircrafts[i + 1:]:
                valid = ["FLYING", "LANDING", "HOLDING"]
                if a1.state in valid and a2.state in valid:
                    d = math.sqrt((a1.x - a2.x) ** 2 + (a1.y - a2.y) ** 2)
                    adh = abs(a1.altitude - a2.altitude)
                    if d < 30 and adh < 100:
                        a1.state = "CRASHED"
                        a2.state = "CRASHED"

    def _check_progression(self, cfg):
        if self.game_over or self.level_complete: return
        if self.planes_spawned >= cfg["total"] and len(self.aircrafts) == 0:
            if self.score >= cfg["score_min"]:
                self.level_complete = True
            else:
                self.game_over = True