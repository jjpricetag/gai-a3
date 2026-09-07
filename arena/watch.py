from stable_baselines3.common.callbacks import BaseCallback

from arena.env import ArenaEnv


class WatchCallback(BaseCallback):
    def __init__(self, control_style, every, seed=0, verbose=0):
        super().__init__(verbose)
        self.control_style = control_style
        self.every = every
        self.seed = seed
        self._env = None
        self._next = every

    def _on_step(self):
        if self.num_timesteps < self._next:
            return True
        self._next += self.every

        if self._env is None:
            self._env = ArenaEnv(control_style=self.control_style,
                                 render_mode="human", seed=self.seed)

        obs, _ = self._env.reset(seed=self.seed)
        total, steps = 0.0, 0
        while True:
            action, _ = self.model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = self._env.step(action)
            total += reward
            steps += 1
            if terminated or truncated:
                break
        print("[watch] {:>7} steps  return {:>7.2f}  length {:>4}  phase {}".format(
            self.num_timesteps, total, steps, info["phase"]))
        return True

    def _on_training_end(self):
        if self._env is not None:
            self._env.close()
            self._env = None
