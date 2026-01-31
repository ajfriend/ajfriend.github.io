from pathlib import Path

import h3
from h3_bits import plot_h3_bits

output_dir = Path(__file__).parent.parent.parent / 'figs'


cells = [
    h3.latlng_to_cell(0, 0, res=4),
    # h3.latlng_to_cell(37.7749, -122.4194, res=9)  # San Francisco
]

for cell in cells:
    plot_h3_bits(cell, output_dir, fmt='png')
