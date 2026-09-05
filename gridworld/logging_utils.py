import csv
import os


class EpisodeLogger:
    """Collects one row per training episode; write it out for report evidence."""

    def __init__(self):
        self.episodes = []
        self.env_returns = []
        self.total_returns = []
        self.steps = []
        self.epsilons = []

    def record(self, episode, env_return, total_return, steps, epsilon):
        self.episodes.append(episode)
        self.env_returns.append(env_return)
        self.total_returns.append(total_return)
        self.steps.append(steps)
        self.epsilons.append(epsilon)

    def save_csv(self, path):
        out_dir = os.path.dirname(path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["episode", "env_return", "total_return", "steps", "epsilon"])
            for row in zip(self.episodes, self.env_returns, self.total_returns, self.steps, self.epsilons):
                writer.writerow(row)
