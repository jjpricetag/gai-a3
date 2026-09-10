import pygame

from .agents import QTable, VisitCounter, epsilon_greedy, linear_epsilon, q_learning_update, sarsa_update, compute_intrinsic_reward
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
    render: bool = True,
    episode_callback=None,
    use_intrinsic_reward: bool = False,
) -> bool:
    """Runs Q-learning or SARSA training for `env`. Returns True if the user closed the window.

    render=False skips all drawing so training runs at full speed (for generating
    report evidence). episode_callback(episode, env_return, steps, epsilon), if
    given, is called once at the end of each completed episode.

    If use_intrinsic_reward=True, intrinsic rewards are added based on visit counts.
    """
    assert algorithm in ("qlearning", "sarsa")

    episodes = int(cfg["episodes"])
    alpha, gamma = float(cfg["alpha"]), float(cfg["gamma"])
    eps_start, eps_end = float(cfg["epsilonStart"]), float(cfg["epsilonEnd"])
    eps_decay_ep = int(cfg["epsilonDecayEpisodes"])
    max_steps = int(cfg["maxStepsPerEpisode"])
    fps_visual, fps_fast = int(cfg["fpsVisual"]), int(cfg["fpsFast"])
    tile_size = int(cfg["tileSize"])
    intrinsic_strength = float(cfg.get("intrinsicRewardStrength", 0.0))

    qtab = QTable()
    visit_counter = VisitCounter() if use_intrinsic_reward else None
    visualize, running = True, True

    for ep in range(episodes):
        s = env.reset()
        if visit_counter:
            visit_counter.reset()
        env_return, steps = 0.0, 0
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
                        env_return, steps = 0.0, 0
                        eps = linear_epsilon(ep, eps_start, eps_end, eps_decay_ep)
                        a = epsilon_greedy(qtab, s, eps) if algorithm == "sarsa" else None
            if not running:
                break

            if algorithm == "qlearning":
                a = epsilon_greedy(qtab, s, eps)
            res = env.step(a)

            # Calculate total reward (env reward + optional intrinsic reward)
            total_reward = res.reward
            if visit_counter:
                visit_count = visit_counter.visit(s)
                intrinsic_r = compute_intrinsic_reward(visit_count, intrinsic_strength)
                total_reward = res.reward + intrinsic_r

            if algorithm == "qlearning":
                q_learning_update(qtab, s, a, total_reward, res.next_state, alpha, gamma, done=res.done)
                s = res.next_state
            else:  # sarsa
                ap = epsilon_greedy(qtab, res.next_state, eps)
                sarsa_update(qtab, s, a, total_reward, res.next_state, ap, alpha, gamma, done=res.done)
                s, a = res.next_state, ap

            env_return += res.reward  # Log environment reward only, not intrinsic
            steps += 1

            if render:
                hud_lines = [
                    f"Ep {ep + 1}/{episodes}  step {steps}  eps {eps:.3f}  {algorithm.upper()}",
                    f"Apples left {bin(env.apple_mask).count('1')}"
                    + (f"  Chests left {bin(env.chest_mask).count('1')}" if env.chests else "")
                    + (f"  Keys {env.key_count}" if env.key_positions else "")
                    + (f"  Monsters {len(env.monsters)}" if env.monsters else ""),
                    f"Return {env_return:.2f}  {title}",
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
            episode_callback(ep, env_return, steps, eps)

        if not running:
            break

    return not running
