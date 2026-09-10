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
    "aimTarget": "nearest",
    "rewardStep": -0.01,
    "rewardHit": 0.0,
    "rewardSpawnerHit": 0.0,
    "rewardAim": 0.0,
    "rewardEnemy": 1.0,
    "rewardSpawner": 5.0,
    "rewardPhase": 10.0,
    "rewardDamage": -1.0,
    "rewardDeath": -10.0,
}


def load_config(config_filename, base_dir):
    path = os.path.join(base_dir, config_filename)
    if not os.path.exists(path):
        raise SystemExit("config not found: {}".format(path))

    with open(path, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    unknown = sorted(set(loaded) - set(DEFAULT_CFG))
    if unknown:
        raise SystemExit("unknown keys in {}: {}".format(config_filename,
                                                         ", ".join(unknown)))

    cfg = DEFAULT_CFG.copy()
    cfg.update(loaded)
    print("Loaded {}".format(config_filename))
    return cfg


def save_config(cfg, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
