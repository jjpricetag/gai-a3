import math

import pygame

from .agents import QTable, epsilon_greedy, linear_epsilon, q_learning_update, sarsa_update
from .env import GridWorld
from .render import draw_grid


def run_training(
    env: GridWorld,
    cfg: dict,
    screen,
    clock,
    font,
    title: str,
    algorithm: str = "qlearning",
    use_intrinsic_reward: bool = False,
    intrinsic_strength: float = 1.0,
    render: bool = True,
    episode_callback=None,
) -> bool:
    """Runs Q-learning or SARSA training for `env`. Returns True if the user closed the window.

    render=False skips all drawing so training runs at full speed (for generating
    report evidence). episode_callback(episode, env_return, total_return, steps,
    epsilon), if given, is called once at the end of each completed episode.
    """
    assert algorithm in ("qlearning", "sarsa")

    episodes = int(cfg["episodes"])
    alpha, gamma = float(cfg["alpha"]), float(cfg["gamma"])
    eps_start, eps_end = float(cfg["epsilonStart"]), float(cfg["epsilonEnd"])
    eps_decay_ep = int(cfg["epsilonDecayEpisodes"])
    max_steps = int(cfg["maxStepsPerEpisode"])
    fps_visual, fps_fast = int(cfg["fpsVisual"]), int(cfg["fpsFast"])
    tile_size = int(cfg["tileSize"])

    qtab = QTable()
    visualize, running = True, True

    for ep in range(episodes):
        s = env.reset()
        visit_counts = {}
        env_return, total_return, steps = 0.0, 0.0, 0
        eps = linear_epsilon(ep, eps_start, eps_end, eps_decay_ep)
        a = epsilon_greedy(qtab, s, eps) if algorithm == "sarsa" else None

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_v:
                        visualize = not visualize
                    if event.key == pygame.K_r:
                        qtab = QTable()
                        s = env.reset()
                        visit_counts = {}
                        env_return, total_return, steps = 0.0, 0.0, 0
                        eps = linear_epsilon(ep, eps_start, eps_end, eps_decay_ep)
                        a = epsilon_greedy(qtab, s, eps) if algorithm == "sarsa" else None
            if not running:
                break

            if algorithm == "qlearning":
                a = epsilon_greedy(qtab, s, eps)
            res = env.step(a)

            reward_for_update = res.reward
            if use_intrinsic_reward:
                n_prior = visit_counts.get(s, 0)
                intrinsic = intrinsic_strength / math.sqrt(n_prior + 1)
                visit_counts[s] = n_prior + 1
                reward_for_update += intrinsic

            if algorithm == "qlearning":
                q_learning_update(qtab, s, a, reward_for_update, res.next_state, alpha, gamma, done=res.done)
                s = res.next_state
            else:  # sarsa
                ap = epsilon_greedy(qtab, res.next_state, eps)
                sarsa_update(qtab, s, a, reward_for_update, res.next_state, ap, alpha, gamma, done=res.done)
                s, a = res.next_state, ap

            env_return += res.reward
            total_return += reward_for_update
            steps += 1

            if render:
                hud_lines = [
                    f"Ep {ep + 1}/{episodes}  step {steps}  eps {eps:.3f}  {algorithm.upper()}",
                    f"Apples left {bin(env.apple_mask).count('1')}"
                    + (f"  Chests left {bin(env.chest_mask).count('1')}" if env.chests else "")
                    + (f"  Keys {env.key_count}" if env.key_positions else ""),
                    f"Return {env_return:.2f}"
                    + (f"  (+intrinsic {total_return:.2f})" if use_intrinsic_reward else "")
                    + f"  {title}",
                    "V toggles fast mode. R resets.",
                ]
                if visualize:
                    draw_grid(screen, font, tile_size, env, hud_lines)
                    clock.tick(fps_visual)
                else:
                    if steps % 5 == 0:
                        draw_grid(screen, font, tile_size, env, hud_lines)
                    clock.tick(fps_fast)

            if res.done or steps >= max_steps:
                if render:
                    draw_grid(screen, font, tile_size, env, hud_lines)
                break

        if running and episode_callback is not None:
            episode_callback(ep, env_return, total_return, steps, eps)

        if not running:
            break

    return not running
