import argparse
import statistics

from stable_baselines3 import DQN, PPO

from arena.env import ArenaEnv

ALGOS = {"ppo": PPO, "dqn": DQN}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--style", default="rotation", choices=("rotation", "direct"))
    p.add_argument("--algo", default="ppo", choices=("ppo", "dqn"))
    p.add_argument("--episodes", type=int, default=5)
    p.add_argument("--seed", type=int, default=1000)
    p.add_argument("--no-render", action="store_true")
    p.add_argument("--stochastic", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()
    env = ArenaEnv(control_style=args.style,
                   render_mode=None if args.no_render else "human",
                   seed=args.seed)
    model = ALGOS[args.algo].load(args.model)

    returns, lengths, phases, kills, spawners = [], [], [], [], []

    for ep in range(args.episodes):
        obs, _ = env.reset(seed=args.seed + ep)
        total, steps, killed, destroyed = 0.0, 0, 0, 0
        while True:
            action, _ = model.predict(obs, deterministic=not args.stochastic)
            obs, reward, terminated, truncated, info = env.step(action)
            total += reward
            steps += 1
            killed += info["enemies_killed"]
            destroyed += info["spawners_killed"]
            if terminated or truncated:
                break
        returns.append(total)
        lengths.append(steps)
        phases.append(info["phase"])
        kills.append(killed)
        spawners.append(destroyed)
        print("ep {:>2}  return {:>8.2f}  steps {:>4}  phase {}  enemies {:>2}  "
              "spawners {}  {}".format(ep + 1, total, steps, info["phase"],
                                       killed, destroyed,
                                       "died" if terminated else "timeout"))

    env.close()
    print("\nmean over {} episodes".format(args.episodes))
    print("  return   {:.2f} +/- {:.2f}".format(statistics.mean(returns),
                                                statistics.pstdev(returns)))
    print("  length   {:.1f}".format(statistics.mean(lengths)))
    print("  phase    {:.2f}".format(statistics.mean(phases)))
    print("  enemies  {:.1f}".format(statistics.mean(kills)))
    print("  spawners {:.1f}".format(statistics.mean(spawners)))


if __name__ == "__main__":
    main()
