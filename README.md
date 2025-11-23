# Cosmic Wayfinder: AI Search & Problem-Solving Agent

Cosmic Wayfinder is a Python game and interactive simulation where an intelligent agent navigates a dynamic 2D space environment to reach a target efficiently. Unlike classic examples like mazes or the 8-puzzle, this project combines obstacles, variable traversal costs, and teleportation points (wormholes) to create a rich, non-trivial pathfinding challenge.

---

## 🚀 Features

- **Dynamic Grid Environment**
  - **Nebulas:** Slow down movement (higher traversal cost).  
  - **Asteroids:** Increase the cost to move through them.  
  - **Black Holes:** Impassable obstacles that block the path.  
  - **Wormholes:** Teleportation points that can shortcut the route.  

- **AI Search Algorithms**
  - **Uniform Cost Search (UCS):** Explores all paths to guarantee the lowest-cost route.  
  - **A\* Search:** Uses heuristics to find an optimal path more efficiently.  
  - **Greedy Best-First Search:** Fast exploration that prioritizes speed over optimality.  

- **Interactive Visualization**
  - Real-time display of the agent, obstacles, and wormholes.  
  - Animated ships and stars enhance immersion.  
  - “Race mode” lets you see how A* and Greedy differ in real time.  

---

## 🧠 How It Works

The agent navigates a grid filled with obstacles and optional wormholes. Each terrain type affects movement differently, requiring the agent to balance speed and cost:  

- **Decision-making:** Should the agent take a wormhole, risk high-cost terrain, or follow a safer path?  
- **Algorithm trade-offs:** UCS guarantees optimal paths but explores more nodes. A* reduces search effort with heuristics. Greedy is fastest but may miss the optimal path.  
- **Race mode:** Observe AI agents competing to reach the goal, illustrating the practical differences between algorithms.  

---

## 📊 Comparative Evaluation

| Algorithm | Nodes Expanded | Path Cost | Time | Optimal | Notes |
|-----------|----------------|-----------|------|---------|-------|
| UCS       | High           | Lowest    | Medium | Yes     | Explores all paths; guarantees the optimal route. |
| A*        | Moderate       | Lowest    | Low    | Yes     | Efficient heuristic reduces exploration while maintaining optimality. |
| Greedy    | Low            | Higher    | Very Low | No    | Fastest exploration, but may produce suboptimal paths. |

**Insights:**
- UCS ensures optimality but consumes more memory and time.  
- A* balances speed and optimality using heuristics.  
- Greedy is fastest with minimal memory usage but can miss better routes.  
- Teleportation introduces strategic complexity, as the agent must decide whether using a wormhole is worth the cost.  

---

## 🎮 Installation & Usage

1. Clone the repository:

```bash
git clone https://github.com/YourUsername/CosmicWayfinder.git
cd CosmicWayfinder
```
2. Install dependencies:
```bash
pip install pygame
```
3. Run the game:
```bash
python cosmic_wayfinder.py
```
