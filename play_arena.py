import pygame as pg

from arena.game import Game
from arena.render import draw
from arena.settings import DT, FPS, HEIGHT, WIDTH


def read_input():
    keys = pg.key.get_pressed()
    move_x = 0.0
    move_y = 0.0
    if keys[pg.K_a] or keys[pg.K_LEFT]:
        move_x -= 1.0
    if keys[pg.K_d] or keys[pg.K_RIGHT]:
        move_x += 1.0
    if keys[pg.K_w] or keys[pg.K_UP]:
        move_y -= 1.0
    if keys[pg.K_s] or keys[pg.K_DOWN]:
        move_y += 1.0
    shooting = keys[pg.K_SPACE]
    return move_x, move_y, shooting, pg.mouse.get_pos()


def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Arena")
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

        move_x, move_y, shooting, aim = read_input()
        game.update(DT, move_x, move_y, shooting, aim)

        draw(screen, font, game)
        pg.display.flip()
        clock.tick(FPS)

    pg.quit()


if __name__ == "__main__":
    main()
