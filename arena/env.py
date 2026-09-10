import math

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from arena.game import Game
from arena.settings import (
    ACTION_REPEAT, DT, FPS, HEIGHT, MAX_EPISODE_SECONDS, MAX_EPISODE_STEPS,
    OBS_SIZE, PHASE_OBS_SCALE, PHASE_SPAWNERS_MAX, PLAYER_MAX_SPEED,
    REWARD_DAMAGE, REWARD_DEATH, REWARD_ENEMY, REWARD_HIT, REWARD_PHASE,
    REWARD_SPAWNER, REWARD_SPAWNER_HIT, REWARD_STEP, SHOOT_COOLDOWN,
    WIDTH,
)

DIAGONAL = math.hypot(WIDTH, HEIGHT)

ROTATION_ACTIONS = ("noop", "thrust", "rotate_left", "rotate_right", "shoot")
DIRECT_ACTIONS = ("noop", "up", "down", "left", "right", "shoot")

TRACKED = ("enemies_killed", "spawners_killed", "phase_advanced",
           "damage_taken", "hits_landed", "spawner_hits", "aimed_shots",
           "aim_alignment", "shots_fired")


class ArenaEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": FPS}

    DEFAULT_REWARDS = {
        "rewardStep": REWARD_STEP,
        "rewardHit": REWARD_HIT,
        "rewardSpawnerHit": REWARD_SPAWNER_HIT,
        "rewardAim": 0.0,
        "rewardEnemy": REWARD_ENEMY,
        "rewardSpawner": REWARD_SPAWNER,
        "rewardPhase": REWARD_PHASE,
        "rewardDamage": REWARD_DAMAGE,
        "rewardDeath": REWARD_DEATH,
    }

    def __init__(self, control_style="rotation", render_mode=None, seed=None,
                 rewards=None, aim_target="nearest"):
        super().__init__()
        if control_style not in ("rotation", "direct"):
            raise ValueError("control_style must be 'rotation' or 'direct'")
        if aim_target not in ("nearest", "spawner"):
            raise ValueError("aim_target must be 'nearest' or 'spawner'")

        self.control_style = control_style
        self.actions = (ROTATION_ACTIONS if control_style == "rotation"
                        else DIRECT_ACTIONS)
        self.render_mode = render_mode
        self.rewards = dict(self.DEFAULT_REWARDS)
        if rewards:
            self.rewards.update({k: v for k, v in rewards.items()
                                 if k in self.DEFAULT_REWARDS})

        self.game = Game(seed=seed, aim_target=aim_target)
        self.steps = 0
        self.overlay = None

        self._screen = None
        self._font = None
        self._clock = None

        self.observation_space = spaces.Box(low=-1.0, high=1.0,
                                            shape=(OBS_SIZE,), dtype=np.float32)
        self.action_space = spaces.Discrete(len(self.actions))

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            self.game.rng.seed(seed)
        self.game.reset()
        self.steps = 0
        return self._observe(), {}

    def step(self, action):
        inputs = self._inputs(int(action))
        totals = dict.fromkeys(TRACKED, 0)

        for _ in range(ACTION_REPEAT):
            self.game.update(DT, **inputs)
            for key in TRACKED:
                totals[key] += self.game.events.get(key, 0)
            if self.render_mode == "human":
                self.render()
            if self.game.over:
                break

        self.steps += 1
        terminated = self.game.player.hp <= 0
        truncated = (not terminated) and (self.game.over
                                          or self.steps >= MAX_EPISODE_STEPS)
        reward = self._reward(totals, terminated)

        info = dict(totals)
        info["phase"] = self.game.phase
        info["time"] = self.game.time

        return self._observe(), reward, terminated, truncated, info

    def _inputs(self, action):
        name = self.actions[action]
        if self.control_style == "rotation":
            return {
                "rotate": -1.0 if name == "rotate_left" else
                          1.0 if name == "rotate_right" else 0.0,
                "thrust": name == "thrust",
                "shoot": name == "shoot",
            }
        move = {"up": (0.0, -1.0), "down": (0.0, 1.0),
                "left": (-1.0, 0.0), "right": (1.0, 0.0)}.get(name, (0.0, 0.0))
        return {"move": move, "shoot": name == "shoot"}

    def _reward(self, totals, terminated):
        r = self.rewards
        reward = r["rewardStep"]
        reward += r["rewardAim"] * totals["aim_alignment"]
        reward += r["rewardHit"] * totals["hits_landed"]
        reward += r["rewardSpawnerHit"] * totals["spawner_hits"]
        reward += r["rewardEnemy"] * totals["enemies_killed"]
        reward += r["rewardSpawner"] * totals["spawners_killed"]
        reward += r["rewardPhase"] * totals["phase_advanced"]
        reward += r["rewardDamage"] * totals["damage_taken"]
        if terminated:
            reward += r["rewardDeath"]
        return float(reward)

    def _relative(self, target):
        if target is None:
            return 0.0, 0.0, 1.0
        dx = (target.x - self.game.player.x) / WIDTH
        dy = (target.y - self.game.player.y) / HEIGHT
        dist = math.hypot(target.x - self.game.player.x,
                          target.y - self.game.player.y) / DIAGONAL
        return dx, dy, dist

    def _observe(self):
        p = self.game.player
        enemy_dx, enemy_dy, enemy_dist = self._relative(self.game.nearest_enemy())
        spawn_dx, spawn_dy, spawn_dist = self._relative(self.game.nearest_spawner())

        obs = np.array([
            p.x / WIDTH * 2.0 - 1.0,
            p.y / HEIGHT * 2.0 - 1.0,
            p.vx / PLAYER_MAX_SPEED,
            p.vy / PLAYER_MAX_SPEED,
            math.sin(p.angle),
            math.cos(p.angle),
            p.hp / p.max_hp,
            enemy_dx,
            enemy_dy,
            enemy_dist,
            spawn_dx,
            spawn_dy,
            spawn_dist,
            len(self.game.enemies) / self.game.max_enemies(),
            len(self.game.spawners) / PHASE_SPAWNERS_MAX,
            min(self.game.phase / PHASE_OBS_SCALE, 1.0),
            p.cooldown / SHOOT_COOLDOWN,
            1.0 - self.game.time / MAX_EPISODE_SECONDS,
        ], dtype=np.float32)

        return np.clip(obs, -1.0, 1.0)

    def render(self):
        if self.render_mode != "human":
            return
        import pygame as pg

        from arena.render import draw, draw_overlay

        if self._screen is None:
            pg.init()
            self._screen = pg.display.set_mode((WIDTH, HEIGHT))
            pg.display.set_caption("Arena - {}".format(self.control_style))
            self._font = pg.font.SysFont("consolas", 16)
            self._clock = pg.time.Clock()

        pg.event.pump()
        draw(self._screen, self._font, self.game)
        if self.overlay is not None:
            draw_overlay(self._screen, self._font, self.game, self.overlay)
        pg.display.flip()
        self._clock.tick(FPS)

    def close(self):
        if self._screen is not None:
            import pygame as pg
            pg.display.quit()
            pg.quit()
            self._screen = None
