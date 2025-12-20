#!/usr/bin/env python3
"""Generate random walk visualization."""
import numpy as np
import matplotlib.pyplot as plt

# Set random seed for reproducibility
np.random.seed(42)

# Generate random walk
n_steps = 1000
steps = np.random.randn(n_steps, 2)
positions = np.cumsum(steps, axis=0)

# Create plot
fig, ax = plt.subplots(figsize=(10, 8))
ax.plot(positions[:, 0], positions[:, 1],
        alpha=0.6, linewidth=1, color='steelblue')
ax.plot(positions[0, 0], positions[0, 1],
        'go', markersize=10, label='Start')
ax.plot(positions[-1, 0], positions[-1, 1],
        'ro', markersize=10, label='End')
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_xlabel('x position')
ax.set_ylabel('y position')
ax.set_title(f'2D Random Walk ({n_steps} steps)')
ax.axis('equal')

# Save
plt.savefig('images/random_walk.png', dpi=150, bbox_inches='tight')
print("Generated: random_walk.png")
