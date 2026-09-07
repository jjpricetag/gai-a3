import json
import os

DEFAULT_CFG = {
    "algo": "ppo",
    "style": "rotation",
    "timesteps": 300000,
    "learningRate": 0.0003,
    "entCoef": 0.0,
    "nSteps": 2048,
    "batchSize": 64,
    "gamma": 0.99,
    "netArch": [64, 64],
    "seed": 0,
}


def load_config(config_filename, base_dir):
    cfg = DEFAULT_CFG.copy()
    path = os.path.join(base_dir, config_filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
        print("Loaded {}".format(config_filename))
    return cfg


def save_config(cfg, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
