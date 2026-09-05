# Part I. Classical Reinforcement Learning

In this part you will implement Q-learning and SARSA in a visual gridworld created in Python. Your gridworld must be implemented and visually rendered in Pygame and must support interaction and animation. Console or text based displays are not permitted.

## 1. Gridworld Rules

- The agent can move: up, down, left, right.
- Rocks block movement. Attempting to move into one results in no movement.
- Stepping into fire or monsters results in immediate death.
- Apples give **+1** reward.
- Keys give no reward but allow opening chests.
- Opening a chest gives **+2** reward.
- The episode ends when all collectible rewards are obtained or the agent dies.
- After each agent action, monsters (if present) have a **40%** chance of moving.
- You may add helper functions if needed but must not alter rewards or mechanics.
- You must create multiple levels with different layouts.

## Task 1: Basic Q-Learning (Level 0)

Level 0 contains only apples, on the right side of the map.

Your Q-learning implementation must:

- Use an epsilon-greedy policy
- Update Q-values according to the Q-learning rule
- Use linear epsilon decay from `epsilonStart` to `epsilonEnd`
- Use random tie-breaking when multiple actions have equal value
- Successfully learn a shortest-path policy to the apples

> Training parameters (episodes, alpha, gamma, epsilon ranges) will be provided in a config file.

## Task 2: Basic SARSA (Level 1)

Implement SARSA using on-policy updates:

- Use the same exploration schedule as Q-learning
- Demonstrate that the learned policy differs from Q-learning, typically being more conservative around hazards

## Task 3: Extend Q-Learning and SARSA (Levels 2–3)

Levels 2–3 introduce:

- Multiple apples
- A key
- A chest

## Task 4: Monster Levels (Levels 4–5)

**What to implement**

- Monsters that move after each agent action
- Movement is probabilistic (e.g. 40% chance to move)
- Monsters use a simple pattern, such as choosing randomly from allowed directions
- If the player enters a monster tile or a monster moves into the player, the player dies

**What is required from the RL side**

- Your Q-learning and SARSA implementations must handle stochastic transitions
- The agent should learn to avoid monsters while still completing objectives

**Evidence to include**

- Working monster movement in your gridworld
- Training curves showing learning behaviour on Levels 4 and 5

## Task 5: Intrinsic Reward (Level 6)

**What to implement**

Intrinsic reward:

```
r_i = intrinsicRewardStrength / sqrt(n(s) + 1)
```

Where:

- `n(s)` = number of visits to the current state during the episode
- `total reward = environment reward + intrinsic reward`

**Requirements**

- Keep all environment rewards unchanged
- Maintain a visit counter for each state per episode
- Agent must use intrinsic reward during Q-learning or SARSA updates

**Evidence to include in your report**

- Training curves comparing learning with and without intrinsic reward
- Short explanation of the improvement observed

---

# Part II. Deep Reinforcement Learning in a Pygame Arena

In this part you will design a real-time Pygame arena and train deep RL agents inside it using Stable Baselines3. The simulation must be your own design and must be visually animated. The agent will learn from a continuous observation vector and train with a neural network based algorithm.

## 1. Environment Requirements

Your Pygame scene must include:

- A controllable player ship with movement and shooting
- Enemy spawners that periodically create enemies
- Enemies that navigate toward the player
- Player health
- Enemy health
- Projectile collisions
- A phase system where destroying all active spawners progresses the simulation to the next difficulty level

The game must feel like a simplified action arena instead of a tile-based grid. Movements should be continuous or semi-continuous. All elements must be visual on screen.

**The episode ends when:**

- The player dies
- A maximum time or step count is reached

## 2. Gym-Style API

Your environment must expose these methods:

| Method | Behaviour |
|---|---|
| `reset()` | Returns an initial observation |
| `step(action)` | Applies an action and returns `observation, reward, done, info` |
| `render()` | Displays the scene for evaluation |

## 3. Observation Design

Your agent must receive a fixed-size vector containing at least:

- Player position
- Player velocity
- Player orientation (if relevant)
- Distance and relative direction to nearest enemy
- Distance and relative direction to nearest spawner
- Player health
- Current phase

> Prefer feature vectors over pixels/screenshots. They must be numeric and fixed size.

## 4. Action Sets

You must implement **two distinct control schemes** and train a separate agent for each one.

**Control style 1 — Rotation movement and thrust**

- No action
- Thrust forward
- Rotate left
- Rotate right
- Shoot

**Control style 2 — Direct directional movement**

- No action
- Move up
- Move down
- Move left
- Move right
- Shoot

Each style must produce a trained model and an evaluation script (a separate trained model per style).

## 5. Reward Function

You must define a reward structure that encourages intentional progression, for example:

- Positive reward for destroying enemies
- Larger positive reward for destroying spawners
- Positive reward when progressing to the next phase
- Negative reward when taking damage
- Strong negative reward on death

Optional shaping rewards must be justified. Reward design is part of the assessment — you may use additional shaping with justification.

## 6. Deep RL Training

You are advised to use Stable Baselines3 with either **DQN** or **PPO**.

**Expectations:**

- Use neural networks with at least one hidden layer
- Train using Stable Baselines3 while logging results to TensorBoard
- Tune hyperparameters in a meaningful way
- Save trained models in a folder named `models`
- Provide an evaluation script able to visually play the agent in the arena

---

# Appendix: Technical Expectations and Feasibility Guide

To ensure the project remains feasible on standard hardware, here are the technical expectations. The below is not a requirement but is a feasible guide to help you.

**Gridworld**

- Use grids around 10x10 or 12x12
- Use simple shapes in Pygame
- Q-learning and SARSA must run quickly

**Arena simulation**

- Window size around 800x600 or 960x680
- Use clear shapes for players, enemies, and bullets
- Keep enemy count and spawner frequency manageable
- Physics should remain simple
- Render only during evaluation, not during long training runs

**Observation vector**

- Should contain around 10 to 30 float features
- Must be fixed size
- Must not use pixels or images

**RL training**

- Use Stable Baselines3
- Networks should be small MLPs
- Train headless for speed
- Total training typically between 100,000 and 600,000 timesteps
- Use TensorBoard for monitoring
