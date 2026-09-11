import pygame

from .env import GridWorld

COL_BG = (25, 28, 34)
COL_GRID = (45, 50, 58)
COL_AGENT = (74, 222, 128)
COL_APPLE = (252, 92, 101)
COL_TEXT = (240, 240, 240)
COL_ROCK = (110, 114, 122)
COL_FIRE = (247, 140, 40)
COL_KEY = (250, 204, 60)
COL_CHEST_CLOSED = (168, 110, 48)
COL_CHEST_OPEN = (70, 66, 60)
COL_MONSTER = (200, 50, 200)


def draw_grid(screen, font, tile_size, env: GridWorld, hud_lines, v_button=None, r_button=None, back_button=None):
    screen.fill(COL_BG)

    for x in range(env.w):
        for y in range(env.h):
            pygame.draw.rect(
                screen, COL_GRID,
                pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size), 1,
            )

    def center(p):
        return p[0] * tile_size + tile_size // 2, p[1] * tile_size + tile_size // 2

    for p in env.rocks:
        r = tile_size - 6
        rect = pygame.Rect(0, 0, r, r)
        rect.center = center(p)
        pygame.draw.rect(screen, COL_ROCK, rect, border_radius=4)

    for p in env.fires:
        cx, cy = center(p)
        pts = [(cx, cy - tile_size // 3), (cx - tile_size // 3, cy + tile_size // 3),
               (cx + tile_size // 3, cy + tile_size // 3)]
        pygame.draw.polygon(screen, COL_FIRE, pts)

    for p in env.keys_remaining:
        cx, cy = center(p)
        pygame.draw.circle(screen, COL_KEY, (cx, cy), tile_size // 5)

    for p, idx in env.chest_index.items():
        opened = not ((env.chest_mask >> idx) & 1)
        color = COL_CHEST_OPEN if opened else COL_CHEST_CLOSED
        r = tile_size - 12
        rect = pygame.Rect(0, 0, r, r)
        rect.center = center(p)
        pygame.draw.rect(screen, color, rect, border_radius=3)

    for p, idx in env.apple_index.items():
        if (env.apple_mask >> idx) & 1:
            cx, cy = center(p)
            pygame.draw.circle(screen, COL_APPLE, (cx, cy), tile_size // 3)

    for p in env.monster_positions:
        cx, cy = center(p)
        pygame.draw.circle(screen, COL_MONSTER, (cx, cy), tile_size // 3)

    ax, ay = env.agent
    pygame.draw.rect(
        screen, COL_AGENT,
        (ax * tile_size + 8, ay * tile_size + 8, tile_size - 16, tile_size - 16),
        border_radius=6,
    )

    for i, t in enumerate(hud_lines):
        screen.blit(font.render(t, True, COL_TEXT), (10, 8 + i * 20))

    if v_button:
        v_button.draw(screen, font)
    if r_button:
        r_button.draw(screen, font)
    if back_button:
        back_button.draw(screen, font)

    pygame.display.flip()
