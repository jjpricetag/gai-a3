import argparse
import collections
import json
import math
import os
import statistics

import numpy as np
import torch
from stable_baselines3 import DQN, PPO

from arena.env import ArenaEnv

ALGOS = {"ppo": PPO, "dqn": DQN}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--episodes", type=int, default=5)
    p.add_argument("--seed", type=int, default=1000)
    p.add_argument("--no-render", action="store_true")
    p.add_argument("--actions", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()

    cfg = {}
    side = args.model + ".json"
    if os.path.exists(side):
        with open(side, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        print("Loaded {}".format(os.path.basename(side)))

    env = ArenaEnv(control_style=cfg.get("style", "rotation"),
                   render_mode=None if args.no_render else "human",
                   seed=args.seed, rewards=cfg)
    model = ALGOS[cfg.get("algo", "ppo")].load(args.model)

    returns, lengths, phases, kills, spawners, hits = [], [], [], [], [], []
    aimed, shots, aligns = [], [], []
    taken = collections.Counter()
    entropies = []

    for ep in range(args.episodes):
        obs, _ = env.reset(seed=args.seed + ep)
        total, steps, killed, destroyed, landed = 0.0, 0, 0, 0, 0
        on_target, fired, align = 0, 0, 0.0
        while True:
            action, _ = model.predict(obs, deterministic=True)
            taken[env.actions[int(action)]] += 1
            if args.actions:
                with torch.no_grad():
                    obs_t = torch.as_tensor(np.asarray(obs)).unsqueeze(0).float()
                    entropies.append(
                        float(model.policy.get_distribution(obs_t).entropy().item()))
            obs, reward, terminated, truncated, info = env.step(action)
            total += reward
            steps += 1
            killed += info["enemies_killed"]
            destroyed += info["spawners_killed"]
            landed += info["hits_landed"]
            on_target += info["aimed_shots"]
            align += info["aim_alignment"]
            fired += 1 if env.actions[int(action)] == "shoot" else 0
            if terminated or truncated:
                break
        returns.append(total)
        lengths.append(steps)
        phases.append(info["phase"])
        kills.append(killed)
        spawners.append(destroyed)
        hits.append(landed)
        aimed.append(on_target)
        shots.append(fired)
        aligns.append(align / fired if fired else 0.0)
        print("ep {:>2}  return {:>8.2f}  steps {:>4}  phase {}  hits {:>3}  "
              "enemies {:>2}  spawners {}  {}".format(
                  ep + 1, total, steps, info["phase"], landed, killed,
                  destroyed, "died" if terminated else "timeout"))

    env.close()
    print("\nmean over {} episodes".format(args.episodes))
    print("  return   {:.2f} +/- {:.2f}".format(statistics.mean(returns),
                                                statistics.pstdev(returns)))
    print("  length   {:.1f}".format(statistics.mean(lengths)))
    print("  phase    {:.2f}".format(statistics.mean(phases)))
    print("  shots    {:.1f}".format(statistics.mean(shots)))
    print("  on-target{:>6.1f}".format(statistics.mean(aimed)))
    print("  mean aim {:.3f}   (0.32 = random heading, 1.0 = perfect)".format(
        statistics.mean(aligns)))
    print("  hits     {:.1f}".format(statistics.mean(hits)))
    print("  enemies  {:.1f}".format(statistics.mean(kills)))
    print("  spawners {:.1f}".format(statistics.mean(spawners)))

    if args.actions:
        total_steps = sum(taken.values())
        print("\naction distribution over {} steps".format(total_steps))
        for name in env.actions:
            n = taken.get(name, 0)
            print("  {:<14} {:>6}  {:>5.1f}%".format(name, n,
                                                     n / total_steps * 100))
        mean_h = statistics.mean(entropies)
        max_h = math.log(env.action_space.n)
        print("\npolicy entropy  {:.3f}  of max {:.3f}  ({:.0f}%)".format(
            mean_h, max_h, mean_h / max_h * 100))
        print("effective actions  {:.2f} of {}".format(math.exp(mean_h),
                                                       env.action_space.n))


if __name__ == "__main__":
    main()
