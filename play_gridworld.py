#!/usr/bin/env python3
"""GridWorld RL - main menu.

Title screen -> Play / Exit. Play -> pick a level -> pick a mode (whichever
algorithm(s) the level supports, plus "Play (WASD)" to control the agent
yourself) -> runs in its own window.
"""
import os
import random

import pygame

from gridworld.config import load_config
from gridworld.env import GridWorld
from gridworld.levels import LEVELS, get_level
from gridworld.render import effective_tile_size, window_size_for
from gridworld.train import run_human_play, run_training
from gridworld.ui import Button


def get_font(size, bold=False):
    """pygame's bundled default font - always available, no OS font-lookup
    issues (unlike SysFont, which can resolve to a broken .ttc font on some
    Windows setups and render every glyph as a solid black box)."""
    font = pygame.font.Font(None, size)
    font.set_bold(bold)
    return font

MENU, LEVEL_SELECT, MODE_SELECT = "menu", "level_select", "mode_select"

WINDOW_SIZE = (640, 520)
NUM_LEVEL_BUTTONS = 7
COL_BG = (25, 28, 34)
COL_TEXT = (240, 240, 240)

# Levels 0 and 1 use one fixed algorithm per the spec (Task 1 / Task 2).
# Levels 2-3 let you pick either, to compare them (Task 3).
# Levels 4-6 are Task 4 & 5 (monsters and intrinsic reward).
LEVEL_FIXED_ALGORITHM = {0: "qlearning", 1: "sarsa", 4: "qlearning", 5: "qlearning"}
LEVEL_TITLES = {
    0: "Level 0 - Q-Learning",
    1: "Level 1 - SARSA",
    2: "Level 2 - Key & Chest",
    3: "Level 3 - Key & Chest+",
    4: "Level 4 - Monster (Simple)",
    5: "Level 5 - Monster (Complex)",
    6: "Level 6 - Intrinsic Reward",
}


def _setup_level(level_id: int, caption_suffix: str):
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    cfg = load_config(f"config_level{level_id}.json", config_dir)
    random.seed(int(cfg["seed"]))

    layout = get_level(level_id)
    width_tiles, height_tiles = len(layout[0]), len(layout)
    # Scale the tile size (and therefore every sprite) up so the grid fills
    # the same vertical space as the HUD sidebar, instead of the sidebar
    # dwarfing a small grid left tiny in the corner.
    cfg["tileSize"] = effective_tile_size(height_tiles, int(cfg["tileSize"]))

    screen = pygame.display.set_mode(window_size_for(width_tiles, height_tiles, cfg["tileSize"]))
    pygame.display.set_caption(f"GridWorld - {LEVEL_TITLES[level_id]} ({caption_suffix})")
    font = get_font(18)
    env = GridWorld(layout)
    return cfg, env, screen, font


def run_level(level_id: int, algorithm: str, clock) -> bool:
    """Launches training for a level. Returns True if the user closed the window."""
    cfg, env, screen, font = _setup_level(level_id, algorithm)
    return run_training(
        env, cfg, screen, clock, font,
        title=LEVEL_TITLES[level_id],
        algorithm=algorithm,
    )


def run_human_level(level_id: int, clock) -> bool:
    """Launches human WASD play for a level. Returns True if the user closed the window."""
    cfg, env, screen, font = _setup_level(level_id, "Human Play")
    return run_human_play(env, cfg, screen, clock, font, title=LEVEL_TITLES[level_id])


def draw_menu(screen, font_title, play_btn, exit_btn, font_btn):
    screen.fill(COL_BG)
    title_surf = font_title.render("GridWorld RL", True, COL_TEXT)
    screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_SIZE[0] // 2, 120)))
    play_btn.draw(screen, font_btn)
    exit_btn.draw(screen, font_btn)
    pygame.display.flip()


def draw_buttons_screen(screen, font_title, font_btn, title_text, buttons, back_btn):
    screen.fill(COL_BG)
    title_surf = font_title.render(title_text, True, COL_TEXT)
    screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_SIZE[0] // 2, 55)))
    for btn in buttons:
        btn.draw(screen, font_btn)
    back_btn.draw(screen, font_btn)
    pygame.display.flip()


MODE_LABELS = {"qlearning": "Q-Learning", "sarsa": "SARSA", "human": "Play (WASD)"}


def build_mode_buttons(level_id):
    """Q-learning/SARSA (whichever the level supports) plus human Play, always."""
    modes = [LEVEL_FIXED_ALGORITHM[level_id]] if level_id in LEVEL_FIXED_ALGORITHM else ["qlearning", "sarsa"]
    modes.append("human")
    buttons = [
        (Button(pygame.Rect(220, 160 + i * 65, 200, 50), MODE_LABELS[mode]), mode)
        for i, mode in enumerate(modes)
    ]
    back_btn = Button(pygame.Rect(220, 160 + len(modes) * 65 + 15, 200, 50), "Back")
    return buttons, back_btn


def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("GridWorld RL")
    clock = pygame.time.Clock()
    font_title = get_font(32, bold=True)
    font_btn = get_font(18)

    play_btn = Button(pygame.Rect(220, 220, 200, 50), "Play")
    exit_btn = Button(pygame.Rect(220, 290, 200, 50), "Exit")

    level_buttons = []
    for i in range(NUM_LEVEL_BUTTONS):
        enabled = i in LEVELS
        label = LEVEL_TITLES.get(i, f"Level {i}") + ("" if enabled else " (Soon)")
        rect = pygame.Rect(170, 100 + i * 50, 300, 40)
        level_buttons.append(Button(rect, label, enabled=enabled))
    level_back_btn = Button(pygame.Rect(170, 100 + NUM_LEVEL_BUTTONS * 50 + 15, 300, 40), "Back")

    state = MENU
    selected_level = None
    mode_buttons, mode_back_btn = [], None
    running = True
    while running:
        if state == MENU:
            draw_menu(screen, font_title, play_btn, exit_btn, font_btn)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if play_btn.is_clicked(event.pos):
                        state = LEVEL_SELECT
                    elif exit_btn.is_clicked(event.pos):
                        running = False
            clock.tick(30)

        elif state == LEVEL_SELECT:
            draw_buttons_screen(screen, font_title, font_btn, "Select Level", level_buttons, level_back_btn)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if level_back_btn.is_clicked(event.pos):
                        state = MENU
                    else:
                        for i, btn in enumerate(level_buttons):
                            if btn.is_clicked(event.pos):
                                selected_level = i
                                mode_buttons, mode_back_btn = build_mode_buttons(i)
                                state = MODE_SELECT
            clock.tick(30)

        elif state == MODE_SELECT:
            draw_buttons_screen(
                screen, font_title, font_btn,
                LEVEL_TITLES.get(selected_level, f"Level {selected_level}"),
                [btn for btn, _ in mode_buttons], mode_back_btn,
            )
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if mode_back_btn.is_clicked(event.pos):
                        state = LEVEL_SELECT
                    else:
                        for btn, mode in mode_buttons:
                            if btn.is_clicked(event.pos):
                                if mode == "human":
                                    quit_requested = run_human_level(selected_level, clock)
                                else:
                                    quit_requested = run_level(selected_level, mode, clock)
                                if quit_requested:
                                    running = False
                                else:
                                    screen = pygame.display.set_mode(WINDOW_SIZE)
                                    pygame.display.set_caption("GridWorld RL")
                                    state = LEVEL_SELECT
            clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
