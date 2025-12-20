#!/usr/bin/env python3
"""Generate sine and cosine plot."""
import numpy as np
import matplotlib.pyplot as plt

# Generate data
x = np.linspace(0, 4 * np.pi, 1000)
y_sin = np.sin(x)
y_cos = np.cos(x)

# Create plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, y_sin, label='sin(x)', linewidth=2)
ax.plot(x, y_cos, label='cos(x)', linewidth=2)
ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('Sine and Cosine Functions')

# Save
plt.savefig('images/trig_functions.png', dpi=150, bbox_inches='tight')
print("Generated: trig_functions.png")
