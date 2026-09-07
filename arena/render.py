import pygame as pg

from arena.settings import (
    BG, BULLET_COL, ENEMY_COL, GRID, HEIGHT, MUTED, PLAYER_COL, WHITE, WIDTH,
)


def draw(screen, font, game):
    screen.fill(BG)

    for x in range(0, WIDTH, 40):
        pg.draw.line(screen, GRID, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pg.draw.line(screen, GRID, (0, y), (WIDTH, y))

    for b in game.bullets:
        pg.draw.circle(screen, BULLET_COL, (int(b.x), int(b.y)), b.r)

    for e in game.enemies:
        pg.draw.rect(screen, ENEMY_COL, e.rect())

    pg.draw.rect(screen, PLAYER_COL, game.player.rect(), border_radius=4)

    lines = [
        "HP {}/{}".format(game.player.hp, game.player.max_hp),
        "Enemies {}".format(len(game.enemies)),
        "Time {:.1f}".format(game.time),
    ]
    for i, text in enumerate(lines):
        screen.blit(font.render(text, True, WHITE), (12, 10 + i * 20))

    if game.over:
        label = font.render("EPISODE OVER  -  press R", True, MUTED)
        rect = label.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(label, rect)
