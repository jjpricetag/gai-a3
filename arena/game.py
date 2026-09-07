import math
import random

from arena.entities import Enemy, Player, Spawner
from arena.settings import (
    ENEMY_CONTACT_DAMAGE_COOLDOWN, HEIGHT, MAX_ENEMIES_BASE,
    MAX_ENEMIES_PER_PHASE, MAX_EPISODE_SECONDS, PHASE_SPAWNERS_BASE,
    PHASE_SPAWNERS_MAX, SPAWN_INTERVAL_BASE, SPAWN_INTERVAL_MIN,
    SPAWN_INTERVAL_PER_PHASE, SPAWN_OFFSET, SPAWNER_MIN_PLAYER_DIST,
    SPAWNER_MIN_SEPARATION, WIDTH,
)


class Game:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.reset()

    def reset(self):
        self.player = Player(WIDTH * 0.5, HEIGHT * 0.5)
        self.bullets = []
        self.enemies = []
        self.spawners = []
        self.phase = 1
        self.time = 0.0
        self.over = False
        self.contact_timer = 0.0
        self.events = {}
        self._build_phase()

    def spawner_count(self):
        return min(PHASE_SPAWNERS_BASE + self.phase - 1, PHASE_SPAWNERS_MAX)

    def spawn_interval(self):
        return max(SPAWN_INTERVAL_MIN,
                   SPAWN_INTERVAL_BASE - SPAWN_INTERVAL_PER_PHASE * (self.phase - 1))

    def max_enemies(self):
        return MAX_ENEMIES_BASE + MAX_ENEMIES_PER_PHASE * (self.phase - 1)

    def _build_phase(self):
        interval = self.spawn_interval()
        placed = []
        for _ in range(self.spawner_count()):
            for _ in range(200):
                x = self.rng.uniform(60.0, WIDTH - 60.0)
                y = self.rng.uniform(60.0, HEIGHT - 60.0)
                if (x - self.player.x) ** 2 + (y - self.player.y) ** 2 \
                        < SPAWNER_MIN_PLAYER_DIST ** 2:
                    continue
                if any((x - px) ** 2 + (y - py) ** 2 < SPAWNER_MIN_SEPARATION ** 2
                       for px, py in placed):
                    continue
                placed.append((x, y))
                self.spawners.append(Spawner(x, y, interval))
                break

    def _emit_enemy(self, spawner):
        if len(self.enemies) >= self.max_enemies():
            return
        angle = self.rng.uniform(-math.pi, math.pi)
        x = spawner.x + math.cos(angle) * SPAWN_OFFSET
        y = spawner.y + math.sin(angle) * SPAWN_OFFSET
        x = min(max(x, 20.0), WIDTH - 20.0)
        y = min(max(y, 20.0), HEIGHT - 20.0)
        self.enemies.append(Enemy(x, y, self.rng))

    def update(self, dt, rotate=0.0, thrust=False, move=None, shoot=False):
        if self.over:
            return

        self.events = {"enemies_killed": 0, "spawners_killed": 0,
                       "phase_advanced": 0, "damage_taken": 0, "shots_fired": 0}

        self.time += dt
        self.contact_timer = max(0.0, self.contact_timer - dt)

        if move is None:
            if rotate:
                self.player.rotate(rotate, dt)
            if thrust:
                self.player.thrust(dt)
            self.player.integrate(dt, drag=True)
        else:
            self.player.move_direct(move[0], move[1])
            self.player.integrate(dt, drag=False)

        if shoot and self.player.shoot(self.bullets):
            self.events["shots_fired"] = 1

        for s in self.spawners:
            if s.update(dt):
                self._emit_enemy(s)

        for e in self.enemies:
            e.update(dt, self.player)

        for b in self.bullets:
            b.update(dt)
        self.bullets = [b for b in self.bullets if b.alive]

        for b in self.bullets:
            if b.owner != "player":
                continue
            hit = False
            for e in self.enemies:
                if e.hp > 0 and b.rect().colliderect(e.rect()):
                    e.hp -= 1
                    if e.hp <= 0:
                        self.events["enemies_killed"] += 1
                    hit = True
                    break
            if not hit:
                for s in self.spawners:
                    if s.hp > 0 and b.rect().colliderect(s.rect()):
                        s.hp -= 1
                        if s.hp <= 0:
                            self.events["spawners_killed"] += 1
                        hit = True
                        break
            if hit:
                b.alive = False

        self.bullets = [b for b in self.bullets if b.alive]
        self.enemies = [e for e in self.enemies if e.hp > 0]
        self.spawners = [s for s in self.spawners if s.hp > 0]

        if self.contact_timer <= 0.0:
            for e in self.enemies:
                if e.rect().colliderect(self.player.rect()):
                    self.player.hp -= 1
                    self.events["damage_taken"] = 1
                    self.contact_timer = ENEMY_CONTACT_DAMAGE_COOLDOWN
                    break

        if not self.spawners:
            self.phase += 1
            self.events["phase_advanced"] = 1
            self._build_phase()

        if self.player.hp <= 0:
            self.over = True
        if self.time >= MAX_EPISODE_SECONDS:
            self.over = True

    def nearest_enemy(self):
        return self._nearest(self.enemies)

    def nearest_spawner(self):
        return self._nearest(self.spawners)

    def _nearest(self, items):
        best = None
        best_d2 = None
        for it in items:
            d2 = (it.x - self.player.x) ** 2 + (it.y - self.player.y) ** 2
            if best_d2 is None or d2 < best_d2:
                best = it
                best_d2 = d2
        return best
