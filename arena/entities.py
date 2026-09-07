import math
import random

import pygame as pg

from arena.settings import (
    BULLET_R, BULLET_SPEED, ENEMY_CHASE_RADIUS, ENEMY_H, ENEMY_HP,
    ENEMY_LOSE_RADIUS, ENEMY_PATROL_RANGE, ENEMY_PATROL_TIME, ENEMY_SPEED,
    ENEMY_W, HEIGHT, PLAYER_DIRECT_SPEED, PLAYER_DRAG, PLAYER_H, PLAYER_HP,
    PLAYER_MAX_SPEED, PLAYER_RADIUS, PLAYER_THRUST, PLAYER_TURN_RATE,
    PLAYER_W, SHOOT_COOLDOWN, SPAWNER_HP, SPAWNER_SIZE, WIDTH,
)


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


class Bullet:
    def __init__(self, x, y, vx, vy, owner):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.r = BULLET_R
        self.owner = owner
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.alive = False

    def rect(self):
        return pg.Rect(int(self.x - self.r), int(self.y - self.r),
                       self.r * 2, self.r * 2)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = PLAYER_W
        self.h = PLAYER_H
        self.radius = PLAYER_RADIUS
        self.angle = -math.pi / 2
        self.vx = 0.0
        self.vy = 0.0
        self.max_hp = PLAYER_HP
        self.hp = PLAYER_HP
        self.cooldown = 0.0

    def rotate(self, direction, dt):
        self.angle += direction * PLAYER_TURN_RATE * dt
        if self.angle > math.pi:
            self.angle -= 2.0 * math.pi
        elif self.angle < -math.pi:
            self.angle += 2.0 * math.pi

    def thrust(self, dt):
        self.vx += math.cos(self.angle) * PLAYER_THRUST * dt
        self.vy += math.sin(self.angle) * PLAYER_THRUST * dt

    def move_direct(self, dx, dy):
        if dx or dy:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            self.vx = dx * PLAYER_DIRECT_SPEED
            self.vy = dy * PLAYER_DIRECT_SPEED
            self.angle = math.atan2(dy, dx)
        else:
            self.vx = 0.0
            self.vy = 0.0

    def shoot(self, bullets):
        if self.cooldown > 0.0:
            return False
        dx = math.cos(self.angle)
        dy = math.sin(self.angle)
        bullets.append(Bullet(self.x + dx * self.radius,
                              self.y + dy * self.radius,
                              dx * BULLET_SPEED, dy * BULLET_SPEED,
                              "player"))
        self.cooldown = SHOOT_COOLDOWN
        return True

    def integrate(self, dt, drag=True):
        if drag:
            factor = max(0.0, 1.0 - PLAYER_DRAG * dt)
            self.vx *= factor
            self.vy *= factor

        speed = math.hypot(self.vx, self.vy)
        if speed > PLAYER_MAX_SPEED:
            scale = PLAYER_MAX_SPEED / speed
            self.vx *= scale
            self.vy *= scale

        self.x = clamp(self.x + self.vx * dt, self.radius, WIDTH - self.radius)
        self.y = clamp(self.y + self.vy * dt, self.radius, HEIGHT - self.radius)
        self.cooldown = max(0.0, self.cooldown - dt)

    def speed(self):
        return math.hypot(self.vx, self.vy)

    def rect(self):
        r = pg.Rect(0, 0, self.w, self.h)
        r.center = (int(self.x), int(self.y))
        return r


class Enemy:
    def __init__(self, x, y, rng=None):
        self.rng = rng or random
        self.x = x
        self.y = y
        self.w = ENEMY_W
        self.h = ENEMY_H
        self.speed = ENEMY_SPEED
        self.max_hp = ENEMY_HP
        self.hp = ENEMY_HP
        self.state = "PATROL"
        self.target = (x, y)
        self.state_timer = 0.0

    def update(self, dt, player):
        self.state_timer += dt
        dist2 = (player.x - self.x) ** 2 + (player.y - self.y) ** 2

        if self.state == "PATROL":
            reached = (abs(self.x - self.target[0]) < 5.0 and
                       abs(self.y - self.target[1]) < 5.0)
            if self.state_timer > ENEMY_PATROL_TIME or reached:
                self.target = (
                    clamp(self.x + self.rng.randint(-ENEMY_PATROL_RANGE,
                                                    ENEMY_PATROL_RANGE),
                          0.0, WIDTH),
                    clamp(self.y + self.rng.randint(-ENEMY_PATROL_RANGE,
                                                    ENEMY_PATROL_RANGE),
                          0.0, HEIGHT),
                )
                self.state_timer = 0.0
            if dist2 < ENEMY_CHASE_RADIUS ** 2:
                self.state = "CHASE"
                self.state_timer = 0.0
        else:
            if dist2 > ENEMY_LOSE_RADIUS ** 2:
                self.state = "PATROL"
                self.state_timer = 0.0
            else:
                self.target = (player.x, player.y)

        dx = self.target[0] - self.x
        dy = self.target[1] - self.y
        length = math.hypot(dx, dy)
        if length > 1.0:
            dx /= length
            dy /= length
            self.x = clamp(self.x + dx * self.speed * dt,
                           self.w * 0.5, WIDTH - self.w * 0.5)
            self.y = clamp(self.y + dy * self.speed * dt,
                           self.h * 0.5, HEIGHT - self.h * 0.5)

    def rect(self):
        r = pg.Rect(0, 0, self.w, self.h)
        r.center = (int(self.x), int(self.y))
        return r


class Spawner:
    def __init__(self, x, y, interval):
        self.x = x
        self.y = y
        self.size = SPAWNER_SIZE
        self.max_hp = SPAWNER_HP
        self.hp = SPAWNER_HP
        self.interval = interval
        self.timer = interval * 0.5

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0.0:
            self.timer += self.interval
            return True
        return False

    def rect(self):
        r = pg.Rect(0, 0, self.size, self.size)
        r.center = (int(self.x), int(self.y))
        return r
