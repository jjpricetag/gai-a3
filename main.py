#!/usr/bin/env python3
"""GridWorld RL - main menu.

Title screen -> Play / Exit. Play -> pick a level -> (if the level supports
both algorithms) pick Q-Learning or SARSA -> training runs in its own window.
"""
import os
import random

import pygame

from gridworld.config import load_config
from gridworld.env import GridWorld
from gridworld.levels import LEVELS, get_level
from gridworld.train import run_training
from gridworld.ui import Button

MENU, LEVEL_SELECT, ALGO_SELECT = "menu", "level_select", "algo_select"

WINDOW_SIZE = (640, 560)
NUM_LEVEL_BUTTONS = 7
COL_BG = (25, 28, 34)
COL_TEXT = (240, 240, 240)

# Levels 0 and 1 use one fixed algorithm per the spec (Task 1 / Task 2).
# Levels 2-6 let you pick either, to compare them (Task 3/4/5).
LEVEL_FIXED_ALGORITHM = {0: "qlearning", 1: "sarsa"}
LEVEL_TITLES = {
    0: "Level 0 - Q-Learning",
    1: "Level 1 - SARSA",
    2: "Level 2 - Key & Chest",
    3: "Level 3 - Key & Chest+",
    4: "Level 4 - Monsters",
    5: "Level 5 - Monsters+",
    6: "Level 6 - Intrinsic Reward",
}
# Level 6 defaults to using intrinsic reward; every level can still override
# this via its own config file's "useIntrinsicReward" key.
LEVEL_INTRINSIC_DEFAULT = {6: True}


def run_level(level_id: int, algorithm: str, clock) -> bool:
    """Launches training for a level. Returns True if the user closed the window."""
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    cfg = load_config(f"config_level{level_id}.json", config_dir)
    random.seed(int(cfg["seed"]))

    layout = get_level(level_id)
    tile_size = int(cfg["tileSize"])
    width_tiles, height_tiles = len(layout[0]), len(layout)

    screen = pygame.display.set_mode((width_tiles * tile_size, height_tiles * tile_size))
    pygame.display.set_caption(f"GridWorld - {LEVEL_TITLES[level_id]} ({algorithm})")
    font = pygame.font.SysFont("consolas", 18)

    use_intrinsic = bool(cfg.get("useIntrinsicReward", LEVEL_INTRINSIC_DEFAULT.get(level_id, False)))
    intrinsic_strength = float(cfg.get("intrinsicRewardStrength", 1.0))

    env = GridWorld(layout)
    return run_training(
        env, cfg, screen, clock, font,
        title=LEVEL_TITLES[level_id],
        algorithm=algorithm,
        use_intrinsic_reward=use_intrinsic,
        intrinsic_strength=intrinsic_strength,
    )


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


def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("GridWorld RL")
    clock = pygame.time.Clock()
    font_title = pygame.font.SysFont("consolas", 32, bold=True)
    font_btn = pygame.font.SysFont("consolas", 18)

    play_btn = Button(pygame.Rect(220, 220, 200, 50), "Play")
    exit_btn = Button(pygame.Rect(220, 290, 200, 50), "Exit")

    level_buttons = []
    for i in range(NUM_LEVEL_BUTTONS):
        enabled = i in LEVELS
        label = LEVEL_TITLES.get(i, f"Level {i}") + ("" if enabled else " (Soon)")
        rect = pygame.Rect(170, 100 + i * 50, 300, 40)
        level_buttons.append(Button(rect, label, enabled=enabled))
    level_back_btn = Button(pygame.Rect(170, 100 + NUM_LEVEL_BUTTONS * 50 + 15, 300, 40), "Back")

    qlearning_btn = Button(pygame.Rect(220, 220, 200, 50), "Q-Learning")
    sarsa_btn = Button(pygame.Rect(220, 290, 200, 50), "SARSA")
    algo_back_btn = Button(pygame.Rect(220, 360, 200, 50), "Back")

    state = MENU
    selected_level = None
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
                                if i in LEVEL_FIXED_ALGORITHM:
                                    quit_requested = run_level(i, LEVEL_FIXED_ALGORITHM[i], clock)
                                    if quit_requested:
                                        running = False
                                    else:
                                        screen = pygame.display.set_mode(WINDOW_SIZE)
                                        pygame.display.set_caption("GridWorld RL")
                                else:
                                    state = ALGO_SELECT
            clock.tick(30)

        elif state == ALGO_SELECT:
            draw_buttons_screen(
                screen, font_title, font_btn,
                LEVEL_TITLES.get(selected_level, f"Level {selected_level}"),
                [qlearning_btn, sarsa_btn], algo_back_btn,
            )
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if algo_back_btn.is_clicked(event.pos):
                        state = LEVEL_SELECT
                    elif qlearning_btn.is_clicked(event.pos) or sarsa_btn.is_clicked(event.pos):
                        algorithm = "qlearning" if qlearning_btn.is_clicked(event.pos) else "sarsa"
                        quit_requested = run_level(selected_level, algorithm, clock)
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
