# A3 - GridWorld RL & Deep RL Arena

## Setup

```bash
pip install -r requirements.txt
```

---

## Part I: GridWorld

### Running the game

```bash
python play_gridworld.py
```

Title screen -> **Play** -> pick a level -> pick a mode. Every level offers
whichever algorithm(s) it supports (**Q-Learning** and/or **SARSA**) plus
**Play (WASD)**, which lets you control the agent yourself instead of
watching it train - same environment, same rules, human-controlled.

See [markdowns/TEST_GAME.md](markdowns/TEST_GAME.md) for a full menu
walkthrough and a level-by-level testing checklist.

**Controls while an RL agent is training:** `V` toggles fast/visual mode,
`R` resets the current run (wipes the Q-table and the rolling stats panel),
closing the window quits the app.

**Controls in human Play mode:** `WASD` or arrow keys to move, `ESC` returns
to the menu.

### Levels

| Level | Task | Mechanics | Algorithm |
|---|---|---|---|
| 0 | 1 | Apples only | Q-learning (fixed) |
| 1 | 2 | Cliff-walk layout (fire row = short path, safe route over the top) | Q-learning or SARSA |
| 2 | 3 | Multiple apples, key, chest | Q-learning or SARSA |
| 3 | 3 | Same as Level 2 + rocks (longer route) | Q-learning or SARSA |
| 4 | 4 | Apples + 1 wandering monster (40% move chance/step) | Q-learning or SARSA |
| 5 | 4 | 2 monsters + rocks, harder navigation | Q-learning or SARSA |
| 6 | 5 | Curiosity-driven exploration with intrinsic reward | Q-learning or SARSA |

Level 1's layout is deliberately the classic "cliff walk": the shortest path
runs beside instant-death fire tiles, with a longer safe route over the top.
This is what makes Q-learning vs. SARSA actually diverge (Q-learning tends
to hug the cliff; SARSA keeps its distance) instead of learning identical
policies.

### Design notes

- **Terminal-state masking.** Both update rules zero out the bootstrap term
  (`gamma * Q(next_state)`) when the transition ends the episode - a
  terminal state has no future reward to bootstrap from. Missing this made
  Level 1 (cliff walk) fail to converge at all in testing.
- **Intrinsic reward (Level 6).** A per-episode state-visit counter adds
  `intrinsicRewardStrength / sqrt(visits + 1)` on top of the environment
  reward, encouraging exploration of rarely-visited states without changing
  the underlying environment reward itself.

### Project layout

```
gridworld/
  env.py            GridWorld environment (rules, step/reset)
  agents.py         QTable, epsilon-greedy, Q-learning & SARSA updates, intrinsic reward
  render.py         Pygame drawing (grid + right-hand HUD panel)
  levels.py         Level layouts (LEVELS dict, keyed by level id)
  config.py         Config loader (defaults + optional per-level JSON)
  train.py          Shared RL training loop + human WASD play loop
  ui.py             Menu Button widget
  logging_utils.py  Per-episode CSV logger
config/
  config_level0.json ... config_level6.json   Per-level training parameters
play_gridworld.py   Game entry point (menu -> level -> mode -> run)
run_experiment.py   Headless training run -> CSV (for report evidence)
plot_curves.py      Overlay CSVs into a comparison PNG
test_part2_implementation.py   Sanity checks for the Levels 4-6 mechanics (Tasks 4-5)
logs/               Training-curve CSVs
report_assets/      Comparison plots for the report
```

### Config files

Each `config/config_level{N}.json` overrides the defaults in
[gridworld/config.py](gridworld/config.py) for that level; any key you omit
falls back to the default. Missing file = defaults are used.

| Key | Meaning |
|---|---|
| `episodes` | Number of training episodes |
| `alpha` | Learning rate |
| `gamma` | Discount factor (how much future reward matters) |
| `epsilonStart` / `epsilonEnd` | Exploration rate at the start / end of decay |
| `epsilonDecayEpisodes` | Episodes over which epsilon linearly decays |
| `maxStepsPerEpisode` | Step cap before an episode is force-ended |
| `fpsVisual` / `fpsFast` | Render speed caps for the two visualize modes (game only) |
| `tileSize` | Pixel size per grid cell (visual only) |
| `seed` | RNG seed, for reproducible runs |
| `useIntrinsicReward` | Enables the Task 5 intrinsic reward bonus (Level 6) |
| `intrinsicRewardStrength` | Strength coefficient for the intrinsic bonus |

### Generating report evidence (training curves)

`run_experiment.py` trains headlessly (no window, full speed) and logs each
episode's return to CSV:

```bash
python run_experiment.py --level 1 --algorithm qlearning --out logs/level1_qlearning.csv
python run_experiment.py --level 1 --algorithm sarsa --out logs/level1_sarsa.csv
```

`--episodes N` overrides the config's episode count without editing the file.

Then overlay any set of CSVs into one comparison plot:

```bash
python plot_curves.py logs/level1_qlearning.csv:Q-learning logs/level1_sarsa.csv:SARSA \
    --title "Level 1: Q-learning vs SARSA" --out report_assets/level1_comparison.png
```

---

## Part II: Deep RL Arena

A real-time Pygame arena ([arena/](arena/)) with a controllable ship,
enemies, spawners that periodically create enemies, projectile collisions,
and a phase system (destroying all active spawners advances the difficulty).
Exposes a Gym-style API (`ArenaEnv` in [arena/env.py](arena/env.py):
`reset()`, `step()`, `render()`) with an 18-float observation vector, and is
trained with Stable-Baselines3 PPO.

### Play it yourself

```bash
python play_arena.py --style rotation   # thrust + rotate + shoot
python play_arena.py --style direct     # up/down/left/right + shoot
```
WASD/arrow keys to move, Space to shoot, `R` to reset, `Esc` to quit.

### Watch a trained agent

```bash
python evaluate.py --model models/ppo_rotation
python evaluate.py --model models/ppo_direct
```

Add `--episodes N` for more rollouts, `--no-render` to evaluate headlessly.
[models/](models/) also holds a set of ablation/hyperparameter-sweep models
(`abl_*`, `dir_lr*`, `rot2m_*`, `spawner006*`) from tuning experiments - each
`.zip` has a matching `.json` recording the config it was trained with.

### Training

```bash
python train.py --config arena_ppo_rotation.json --tag my_run
python train.py --config arena_ppo_direct.json --tag my_run
```

Base configs live in [config/arena_ppo_rotation.json](config/arena_ppo_rotation.json)
and [config/arena_ppo_direct.json](config/arena_ppo_direct.json) (PPO, 150k
timesteps, `[64, 64]` MLP policy); CLI flags (`--timesteps`, `--learning-rate`,
`--ent-coef`, `--seed`, etc.) override individual values without editing the
file. `config/exp_*.json` are the recorded sweep configs (reward-shaping
ablations, learning-rate comparisons, extended 2M-step runs) behind the
models in `models/`. Training logs to TensorBoard under `logs/` (`tensorboard
--logdir logs`).

### Reward shaping

Defined in [arena/settings.py](arena/settings.py), overridable per-config:
enemy kill +1, spawner destroyed +5, phase advance +10, taking damage -1,
death -10, small per-step cost -0.01 (encourages finishing efficiently
rather than stalling).

### Project layout

```
arena/
  env.py       Gym-style ArenaEnv (observation/action/reward, step/reset)
  game.py      Core simulation (entities, physics, collisions, phases)
  entities.py  Player/enemy/spawner/projectile classes
  render.py    Pygame drawing
  settings.py  Constants (window size, rewards, obs size, action sets)
  config.py    JSON config load/save for training runs
play_arena.py  Human-playable entry point (both control schemes)
train.py       SB3 PPO/DQN training CLI
evaluate.py    Loads a saved model and plays/evaluates it
config/        Base + experiment-sweep training configs
models/        Trained model checkpoints (.zip) + their config (.json)
logs/          TensorBoard event logs per training run
```

---

## Status

- **Part I:** complete - all 7 levels, Q-learning, SARSA, human play mode,
  config-driven training, evidence pipeline.
- **Part II:** complete - arena environment, both control schemes, PPO
  models trained and evaluated, hyperparameter/reward-shaping experiments
  logged to TensorBoard.
- **Video demo:** Link to video demo: https://www.youtube.com/watch?v=WkwThnYnZ9E
