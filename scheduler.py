import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import argparse  # Added for command-line argument handling

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="Generate market volunteer schedule")
parser.add_argument(
    "-o", "--output", help="Output file path", default="market_schedule.png"
)
args = parser.parse_args()

# --- Step 1: Load data from Google Sheet ---
sheet_id = "1HmZkAAB24gvqoZYpT3ndJMlEQ_gx5oJunkNYUlLWuU4"
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
df = pd.read_csv(csv_url)

# Print column names to help debug
print("Available columns:", df.columns.tolist())

# --- Step 2: Utility ---
def time_to_decimal(t):
    h, m = map(int, t.split(":"))
    return h + m / 60


# --- Step 3: Sort and position blocks to avoid overlaps ---
blocks = list(df.itertuples(index=False, name=None))
blocks = sorted(blocks, key=lambda b: time_to_decimal(b[0]))

lanes = []
positions = []

for block in blocks:
    start = time_to_decimal(block[0])
    end = time_to_decimal(block[1])
    placed = False
    for row_idx, row in enumerate(lanes):
        if all(end <= r[0] or start >= r[1] for r in row):
            row.append((start, end))
            positions.append((block, row_idx))
            placed = True
            break
    if not placed:
        lanes.append([(start, end)])
        positions.append((block, len(lanes) - 1))

# --- Step 4: Plot with improvements ---
fig, ax = plt.subplots(figsize=(14, 0.8 * len(lanes)))

# Auto-detect time range
min_time = min(time_to_decimal(row[0]) for row in blocks)
max_time = max(time_to_decimal(row[1]) for row in blocks)
# Round to nearest hour
min_time = max(0, int(min_time))
max_time = min(24, int(max_time + 1))  # Add 1 hour buffer, max 24

for (start_str, end_str, name, color), row in positions:
    start = time_to_decimal(start_str)
    end = time_to_decimal(end_str)
    # Use color as is, assuming it's the fourth column, without relying on column name
    ax.add_patch(
        Rectangle((start, row), end - start, 1, facecolor=color, edgecolor="black")
    )
    ax.text((start + end) / 2, row + 0.5, name, ha="center", va="center", fontsize=9)

# Add grid lines for better time reference
ax.grid(True, axis="x", linestyle="--", alpha=0.7)

# Create a color legend assuming fourth column is color
# Extract unique colors directly from blocks data
colors_dict = {}
for block in blocks:
    if len(block) >= 4:  # Make sure block has at least 4 elements
        color = block[3]
        name = block[2]
        if color not in colors_dict:
            colors_dict[color] = name

handles = [plt.Rectangle((0, 0), 1, 1, facecolor=c) for c in colors_dict.keys()]
labels = list(colors_dict.values())
if handles:  # Only create legend if we have colors
    plt.legend(
        handles, labels, title="Roles", loc="upper right", bbox_to_anchor=(1.1, 1)
    )

# Improve time display with half-hour marks
hours = range(min_time, max_time + 1)
all_ticks = []
all_labels = []
for h in hours:
    all_ticks.extend([h, h + 0.5])
    all_labels.extend([f"{h}:00", f"{h}:30"])
ax.set_xticks(all_ticks)
ax.set_xticklabels(all_labels, rotation=45, fontsize=8)

ax.set_xlim(min_time, max_time)
ax.set_ylim(0, len(lanes))
ax.set_yticks([])
ax.set_title("Hemelvaartsdag schema", fontsize=12)
plt.tight_layout()

# Add export function
def save_schedule(filename, dpi=300):
    plt.savefig(filename, dpi=dpi, bbox_inches="tight")
    print(f"Schedule saved as {filename}")


# Save the plot using the specified output path
save_schedule(args.output)
print("Schedule generated successfully. Exiting...")
# Don't use plt.show() in non-interactive environments
# plt.show()  # This line is now commented out
