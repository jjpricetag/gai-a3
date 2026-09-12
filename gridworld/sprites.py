import os

import pygame

SHEET_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "gridworld_sheet.png")
SHEET_CELL = 64
WALK_FRAMES = 11
FIRE_FRAMES = 8

_raw_sheet = None
_cache_by_tile_size = {}


def _load_sheet():
    global _raw_sheet
    if _raw_sheet is None:
        _raw_sheet = pygame.image.load(SHEET_PATH).convert_alpha()
    return _raw_sheet


def get_sprites(tile_size: int) -> dict:
    """Returns {'walk': [11 frames], 'key': surf, 'apple': surf, 'chest': surf,
    'rock': surf, 'fire': [8 frames], 'monster': surf}, each scaled to
    tile_size x tile_size. Cached per tile_size."""
    cached = _cache_by_tile_size.get(tile_size)
    if cached is not None:
        return cached

    sheet = _load_sheet()

    def cell(col, row):
        rect = pygame.Rect(col * SHEET_CELL, row * SHEET_CELL, SHEET_CELL, SHEET_CELL)
        surf = sheet.subsurface(rect).copy()
        if tile_size != SHEET_CELL:
            surf = pygame.transform.smoothscale(surf, (tile_size, tile_size))
        return surf

    sprites = {
        "walk": [cell(i, 0) for i in range(WALK_FRAMES)],
        "key": cell(0, 1),
        "apple": cell(0, 2),
        "chest": cell(0, 3),
        "rock": cell(0, 4),
        "fire": [cell(i, 5) for i in range(FIRE_FRAMES)],
        "monster": cell(0, 6),
    }
    _cache_by_tile_size[tile_size] = sprites
    return sprites
