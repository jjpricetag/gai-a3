#!/usr/bin/env python3
"""Headless training run that logs per-episode return to a CSV, for report
evidence (training curves). Runs at full speed - no rendering, no window
needed.

Examples:
  python run_experiment.py --level 1 --algorithm qlearning --out logs/level1_qlearning.csv
  python run_experiment.py --level 1 --algorithm sarsa --out logs/level1_sarsa.csv
"""
import argparse
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

from gridworld.config import load_config
from gridworld.env import GridWorld
from gridworld.levels import get_level
from gridworld.logging_utils import EpisodeLogger
from gridworld.train import run_training


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--level", type=int, required=True)
    parser.add_argument("--algorithm", choices=["qlearning", "sarsa"], required=True)
    parser.add_argument("--episodes", type=int, default=None, help="override config episodes")
    parser.add_argument("--out", required=True, help="CSV output path")
    parser.add_argument("--no-intrinsic", action="store_true", help="disable intrinsic reward for level 6")
    args = parser.parse_args()

    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
    cfg = load_config(f"config_level{args.level}.json", config_dir)
    if args.episodes is not None:
        cfg["episodes"] = args.episodes
    random.seed(int(cfg["seed"]))

    pygame.init()
    layout = get_level(args.level)
    tile_size = int(cfg["tileSize"])
    screen = pygame.display.set_mode((len(layout[0]) * tile_size, len(layout) * tile_size))
    # Create a dummy font that won't be used in headless mode
    class DummyFont:
        def render(self, text, *args, **kwargs):
            return pygame.Surface((0, 0))
    font = DummyFont()
    clock = pygame.time.Clock()

    env = GridWorld(layout)
    logger = EpisodeLogger()

    # Intrinsic reward is ON by default for level 6, unless --no-intrinsic flag is set
    use_intrinsic_reward = (args.level == 6 and not args.no_intrinsic)

    run_training(
        env, cfg, screen, clock, font,
        title=f"Level {args.level}",
        algorithm=args.algorithm,
        render=False,
        episode_callback=logger.record,
        use_intrinsic_reward=use_intrinsic_reward,
    )
    pygame.quit()

    logger.save_csv(args.out)
    suffix = " (with intrinsic reward)" if args.no_intrinsic and args.level == 6 else ""
    print(f"Saved {len(logger.episodes)} episodes to {args.out}{suffix}")


if __name__ == "__main__":
    main()
