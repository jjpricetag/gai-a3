import math

import pygame as pg

from arena.settings import (
    BG, BULLET_COL, ENEMY_COL, GRID, HEIGHT, HP_BACK, HP_FILL, MUTED,
    PLAYER_COL, SPAWNER_COL, SPAWNER_CORE, WHITE, WIDTH,
)


def _health_bar(screen, cx, top, width, ratio):
    back = pg.Rect(int(cx - width * 0.5), int(top), int(width), 3)
    pg.draw.rect(screen, HP_BACK, back)
    if ratio > 0.0:
        fill = pg.Rect(back.left, back.top, int(width * ratio), 3)
        pg.draw.rect(screen, HP_FILL, fill)


def draw(screen, font, game):
    screen.fill(BG)

    for x in range(0, WIDTH, 40):
        pg.draw.line(screen, GRID, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pg.draw.line(screen, GRID, (0, y), (WIDTH, y))

    for s in game.spawners:
        rect = s.rect()
        pg.draw.rect(screen, SPAWNER_COL, rect, border_radius=5)
        pg.draw.rect(screen, SPAWNER_CORE, rect.inflate(-16, -16), border_radius=3)
        _health_bar(screen, s.x, rect.top - 7, s.size, s.hp / s.max_hp)

    for b in game.bullets:
        pg.draw.circle(screen, BULLET_COL, (int(b.x), int(b.y)), b.r)

    for e in game.enemies:
        rect = e.rect()
        pg.draw.rect(screen, ENEMY_COL, rect)
        if e.hp < e.max_hp:
            _health_bar(screen, e.x, rect.top - 6, e.w, e.hp / e.max_hp)

    p = game.player
    nose = (p.x + math.cos(p.angle) * 15.0, p.y + math.sin(p.angle) * 15.0)
    left = (p.x + math.cos(p.angle + 2.5) * 12.0,
            p.y + math.sin(p.angle + 2.5) * 12.0)
    right = (p.x + math.cos(p.angle - 2.5) * 12.0,
             p.y + math.sin(p.angle - 2.5) * 12.0)
    pg.draw.polygon(screen, PLAYER_COL, [nose, left, right])

    lines = [
        "Phase {}".format(game.phase),
        "HP {}/{}".format(p.hp, p.max_hp),
        "Spawners {}".format(len(game.spawners)),
        "Enemies {}/{}".format(len(game.enemies), game.max_enemies()),
        "Time {:.1f}".format(game.time),
    ]
    for i, text in enumerate(lines):
        screen.blit(font.render(text, True, WHITE), (12, 10 + i * 19))

    if game.over:
        label = font.render("EPISODE OVER  -  press R", True, MUTED)
        screen.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
