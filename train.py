import argparse
import os

from stable_baselines3 import DQN, PPO
from stable_baselines3.common.monitor import Monitor

from arena.config import load_config, save_config
from arena.env import ArenaEnv
from arena.watch import WatchCallback

ALGOS = {"ppo": PPO, "dqn": DQN}
CONFIG_DIR = "config"
MODEL_DIR = "models"
LOG_DIR = "logs"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default=None)
    p.add_argument("--style", default=None, choices=("rotation", "direct"))
    p.add_argument("--algo", default=None, choices=("ppo", "dqn"))
    p.add_argument("--timesteps", type=int, default=None)
    p.add_argument("--learning-rate", type=float, default=None)
    p.add_argument("--ent-coef", type=float, default=None)
    p.add_argument("--n-steps", type=int, default=None)
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--gamma", type=float, default=None)
    p.add_argument("--net-arch", default=None)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--tag", default=None)
    p.add_argument("--watch", type=int, default=0)
    p.add_argument("--render-train", action="store_true")
    p.add_argument("--render-fps", type=int, default=0)
    return p.parse_args()


def resolve(args):
    cfg = load_config(args.config or "arena_ppo_rotation.json", CONFIG_DIR)
    overrides = {
        "style": args.style,
        "algo": args.algo,
        "timesteps": args.timesteps,
        "learningRate": args.learning_rate,
        "entCoef": args.ent_coef,
        "nSteps": args.n_steps,
        "batchSize": args.batch_size,
        "gamma": args.gamma,
        "seed": args.seed,
    }
    for key, value in overrides.items():
        if value is not None:
            cfg[key] = value
    if args.net_arch is not None:
        cfg["netArch"] = [int(n) for n in args.net_arch.split(",")]
    return cfg


def main():
    args = parse_args()
    cfg = resolve(args)
    run = args.tag or "{}_{}".format(cfg["algo"], cfg["style"])

    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    env = Monitor(ArenaEnv(control_style=cfg["style"], seed=cfg["seed"],
                           render_mode="human" if args.render_train else None,
                           render_fps=args.render_fps or None))

    kwargs = {
        "policy": "MlpPolicy",
        "env": env,
        "verbose": 1,
        "seed": cfg["seed"],
        "gamma": cfg["gamma"],
        "learning_rate": cfg["learningRate"],
        "tensorboard_log": LOG_DIR,
        "policy_kwargs": {"net_arch": cfg["netArch"]},
    }
    if cfg["algo"] == "ppo":
        kwargs["n_steps"] = cfg["nSteps"]
        kwargs["batch_size"] = cfg["batchSize"]
        kwargs["ent_coef"] = cfg["entCoef"]

    callback = None
    if args.watch > 0:
        callback = WatchCallback(cfg["style"], args.watch, cfg["seed"])

    model = ALGOS[cfg["algo"]](**kwargs)
    model.learn(total_timesteps=cfg["timesteps"], tb_log_name=run,
                callback=callback)

    path = os.path.join(MODEL_DIR, run)
    model.save(path)
    save_config(cfg, path + ".json")
    env.close()
    print("saved {}.zip and {}.json".format(path, path))


if __name__ == "__main__":
    main()
