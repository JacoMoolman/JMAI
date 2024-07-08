import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import random

# Number of bars for H1
H1_bars = 50

# WH for H1 Graph so far
fig_width_pixels = 2000
fig_height_pixels = 300

# Create the figure with the specified size in pixels
fig = plt.figure(figsize=(fig_width_pixels / 100, fig_height_pixels / 100), dpi=100)

ax = fig.add_axes([0, 0, 1, 1])
x = 0
y = 0
width = 1
height = 1  

# Add the blue rectangle to the plot
ax.add_patch(Rectangle((x, y), width, height, edgecolor='black', facecolor='blue', transform=ax.transAxes))

# Define the width of each bar
bar_width = 1 / H1_bars  # Width of each bar as a fraction of the axes width

# Add the bars to the plot and number them
for i in range(H1_bars):
    bar_x = i * bar_width  # X position of each bar
    bottom = random.uniform(0, 0.5)  # Bottom between 0 and 0.5 in axes units
    top = random.uniform(0.5, 1)  # Top between 0.5 and 1 in axes units
    bar_height = top - bottom  # Height of the bar
    
    ax.add_patch(Rectangle((bar_x, bottom), bar_width, bar_height, edgecolor='white', facecolor='red', lw=1, transform=ax.transAxes))
    # Add the number at the center of each bar
    ax.text(bar_x + bar_width / 2, bottom + bar_height / 2, str(i + 1), ha='center', va='center', color='white', fontsize=12, transform=ax.transAxes)

# Set the limits of the plot to match the rectangle's size in axes units
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# Remove axis for better visualization
ax.axis('off')

# Display the plot
plt.show()
