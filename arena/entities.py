import math
import random

import pygame as pg

from arena.settings import (
    BULLET_R, BULLET_SPEED, ENEMY_CHASE_RADIUS, ENEMY_H, ENEMY_HP,
    ENEMY_LOSE_RADIUS, ENEMY_PATROL_RANGE, ENEMY_PATROL_TIME, ENEMY_SPEED,
    ENEMY_W, HEIGHT, PLAYER_H, PLAYER_HP, PLAYER_SPEED, PLAYER_W,
    SHOOT_COOLDOWN, WIDTH,
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
        self.vx = 0.0
        self.vy = 0.0
        self.speed = PLAYER_SPEED
        self.max_hp = PLAYER_HP
        self.hp = PLAYER_HP
        self.cooldown = 0.0

    def update(self, dt, move_x, move_y, shooting, aim, bullets):
        if move_x and move_y:
            move_x *= 0.7071
            move_y *= 0.7071

        self.vx = move_x * self.speed
        self.vy = move_y * self.speed

        self.x = clamp(self.x + self.vx * dt, self.w * 0.5, WIDTH - self.w * 0.5)
        self.y = clamp(self.y + self.vy * dt, self.h * 0.5, HEIGHT - self.h * 0.5)

        self.cooldown = max(0.0, self.cooldown - dt)
        if shooting and self.cooldown <= 0.0:
            ax, ay = aim
            dx = ax - self.x
            dy = ay - self.y
            length = math.hypot(dx, dy)
            if length < 1e-6:
                dx, dy, length = 1.0, 0.0, 1.0
            dx /= length
            dy /= length
            bullets.append(Bullet(self.x, self.y,
                                  dx * BULLET_SPEED, dy * BULLET_SPEED,
                                  "player"))
            self.cooldown = SHOOT_COOLDOWN

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
