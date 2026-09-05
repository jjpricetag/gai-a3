# A3 — Marking Rubric

**Total: 40 pts**

---

## Part I — Classical RL

### A. Gridworld Implementation and Rules — 2 pts

- **A1.** Pygame gridworld is visually rendered, animated, and interactive (not console/text).
- **A2.** Core mechanics match spec: 4 moves, rocks block, hazards kill instantly, apples +1, key unlocks chest, chest +2, end when rewards collected or death.

| Rating | Points |
|---|---|
| Excellent | 0.8 – 2 pts |
| Fair | >0 – 0.8 pts |

### B. Task 1 — Q-Learning (Level 0) — 2.5 pts

- **B1.** Epsilon-greedy policy used for action selection.
- **B2.** Correct Q-learning update rule implemented (off-policy, max next state).
- **B3.** Linear epsilon decay from `epsilonStart` to `epsilonEnd` (config-driven).
- **B4.** Random tie-breaking when multiple actions share best Q-value.
- **B5.** Demonstrates learned shortest-path policy to apples on Level 0 (evidence via rollout, policy display, or evaluation).

| Rating | Points |
|---|---|
| Excellent | 2.5 pts |
| No Marks | 0 pts |

### C. Task 2 — SARSA (Level 1) — 3 pts

- **C1.** Correct SARSA on-policy update (uses chosen next action, not max).
- **C2.** Uses same exploration schedule as Q-learning (same epsilon decay approach).
- **C3.** Evidence that SARSA policy differs from Q-learning (more conservative near hazards) with a short comparison.

| Rating | Points |
|---|---|
| Excellent | 3 pts |
| No Marks | 0 pts |

### D. Task 3 — Extend Q-Learning and SARSA (Levels 2–3) — 3 pts

- **D1.** Levels 2–3 implemented with required objects: multiple apples, key, chest.
- **D2.** Both algorithms run correctly on Levels 2–3 with correct episode termination and reward accounting.

| Rating | Points |
|---|---|
| Excellent | 3 pts |
| No Marks | 0 pts |

### F. Task 5 — Intrinsic Reward (Level 6) — 3 pts

Intrinsic reward implemented exactly:

- Keep environment rewards unchanged.
- Per-episode visit counter `n(s)`.
- `total reward = env reward + intrinsic reward`.
- Used in Q-learning/SARSA updates.
- Evidence includes training curve comparison and short explanation.

| Rating | Points |
|---|---|
| Excellent | 3 pts |
| No Marks | 0 pts |

> Note: the source rubric has no section **E** — sections are lettered A–D, then F onward.

---

## Part II — Deep RL Arena

### G. Arena Game Environment Requirements — 4.5 pts

- **G1.** Pygame arena is real-time and visually animated (not tile-grid feel).
- **G2.** Core gameplay implemented: player ship movement + shooting, enemy spawners create enemies periodically, enemies navigate toward player, collisions work.
- **G3.** Health systems (player and enemies) + phase system (destroy all spawners to progress difficulty). Episode ends on death or max time/steps.

| Rating | Points |
|---|---|
| Excellent | 2.25 – 4.5 pts |
| Fair | >0 – 2.25 pts |

### H. Gym-Style API + Observation Design — 2.5 pts

- **H1.** Gym-style API: `reset()`, `step(action) -> (obs, reward, done, info)`, `render()` for evaluation. *(2 pts)*
- **H2.** Observation is a fixed-size numeric vector and includes at least the required features (position, velocity, orientation if relevant, nearest enemy/spawner relative info, health, phase). *(3 pts)*

| Rating | Points |
|---|---|
| Excellent | 2.5 pts |
| No Marks | 0 pts |

### I. Two Control Schemes + Models — 4 pts

- **I1.** Control style 1 implemented (rotation + thrust + shoot + no-op).
- **I2.** Control style 2 implemented (direct movement + shoot + no-op).
- **I3.** Separate agent trained for each control scheme and saved models exist (in `models` folder).
- **I4.** Separate evaluation script(s) can visually run each trained agent.

| Rating | Points |
|---|---|
| Excellent | 4 pts |
| No Marks | 0 pts |

### J. Reward Design and Deep RL Training Quality — 3 pts

- **J1.** Reward structure encourages progression: enemy/spawner destruction, phase progress, damage penalty, death penalty (shaping justified if used).
- **J2.** Uses Stable Baselines3 with DQN or PPO, NN has at least one hidden layer, training is logged to TensorBoard.
- **J3.** Hyperparameters tuned in a meaningful way (not default-only) with some evidence of exploration.

| Rating | Points |
|---|---|
| Excellent | 3 pts |
| No Marks | 0 pts |

---

## Report Requirements — 2.5 pts

- **R1.** Max 10 pages including images, no appendix content counted.
- **R2.** Describes both environments clearly (what exists, how it runs).
- **R3.** Observation design explained (what each feature means, why chosen).
- **R4.** Reward design explained and justified (incl. shaping).
- **R5.** Hyperparameter exploration described with evidence (tables/plots).
- **R6.** Comparison of control sets + evidence (curves/screenshots/logs) + originality justification.

| Rating | Points |
|---|---|
| Full Marks | 2.5 pts |
| No Marks | 0 pts |

---

## Video Demo Presentation — 5 pts

- Video is no longer than 10 minutes and all group members appear and present at least one part.
- Gridworld shown running in a Pygame window with an agent using Q-learning or SARSA; items or monsters behave correctly for the level shown.
- Clear evidence the agent follows a learned policy (consistent behaviour, explanation during playback, not random actions).
- Real-time Pygame arena shown with trained deep RL agent; enemies, projectiles, collisions, and at least one phase progression visible.
- Learned behaviour demonstrated for both control schemes.

| Rating | Points |
|---|---|
| Full Marks | 5 pts |
| No Marks | 0 pts |

---

## Creativity — 5 pts

Students show creativity beyond what was expected.

| Rating | Points |
|---|---|
| Full Marks | 5 pts |
| No Marks | 0 pts |
