# NEURAL-SYNC: OBSIDIAN SECTOR

```
╔══════════════════════════════════════════════════════════════════╗
║   N E U R A L - S Y N C   :   O B S I D I A N   S E C T O R    ║
║   Cyberpunk grid-management action game                         ║
║   Prevent thermal cascade. Control the meltdown.                ║
╚══════════════════════════════════════════════════════════════════╝
```

A real-time cyberpunk grid-management game built with **Pygame**. You control a neural processing matrix of 64 nodes. Heat builds continuously. Worms hunt the hottest node. Your job: keep the system alive.

---

## Screenshots / Visuals

| State | Description |
|---|---|
| 🟦 Cold Node `#16213E` | Heat 0–30% — system stable |
| 🟦 Warm Node `#0F3460` | Heat 31–70% — monitor closely |
| 🟥 Critical Node `#E94560` | Heat 71–99% — intervene now |
| 💥 SYSTEM_COLLAPSE | 4+ nodes hit 100% simultaneously |

---

## Requirements

- Python **3.8+**
- Pygame **2.x**

```bash
pip install pygame
```

---

## Installation & Running

```bash
# Clone or download the project
git clone https://github.com/yourname/neural-sync-obsidian-sector.git
cd neural-sync-obsidian-sector

# Install dependency
pip install pygame

# Run the game
python neural_sync.py
```

---

## Controls

| Input | Action |
|---|---|
| `Left Click` on a node | Fire **Synapse Pulse** — cools node by 25%, costs 15% coolant |
| `R` | Restart (Game Over screen only) |
| `ESC` | Quit |

---

## Gameplay

### Objective
Prevent **4 or more nodes** from reaching **100% heat simultaneously**. If that happens, the system collapses.

### Core Loop
- Every node heats up **passively** at a constant rate — there is no pause
- Click nodes to cool them down using your **Coolant Tank**
- Coolant refills slowly over time — spend it wisely
- **Glitch Worms** spawn every 12 seconds from random screen edges, seeking the hottest node and adding +25 heat on contact

### Heat Diffusion
When any node exceeds **75% heat**, it begins spreading heat to its 4 direct neighbors (up/down/left/right). Hot clusters cascade fast — don't let them form.

### Coolant Tank
- Displayed on the right side of the screen (vertical bar)
- Each click costs **15%** coolant
- Refills at **8% per second** passively
- When depleted, clicks have no effect — wait for refill

---

## Game Mechanics Reference

| Mechanic | Value |
|---|---|
| Heat rise rate | 1.0 heat/second |
| Diffusion threshold | 75% heat |
| Diffusion rate | `H_neighbor += H_self × 0.05 × dt` |
| Meltdown trigger | 4 nodes at 100% simultaneously |
| Worm spawn interval | Every 12 seconds |
| Worm heat on contact | +25 heat, then dies |
| Screen shake duration | 20 frames per meltdown event |
| Coolant per click | −15% coolant, −25 node heat |
| Coolant refill rate | +8% per second |

---

## Technical Architecture

### Classes

| Class | Role |
|---|---|
| `Node` | Single grid cell — manages heat state, sag offset, rendering, heartbeat animation |
| `Particle` | 1×1px spark — spawned on click, 30-frame lifespan, random trajectory |
| `GlitchWorm` | Enemy NPC — 6-segment worm, pathfinds to hottest node |
| `Needle` | Player cursor — rotating crosshair, synapse pulse lines |
| `NeuralSync` | Main game controller — grid, physics loop, HUD, game over |

### Physics (Delta-Time Normalized)
All movement and heat calculations use `dt` (seconds per frame) so the game runs correctly at any frame rate.

```
Heat Rise:    H_new = H_old + (1.0 × dt)
Diffusion:    H_neighbor += H_self × 0.05 × dt  (when H_self > 75)
Shake Offset: X = sin(frame × 1.5) × (amplitude × frames_remaining / total_frames)
```

### Color System
Colors are computed via **3-way linear interpolation**:

```
0–40%  heat  →  STABLE  (#16213E)  →  WARM     (#0F3460)
40–100% heat  →  WARM   (#0F3460)  →  CRITICAL (#E94560)
```

### Visual Effects Stack (render order)
1. Grid background (faint guide lines)
2. Node-to-node wire connections (heat-colored)
3. Node glow halos (LAYER — alpha composited)
4. Node bodies + heartbeat squares + heat labels
5. Glitch Worms
6. Spark particles
7. Needle (cursor)
8. Alpha composite layer blit
9. Scanlines overlay (static — built once at startup)
10. Vignette overlay (static — built once at startup)
11. HUD (title, stats, coolant tank)
12. Game Over overlay (if triggered)

---

## HUD Elements

- **Top-left** — Title bar + live stats: meltdown count, average heat, worm count, next worm timer, coolant level
- **Right side** — Coolant tank (30×400px vertical bar) with slosh surface effect and danger pulse when low
- **Bottom center** — Control hint bar
- **Node labels** — Heat percentage displayed inside each node, jitters randomly when heat exceeds 92%

---

## File Structure

```
neural-sync-obsidian-sector/
│
├── neural_sync.py      # Complete game — single file, no assets needed
└── README.md           # This file
```

No external assets required. All visuals are drawn programmatically with Pygame primitives.

---

## Color Palette

| Name | Hex | Usage |
|---|---|---|
| `PRIMARY_VOID` | `#08080A` | Background |
| `CORE_STABLE` | `#16213E` | Nodes at 0–30% heat |
| `CORE_WARM` | `#0F3460` | Nodes at 31–70% heat |
| `CORE_CRITICAL` | `#E94560` | Nodes at 71–100% heat |
| `PULSE_GLITCH` | `#FFD369` | Worms, particles, highlights |
| `COOLANT_HUD` | `#00D2FF` | UI, cursor, coolant tank |

---

## Development Roadmap

| Phase | Hours | Scope |
|---|---|---|
| 1 | 1–4 | Node class, grid rendering, sag mechanic |
| 2 | 5–8 | Heat diffusion math, color lerping |
| 3 | 9–12 | Needle interaction, coolant tank depletion/refill |
| 4 | 13–16 | Glitch Worm AI and collision logic |
| 5 | 17–20 | Screen shake, jitter text, particle juice |

Total estimated development time: **~20 hours**

---

## License

MIT License — free to use, modify, and distribute.
