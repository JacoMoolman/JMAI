import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

H1_bars=50
# Define the dimensions in pixels for the figure
fig_width_pixels = 2000
fig_height_pixels = 300

# Create the figure with the specified size in pixels
fig = plt.figure(figsize=(fig_width_pixels, fig_height_pixels), dpi=1)

# Add axes that span the entire figure
ax = fig.add_axes([0, 0, 1, 1])

# Define the properties of the rectangle in pixel units
x = 0  # X position
y = 0  # Y position
width = fig_width_pixels  # Width of the rectangle
height = fig_height_pixels  # Height of the rectangle

# Add the rectangle to the plot
# Note: Since the figure and axis are both in the same pixel space, we need to convert pixels to axis coordinates.
ax.add_patch(Rectangle((x, y), width, height, edgecolor='black', facecolor='blue', transform=ax.transAxes))

# Set the limits of the plot to match the rectangle's size in pixels
ax.set_xlim(0, width)
ax.set_ylim(0, height)

# Remove axis for better visualization
ax.axis('off')

# Display the plot
plt.show()
