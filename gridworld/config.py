import json
import os

DEFAULT_CFG = {
    "episodes": 800,
    "alpha": 0.2,
    "gamma": 0.95,
    "epsilonStart": 1.0,
    "epsilonEnd": 0.05,
    "epsilonDecayEpisodes": 700,
    "maxStepsPerEpisode": 400,
    "fpsVisual": 30,
    "fpsFast": 240,
    "tileSize": 48,
    "seed": 42,
}


def load_config(config_filename: str, base_dir: str) -> dict:
    cfg = DEFAULT_CFG.copy()
    path = os.path.join(base_dir, config_filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
        print(f"Loaded {config_filename}")
    return cfg
