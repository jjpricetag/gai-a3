import pygame

from .env import GridWorld
from .sprites import get_sprites
from .ui import Button

COL_BG = (25, 28, 34)
COL_GRID = (45, 50, 58)
COL_TEXT = (240, 240, 240)
CHEST_OPENED_ALPHA = 110
COL_PANEL_BG = (18, 20, 25)
COL_PANEL_BORDER = (55, 60, 70)
COL_OVERLAY = (15, 16, 20, 210)
COL_VICTORY_TEXT = (255, 210, 90)

# Fire flickers on wall-clock time rather than env.step_count, so it keeps
# animating even while nothing is stepping the environment (e.g. a human
# player standing still).
FIRE_FRAME_DURATION_MS = 100

HUD_PANEL_WIDTH = 300
# Sized for the worst case: title + algorithm/mode + episode/step/epsilon +
# apples/chests/keys/monsters + return + last-episode + rolling stats (4
# lines) + controls, with blank-line spacers between groups - about 23 lines.
HUD_PANEL_MIN_HEIGHT = 560
HUD_LINE_HEIGHT = 22
HUD_PADDING = 14

# Upscaling tiles much beyond this starts looking visibly soft (sprites are
# natively 64px), so short grids fill most - but not all - of the panel's
# height rather than getting blurry.
MAX_TILE_SIZE = 128


def effective_tile_size(grid_height_tiles: int, base_tile_size: int) -> int:
    """Scales the configured tile size up so the grid's rendered height fills
    the HUD panel's height instead of leaving dead space below a short grid
    (e.g. Level 1's 4-row cliff walk). Never scales down below the configured
    size, and never past MAX_TILE_SIZE (upscaling sprites further just blurs
    them without meaningfully filling more space)."""
    if grid_height_tiles <= 0:
        return base_tile_size
    filled = HUD_PANEL_MIN_HEIGHT // grid_height_tiles
    return max(base_tile_size, min(filled, MAX_TILE_SIZE))


def window_size_for(grid_width_tiles: int, grid_height_tiles: int, tile_size: int):
    """Total window size needed for the grid plus the HUD side panel."""
    width = grid_width_tiles * tile_size + HUD_PANEL_WIDTH
    height = max(grid_height_tiles * tile_size, HUD_PANEL_MIN_HEIGHT)
    return width, height


def draw_grid(screen, font, tile_size, env: GridWorld, hud_lines, flip=True):
    screen.fill(COL_BG)
    sprites = get_sprites(tile_size)

    for x in range(env.w):
        for y in range(env.h):
            pygame.draw.rect(
                screen, COL_GRID,
                pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size), 1,
            )

    def top_left(p):
        return p[0] * tile_size, p[1] * tile_size

    for p in env.rocks:
        screen.blit(sprites["rock"], top_left(p))

    fire_frames = sprites["fire"]
    fire_frame = fire_frames[(pygame.time.get_ticks() // FIRE_FRAME_DURATION_MS) % len(fire_frames)]
    for p in env.fires:
        screen.blit(fire_frame, top_left(p))

    for p in env.keys_remaining:
        screen.blit(sprites["key"], top_left(p))

    for p, idx in env.chest_index.items():
        opened = not ((env.chest_mask >> idx) & 1)
        chest_img = sprites["chest"]
        if opened:
            chest_img = chest_img.copy()
            chest_img.set_alpha(CHEST_OPENED_ALPHA)
        screen.blit(chest_img, top_left(p))

    for p, idx in env.apple_index.items():
        if (env.apple_mask >> idx) & 1:
            screen.blit(sprites["apple"], top_left(p))

    for p in env.monster_positions:
        screen.blit(sprites["monster"], top_left(p))

    walk_frames = sprites["walk"]
    frame = walk_frames[env.step_count % len(walk_frames)]
    screen.blit(frame, top_left(env.agent))

    draw_hud_panel(screen, font, env.w * tile_size, hud_lines)
    if flip:
        pygame.display.flip()


def draw_victory_overlay(screen, big_font, btn_font) -> Button:
    """Greys out the whole window, shows 'VICTORY' centered, and a Restart
    button below it. Returns the Button so the caller can hit-test clicks
    against it. Call after draw_grid(..., flip=False) so only one frame gets
    presented, then flip once yourself after this returns."""
    screen_w, screen_h = screen.get_size()

    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill(COL_OVERLAY)
    screen.blit(overlay, (0, 0))

    text_surf = big_font.render("VICTORY", True, COL_VICTORY_TEXT)
    text_rect = text_surf.get_rect(center=(screen_w // 2, screen_h // 2 - 40))
    screen.blit(text_surf, text_rect)

    btn_rect = pygame.Rect(0, 0, 200, 50)
    btn_rect.center = (screen_w // 2, screen_h // 2 + 40)
    restart_btn = Button(btn_rect, "Restart")
    restart_btn.draw(screen, btn_font)

    return restart_btn


def draw_summary_screen(screen, title_font, line_font, btn_font, title_text, stat_lines,
                         button_label="Back to Menu") -> Button:
    """Greys out the whole window and shows a title, a block of stat lines
    (centered as a group, one per line), and a button below them. Returns the
    Button so the caller can hit-test clicks. Caller must flip the display
    afterwards."""
    screen_w, screen_h = screen.get_size()

    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill(COL_OVERLAY)
    screen.blit(overlay, (0, 0))

    line_surfs = [line_font.render(t, True, COL_TEXT) if t else None for t in stat_lines]
    line_h = line_font.get_linesize()
    block_h = len(stat_lines) * line_h
    title_surf = title_font.render(title_text, True, COL_VICTORY_TEXT)

    top = screen_h // 2 - (title_surf.get_height() + 20 + block_h + 20 + 50) // 2
    screen.blit(title_surf, title_surf.get_rect(midtop=(screen_w // 2, top)))

    y = top + title_surf.get_height() + 20
    for surf in line_surfs:
        if surf is not None:
            screen.blit(surf, surf.get_rect(midtop=(screen_w // 2, y)))
        y += line_h

    btn_rect = pygame.Rect(0, 0, 220, 50)
    btn_rect.center = (screen_w // 2, y + 20 + 25)
    btn = Button(btn_rect, button_label)
    btn.draw(screen, btn_font)

    return btn


def draw_hud_panel(screen, font, panel_x, hud_lines):
    """Draws the HUD as a sidebar to the right of the grid, one stat per line."""
    screen_w, screen_h = screen.get_size()
    panel_rect = pygame.Rect(panel_x, 0, screen_w - panel_x, screen_h)
    pygame.draw.rect(screen, COL_PANEL_BG, panel_rect)
    pygame.draw.line(screen, COL_PANEL_BORDER, (panel_x, 0), (panel_x, screen_h), 2)

    x = panel_x + HUD_PADDING
    y = HUD_PADDING
    for line in hud_lines:
        if line:
            screen.blit(font.render(line, True, COL_TEXT), (x, y))
        y += HUD_LINE_HEIGHT
