import math

import pygame as pg

from arena.game import FX_TIME
from arena.settings import (
    BG, BULLET_COL, ENEMY_COL, GRID, HEIGHT, HP_BACK, HP_FILL, MUTED,
    PLAYER_COL, SPAWNER_COL, SPAWNER_CORE, WHITE, WIDTH,
)
from arena.sprites import Sprites, blit_mid

_ART = Sprites()


def _health_bar(screen, cx, top, width, ratio):
    back = pg.Rect(int(cx - width * 0.5), int(top), int(width), 3)
    pg.draw.rect(screen, HP_BACK, back)
    if ratio > 0.0:
        fill = pg.Rect(back.left, back.top, int(width * ratio), 3)
        pg.draw.rect(screen, HP_FILL, fill)


def draw(screen, font, game):
    screen.fill(BG)
    art = _ART if _ART.load() else None

    for x in range(0, WIDTH, 40):
        pg.draw.line(screen, GRID, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pg.draw.line(screen, GRID, (0, y), (WIDTH, y))

    for s in game.spawners:
        rect = s.rect()
        if art:
            blit_mid(screen, art.cycle(art.spawner, game.time, s.x * 0.01),
                     s.x, s.y)
        else:
            pg.draw.rect(screen, SPAWNER_COL, rect, border_radius=5)
            pg.draw.rect(screen, SPAWNER_CORE, rect.inflate(-16, -16),
                         border_radius=3)
        _health_bar(screen, s.x, rect.top - 7, s.size, s.hp / s.max_hp)

    for b in game.bullets:
        if art:
            blit_mid(screen, art.bullet, b.x, b.y)
        else:
            pg.draw.circle(screen, BULLET_COL, (int(b.x), int(b.y)), b.r)

    for e in game.enemies:
        rect = e.rect()
        if art:
            heading = math.atan2(game.player.y - e.y, game.player.x - e.x)
            blit_mid(screen,
                     art.facing(art.cycle(art.enemy, game.time, e.x * 0.013),
                                heading),
                     e.x, e.y)
        else:
            pg.draw.rect(screen, ENEMY_COL, rect)
        if e.hp < e.max_hp:
            _health_bar(screen, e.x, rect.top - 6, e.w, e.hp / e.max_hp)

    p = game.player
    if art:
        ship = art.facing(art.cycle(art.player, game.time), p.angle)
        if game.hurt > 0.0 and int(game.hurt * 30.0) % 2 == 0:
            ship = ship.copy()
            ship.fill((210, 60, 60, 0), special_flags=pg.BLEND_RGBA_ADD)
        blit_mid(screen, ship, p.x, p.y)
    else:
        nose = (p.x + math.cos(p.angle) * 15.0, p.y + math.sin(p.angle) * 15.0)
        left = (p.x + math.cos(p.angle + 2.5) * 12.0,
                p.y + math.sin(p.angle + 2.5) * 12.0)
        right = (p.x + math.cos(p.angle - 2.5) * 12.0,
                 p.y + math.sin(p.angle - 2.5) * 12.0)
        pg.draw.polygon(screen, PLAYER_COL, [nose, left, right])

    for fx in game.fx:
        ratio = min(fx[2] / FX_TIME, 0.999)
        if art:
            blit_mid(screen, art.burst[int(ratio * len(art.burst))],
                     fx[0], fx[1])
        else:
            pg.draw.circle(screen, BULLET_COL, (int(fx[0]), int(fx[1])),
                           int(6 + 22 * ratio), 2)

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


def draw_overlay(screen, font, game, data):
    p = game.player

    enemy = game.nearest_enemy()
    if enemy is not None:
        pg.draw.line(screen, ENEMY_COL, (p.x, p.y), (enemy.x, enemy.y), 1)
    spawner = game.nearest_spawner()
    if spawner is not None:
        pg.draw.line(screen, SPAWNER_COL, (p.x, p.y), (spawner.x, spawner.y), 1)
    pg.draw.line(screen, WHITE, (p.x, p.y),
                 (p.x + math.cos(p.angle) * 240.0,
                  p.y + math.sin(p.angle) * 240.0), 1)

    actions = data["actions"]
    probs = data["probs"]
    panel_w, row_h = 240, 18
    x0 = WIDTH - panel_w - 12
    y0 = 10
    panel_h = 30 + row_h * len(actions) + 62

    shade = pg.Surface((panel_w, panel_h), pg.SRCALPHA)
    shade.fill((0, 0, 0, 160))
    screen.blit(shade, (x0, y0))
    pg.draw.rect(screen, HP_BACK, pg.Rect(x0, y0, panel_w, panel_h), 1)

    screen.blit(font.render("POLICY", True, MUTED), (x0 + 10, y0 + 7))

    bar_x, bar_w = x0 + 126, 62
    for i, name in enumerate(actions):
        y = y0 + 30 + i * row_h
        col = PLAYER_COL if i == data["chosen"] else MUTED
        screen.blit(font.render(name, True, col), (x0 + 10, y - 3))
        pg.draw.rect(screen, HP_BACK, pg.Rect(bar_x, y + 2, bar_w, 9))
        width = int(bar_w * float(probs[i]))
        if width > 0:
            pg.draw.rect(screen, col, pg.Rect(bar_x, y + 2, width, 9))
        screen.blit(font.render("{:>3.0f}%".format(float(probs[i]) * 100.0),
                                True, col), (bar_x + bar_w + 8, y - 3))

    y = y0 + 36 + row_h * len(actions)
    for text in ("V(s) {:>+8.2f}".format(data["value"]),
                 "entropy {:.2f}  eff {:.2f}".format(
                     data["entropy"], math.exp(data["entropy"])),
                 "aim {:.2f}".format(game.aim_alignment())):
        screen.blit(font.render(text, True, WHITE), (x0 + 10, y))
        y += 18
