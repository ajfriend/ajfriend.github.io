import h3
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path


def _sections(bh):
    lengths = [1, 4, 3, 4, 7] + 15 * [3]
    labels = ['0', 'mode', 'reserved', 'resolution', 'base cell'] + [f'child {x}' for x in range(1, 16)]

    start_pos = 0
    for length, label in zip(lengths, labels):
        yield (start_pos, length, label, bh[start_pos:start_pos + length])
        start_pos += length


def plot_h3_bits(cell, output_dir, fmt='png'):
    """Plot the bit structure of an H3 cell and save to output_dir."""
    h = '0' + cell
    bh = '0000' + str(bin(h3.str_to_int(cell)))[2:]

    num_squares = 64
    square_size = 1
    group_size = 4

    fig, ax = plt.subplots(figsize=(40, 5))

    def square(x, y, n=1, text=None, fontsize=12, fontname=None, fontweight=None):
        rect = patches.Rectangle((x, y), n, 1, edgecolor='black', facecolor='none', linewidth=2)
        ax.add_patch(rect)
        ax.text(
            x + n * 0.5, y + 0.5,
            text,
            fontsize=fontsize,
            ha='center', va='center',
            fontname=fontname,
            fontweight=fontweight,
        )

    def tick(x, y, dx=+1, dy=+1, label=None):
        tick_length = 0.5
        i = x
        x += .01 * dx
        y += .03 * dy
        x2 = x + tick_length * dx
        y2 = y + tick_length * dy
        x3 = x2 + 0.3 * dx
        y3 = y2 + 0.3 * dy
        ax.plot([x, x2], [y, y2], color='black', linewidth=2)
        if label is None:
            label = str(i)
        ax.text(x3, y3, label, fontsize=16, ha='center', va='center')

    for i in range(num_squares):
        square(i, 2, 1, bh[i], fontsize=24, fontname='Courier New', fontweight='bold')

    for i in range(0, num_squares, group_size):
        square(i, 3, group_size, h[i // group_size], fontsize=24, fontname='Courier New', fontweight='bold')
        tick(i, 4, +1, +1, label=str(64 - i))

    for i, n, label, num in _sections(bh):
        square(i, 1, n=n, text=label, fontsize=24, fontname='Times New Roman')
        square(i, 0, n=n, text=int(num, 2), fontsize=24, fontname='Arial')

        if i in [0, 5, 12, 22, 28, 34, 40, 46, 52, 58]:
            rect = patches.Rectangle((i, 0), n, 3, facecolor='grey', linewidth=0, alpha=0.2)
            ax.add_patch(rect)

        if i > 0:
            tick(i, 0, -1, -1)

    tick(64, 0, -1, -1)

    ax.set_xlim(-1, num_squares + 1)
    ax.set_ylim(-2, 4 * square_size + 2)
    ax.set_aspect(1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    fig.tight_layout()

    output_path = Path(output_dir) / f'{cell}.{fmt}'
    plt.savefig(output_path, dpi=200)
    plt.close(fig)
    return output_path
