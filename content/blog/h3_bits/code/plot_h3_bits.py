import h3

import matplotlib.pyplot as plt
import matplotlib.patches as patches

h = h3.latlng_to_cell(0, 0, res=4)
h = '0' + h3.latlng_to_cell(0, 0, res=4)
bh = '0000' + str(bin(h3.str_to_int(h)))[2:]

# Define parameters
num_squares = 64  # Total number of small squares
square_size = 1   # Size of each square
group_size = 4    # Number of small squares per longer box

fig, ax = plt.subplots(figsize=(40, 5))

# 'Courier New',
# 'Times New Roman',
# 'Arial',
# 'sans-serif',
def square(x, y, n=1, text=None, fontsize=12, fontname=None, fontweight=None):
    rect = patches.Rectangle((x, y), n, 1, edgecolor='black', facecolor='none', linewidth=2)
    ax.add_patch(rect)
    ax.text(
        x + n*0.5, y + 0.5,
        text,
        fontsize=fontsize,
        ha='center', va='center',
        fontname = fontname,
        fontweight = fontweight,
    )

def sections(bh):
    third_row_lengths = [1, 4, 3, 4, 7] + 15 * [3]  # These should sum to 64
    labels = ['0', 'mode', 'reserved', 'resolution', 'base cell'] + [f'child {x}' for x in range(1,16)]

    start_pos = 0
    for length, label in zip(third_row_lengths, labels):
        yield (start_pos, length, label, bh[start_pos:start_pos+length])
        start_pos += length

def tick(x,y,dx=+1,dy=+1, label=None):
    tick_length = 0.5

    i = x

    x += .01*dx
    y += .03*dy

    x2 = x + tick_length*dx
    y2 = y + tick_length*dy

    x3 = x2 + 0.3*dx
    y3 = y2 + 0.3*dy

    ax.plot([x, x2], [y, y2], color='black', linewidth=2)

    if label is None:
        label = str(i)
    ax.text(x3, y3, label, fontsize=16, ha='center', va='center')


for i in range(num_squares):
    square(i, 2, 1, bh[i], fontsize=24, fontname='Courier New', fontweight='bold')

for i in range(0, num_squares, group_size):
    # TODO: maybe add '0x'
    square(i, 3, group_size, h[i // group_size], fontsize=24, fontname='Courier New', fontweight='bold')

    # ticks above
    tick(i, 4, +1, +1, label=str(64-i))

for i, n, label, num in sections(bh):
    square(i, 1, n=n, text=label, fontsize=24, fontname='Times New Roman')
    square(i, 0, n=n, text=int(num, 2), fontsize=24, fontname='Arial')

    # if i in [1,8, 19, 25, 31, 37, 43, 49, 55, 61]:
    if i in [0,5, 12, 22, 28, 34, 40, 46, 52, 58]:
        rect = patches.Rectangle((i, 0), n, 3, facecolor='grey', linewidth=0, alpha=0.2)
        ax.add_patch(rect)

    # ticks below
    if i > 0:
        tick(i, 0, -1, -1)

tick(64, 0, -1, -1)

# Set limits and aspect ratio
ax.set_xlim(-1, num_squares + 1)
ax.set_ylim(-2, 4 * square_size + 2)
ax.set_aspect(1)

# Remove axes
ax.set_xticks([])
ax.set_yticks([])
ax.axis('off')

fig.tight_layout()

plt.savefig(f'figs/{h[1:]}.png', dpi=200)
