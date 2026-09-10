import math
import os

import pygame as pg

CELL = 32
ROT_STEP = 6
SHEET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "sheet.png")

PLAYER_CELLS = [(c, 0) for c in range(5)]
ENEMY_CELLS = [(c, 1) for c in range(5)]
SPAWNER_CELLS = [(c, 11) for c in range(11, 15)]
BURST_CELLS = [(1, 9), (3, 9), (4, 9), (2, 8), (3, 8), (4, 8)]
BULLET_RECT = (160, 16, 16, 16)

PLAYER_PX = 34
ENEMY_PX = 29
SPAWNER_PX = 40
BULLET_PX = 14
BURST_PX = 52

FRAME_RATE = 12.0


def _tight(surf):
    rect = surf.get_bounding_rect()
    if rect.width == 0 or rect.height == 0:
        return surf
    return surf.subsurface(rect).copy()


def _fit(surf, target):
    w, h = surf.get_size()
    scale = target / float(max(w, h))
    return pg.transform.scale(surf, (max(1, int(round(w * scale))),
                                     max(1, int(round(h * scale)))))


class Sprites:
    def __init__(self):
        self.ready = False
        self.player = []
        self.enemy = []
        self.spawner = []
        self.burst = []
        self.bullet = None

    def load(self):
        if self.ready:
            return True
        if not os.path.exists(SHEET_PATH):
            return False
        sheet = pg.image.load(SHEET_PATH).convert_alpha()
        self.player = [self._spin(self._cell(sheet, c, r), PLAYER_PX)
                       for c, r in PLAYER_CELLS]
        self.enemy = [self._spin(self._cell(sheet, c, r), ENEMY_PX)
                      for c, r in ENEMY_CELLS]
        self.spawner = [_fit(self._cell(sheet, c, r), SPAWNER_PX)
                        for c, r in SPAWNER_CELLS]
        self.burst = [_fit(self._cell(sheet, c, r), BURST_PX)
                      for c, r in BURST_CELLS]
        self.bullet = _fit(
            _tight(sheet.subsurface(pg.Rect(BULLET_RECT)).copy()), BULLET_PX)
        self.ready = True
        return True

    def _cell(self, sheet, col, row):
        return _tight(sheet.subsurface(
            pg.Rect(col * CELL, row * CELL, CELL, CELL)).copy())

    def _spin(self, surf, target):
        base = _fit(surf, target)
        return [pg.transform.rotate(base, -a)
                for a in range(0, 360, ROT_STEP)]

    def facing(self, spins, angle):
        deg = (math.degrees(angle) + 90.0) % 360.0
        return spins[int(round(deg / ROT_STEP)) % len(spins)]

    def cycle(self, frames, clock, offset=0.0):
        return frames[int((clock + offset) * FRAME_RATE) % len(frames)]


def blit_mid(screen, surf, x, y):
    screen.blit(surf, surf.get_rect(center=(int(x), int(y))))
