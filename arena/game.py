import random

from arena.entities import Enemy, Player
from arena.settings import (
    ENEMY_CONTACT_DAMAGE_COOLDOWN, ENEMY_COUNT, ENEMY_MIN_SPAWN_DIST,
    HEIGHT, MAX_EPISODE_SECONDS, WIDTH,
)


class Game:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.reset()

    def reset(self):
        self.player = Player(WIDTH * 0.5, HEIGHT * 0.5)
        self.bullets = []
        self.enemies = []
        self.time = 0.0
        self.over = False
        self.contact_timer = 0.0
        self._spawn_enemies(ENEMY_COUNT)

    def _spawn_enemies(self, n):
        for _ in range(n):
            while True:
                x = self.rng.uniform(40.0, WIDTH - 40.0)
                y = self.rng.uniform(40.0, HEIGHT - 40.0)
                dx = x - self.player.x
                dy = y - self.player.y
                if dx * dx + dy * dy > ENEMY_MIN_SPAWN_DIST ** 2:
                    self.enemies.append(Enemy(x, y, self.rng))
                    break

    def update(self, dt, move_x, move_y, shooting, aim):
        if self.over:
            return

        self.time += dt
        self.contact_timer = max(0.0, self.contact_timer - dt)

        self.player.update(dt, move_x, move_y, shooting, aim, self.bullets)

        for e in self.enemies:
            e.update(dt, self.player)

        for b in self.bullets:
            b.update(dt)
        self.bullets = [b for b in self.bullets if b.alive]

        for b in self.bullets:
            if b.owner != "player":
                continue
            for e in self.enemies:
                if e.hp > 0 and b.rect().colliderect(e.rect()):
                    e.hp -= 1
                    b.alive = False
                    break
        self.bullets = [b for b in self.bullets if b.alive]
        self.enemies = [e for e in self.enemies if e.hp > 0]

        if self.contact_timer <= 0.0:
            for e in self.enemies:
                if e.rect().colliderect(self.player.rect()):
                    self.player.hp -= 1
                    self.contact_timer = ENEMY_CONTACT_DAMAGE_COOLDOWN
                    break

        if self.player.hp <= 0:
            self.over = True
        if self.time >= MAX_EPISODE_SECONDS:
            self.over = True
