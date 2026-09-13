import time
from collections import deque

import pygame

from .agents import QTable, VisitCounter, epsilon_greedy, linear_epsilon, q_learning_update, sarsa_update, compute_intrinsic_reward
from .env import A_DOWN, A_LEFT, A_RIGHT, A_UP, GridWorld
from .render import draw_grid, draw_summary_screen, draw_victory_overlay

OUTCOME_WINDOW = 20
OUTCOME_LABELS = {"success": "Success", "death": "Died", "timeout": "Timeout"}

# WASD is the primary scheme; arrow keys work as an alias.
HUMAN_KEY_ACTIONS = {
    pygame.K_w: A_UP, pygame.K_UP: A_UP,
    pygame.K_d: A_RIGHT, pygame.K_RIGHT: A_RIGHT,
    pygame.K_s: A_DOWN, pygame.K_DOWN: A_DOWN,
    pygame.K_a: A_LEFT, pygame.K_LEFT: A_LEFT,
}


def _classify_outcome(res):
    if res.done:
        return "death" if res.info.get("event") == "death" else "success"
    return "timeout"


def _build_hud_lines(title, algorithm, ep, episodes, steps, eps, env_return, env,
                      last_outcome, outcome_history, visualize):
    """One stat per line, for the right-hand HUD panel."""
    lines = [
        title,
        f"Algorithm: {algorithm.upper()}",
        f"Mode: {'VISUAL' if visualize else 'FAST'}",
        "",
        f"Episode: {ep + 1}/{episodes}",
        f"Step: {steps}",
        f"Epsilon: {eps:.3f}",
        "",
        f"Apples left: {bin(env.apple_mask).count('1')}",
    ]
    if env.chests:
        lines.append(f"Chests left: {bin(env.chest_mask).count('1')}")
    if env.key_positions:
        lines.append(f"Keys held: {env.key_count}")
    if env.monsters:
        lines.append(f"Monsters: {len(env.monsters)}")

    lines += ["", f"Return: {env_return:.2f}", ""]

    lines.append(f"Last ep: {'n/a' if last_outcome is None else OUTCOME_LABELS[last_outcome]}")
    if outcome_history:
        n = len(outcome_history)
        succ_pct = 100 * outcome_history.count("success") / n
        death_pct = 100 * outcome_history.count("death") / n
        timeout_pct = 100 * outcome_history.count("timeout") / n
        lines.append(f"Last {n} eps:")
        lines.append(f"  {succ_pct:.0f}% success")
        lines.append(f"  {death_pct:.0f}% death")
        lines.append(f"  {timeout_pct:.0f}% timeout")
    else:
        lines.append("Last 0 eps: n/a")

    lines += ["", "V: toggle fast mode", "R: reset run", "S: stop & return to menu"]
    return lines


def _build_human_hud_lines(title, env, round_return, last_outcome, rounds_played, wins, deaths):
    lines = [
        title,
        "Mode: Human Play",
        "",
        f"Apples left: {bin(env.apple_mask).count('1')}",
    ]
    if env.chests:
        lines.append(f"Chests left: {bin(env.chest_mask).count('1')}")
    if env.key_positions:
        lines.append(f"Keys held: {env.key_count}")
    if env.monsters:
        lines.append(f"Monsters: {len(env.monsters)}")

    lines += ["", f"Return: {round_return:.2f}", ""]
    lines.append(f"Last round: {'n/a' if last_outcome is None else OUTCOME_LABELS[last_outcome]}")
    lines.append(f"Rounds played: {rounds_played}")
    lines.append(f"  Wins: {wins}  Deaths: {deaths}")
    lines += ["", "WASD / Arrows: move", "ESC: back to menu"]
    return lines


def _build_summary_lines(algorithm, completed_episodes, elapsed_seconds, total_steps,
                          success, death, timeout, best_return, avg_return,
                          recent_returns, final_eps):
    n = max(completed_episodes, 1)
    lines = [
        f"Algorithm: {algorithm.upper()}",
        f"Episodes completed: {completed_episodes}",
        f"Training time: {elapsed_seconds:.1f}s",
        f"Total steps: {total_steps}",
        "",
        f"Success: {success} ({100 * success / n:.0f}%)",
        f"Death: {death} ({100 * death / n:.0f}%)",
        f"Timeout: {timeout} ({100 * timeout / n:.0f}%)",
        "",
        f"Best episode return: {best_return:.2f}",
        f"Average return (all episodes): {avg_return:.2f}",
    ]
    if recent_returns:
        recent_avg = sum(recent_returns) / len(recent_returns)
        lines.append(f"Average return (last {len(recent_returns)} episodes): {recent_avg:.2f}")
    lines += ["", f"Final epsilon: {final_eps:.3f}"]
    return lines


def _show_training_summary(screen, clock, font, title, summary_lines) -> bool:
    """Blocks until the user dismisses the end-of-training screen (Back to
    Menu button, Space, Enter, or Escape). Returns True if they closed the
    window instead."""
    title_font = pygame.font.Font(None, 48)
    line_font = pygame.font.Font(None, 24)
    btn = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN,
            ):
                return False
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                    and btn is not None and btn.is_clicked(event.pos)):
                return False

        btn = draw_summary_screen(
            screen, title_font, line_font, font,
            f"{title} - Training Complete", summary_lines,
        )
        pygame.display.flip()
        clock.tick(30)


def run_human_play(env: GridWorld, cfg: dict, screen, clock, font, title: str) -> bool:
    """Lets a human control the agent with WASD/arrow keys. Returns True if the
    user closed the window (as opposed to pressing ESC to just go back).

    On winning a round, the grid freezes behind a greyed-out victory overlay
    until the player restarts (Restart button, Space, or Enter)."""
    tile_size = int(cfg["tileSize"])
    fps = int(cfg.get("fpsVisual", 30))
    victory_font = pygame.font.Font(None, 64)

    env.reset()
    round_return = 0.0
    rounds_played, wins, deaths = 0, 0, 0
    last_outcome = None
    running = True
    show_victory = False
    restart_btn = None

    def restart_round():
        nonlocal round_return, show_victory
        env.reset()
        round_return = 0.0
        show_victory = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                if show_victory:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        restart_round()
                    continue
                action = HUMAN_KEY_ACTIONS.get(event.key)
                if action is not None:
                    res = env.step(action)
                    round_return += res.reward
                    if res.done:
                        last_outcome = _classify_outcome(res)
                        rounds_played += 1
                        if last_outcome == "success":
                            wins += 1
                            show_victory = True
                        else:
                            if last_outcome == "death":
                                deaths += 1
                            env.reset()
                            round_return = 0.0
            elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                  and show_victory and restart_btn is not None
                  and restart_btn.is_clicked(event.pos)):
                restart_round()
        if not running:
            break

        hud_lines = _build_human_hud_lines(
            title, env, round_return, last_outcome, rounds_played, wins, deaths,
        )
        draw_grid(screen, font, tile_size, env, hud_lines, flip=not show_victory)
        if show_victory:
            restart_btn = draw_victory_overlay(screen, victory_font, font)
            pygame.display.flip()
        clock.tick(fps)

    return False


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
    """Runs Q-learning or SARSA training for `env`. Returns True if the user closed the window
    (as opposed to pressing S to just stop and go back to the menu).

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
    window_closed = False
    outcome_history = deque(maxlen=OUTCOME_WINDOW)
    recent_returns = deque(maxlen=OUTCOME_WINDOW)
    last_outcome = None

    completed_episodes = 0
    total_success = total_death = total_timeout = 0
    total_steps_sum = 0
    total_return_sum = 0.0
    best_return = float("-inf")
    training_start = time.perf_counter()

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
                    window_closed = True
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
                        outcome_history.clear()
                        last_outcome = None
                    if event.key == pygame.K_s:
                        # Stop training and reset to the default (untrained) state,
                        # then hand control back to the menu - not a full app quit.
                        qtab = QTable()
                        env.reset()
                        outcome_history.clear()
                        last_outcome = None
                        running = False
                        break
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
                # In fast mode, only build/draw/tick on the steps we actually
                # redraw - ticking every step throttled raw step throughput
                # to fps_fast even on the 4/5 of steps that skip drawing.
                episode_ending = res.done or steps >= max_steps
                should_draw = visualize or episode_ending or steps % 5 == 0
                if should_draw:
                    hud_lines = _build_hud_lines(
                        title, algorithm, ep, episodes, steps, eps, env_return, env,
                        last_outcome, outcome_history, visualize,
                    )
                    draw_grid(screen, font, tile_size, env, hud_lines)
                    clock.tick(fps_visual if visualize else fps_fast)

            if res.done or steps >= max_steps:
                break

        if running:
            last_outcome = _classify_outcome(res)
            outcome_history.append(last_outcome)
            recent_returns.append(env_return)
            completed_episodes += 1
            total_steps_sum += steps
            total_return_sum += env_return
            best_return = max(best_return, env_return)
            if last_outcome == "success":
                total_success += 1
            elif last_outcome == "death":
                total_death += 1
            else:
                total_timeout += 1
            if episode_callback is not None:
                episode_callback(ep, env_return, steps, eps)

        if not running:
            break

    # `running` is still True here only if the for-loop finished on its own
    # (all episodes completed) rather than via S/QUIT breaking out early.
    if render and running and completed_episodes > 0:
        elapsed = time.perf_counter() - training_start
        avg_return = total_return_sum / completed_episodes
        summary_lines = _build_summary_lines(
            algorithm, completed_episodes, elapsed, total_steps_sum,
            total_success, total_death, total_timeout, best_return, avg_return,
            recent_returns, eps,
        )
        window_closed = _show_training_summary(screen, clock, font, title, summary_lines)

    return window_closed
