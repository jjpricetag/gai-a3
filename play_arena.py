import sys

import pygame as pg

from arena.game import Game
from arena.render import draw
from arena.settings import DT, FPS, HEIGHT, WIDTH


def read_rotation():
    keys = pg.key.get_pressed()
    rotate = 0.0
    if keys[pg.K_a] or keys[pg.K_LEFT]:
        rotate -= 1.0
    if keys[pg.K_d] or keys[pg.K_RIGHT]:
        rotate += 1.0
    thrust = keys[pg.K_w] or keys[pg.K_UP]
    return {"rotate": rotate, "thrust": thrust, "shoot": keys[pg.K_SPACE]}


def read_direct():
    keys = pg.key.get_pressed()
    dx = dy = 0.0
    if keys[pg.K_a] or keys[pg.K_LEFT]:
        dx -= 1.0
    if keys[pg.K_d] or keys[pg.K_RIGHT]:
        dx += 1.0
    if keys[pg.K_w] or keys[pg.K_UP]:
        dy -= 1.0
    if keys[pg.K_s] or keys[pg.K_DOWN]:
        dy += 1.0
    return {"move": (dx, dy), "shoot": keys[pg.K_SPACE]}


def main():
    style = "direct" if "--style" in sys.argv and "direct" in sys.argv else "rotation"

    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Arena - {}".format(style))
    clock = pg.time.Clock()
    font = pg.font.SysFont("consolas", 16)

    game = Game()
    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                elif event.key == pg.K_r:
                    game.reset()

        inputs = read_direct() if style == "direct" else read_rotation()
        game.update(DT, **inputs)

        draw(screen, font, game)
        pg.display.flip()
        clock.tick(FPS)

    pg.quit()


if __name__ == "__main__":
    main()
