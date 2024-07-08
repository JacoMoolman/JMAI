import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

# Customizable variables
X = 2000
Y = 900
COLOR = 'green'  # Use any color name or hex code

def create_custom_image(x=X, y=Y, color=COLOR):
    # Create an image with specified dimensions
    fig, ax = plt.subplots(figsize=(x, y), dpi=1)
    
    # Create a plain rectangle with the specified color
    rectangle = np.ones((y, x, 3))
    color_rgb = mcolors.to_rgb(color)
    rectangle[:, :] = color_rgb

    # Display the plain rectangle
    ax.imshow(rectangle, aspect='auto')
    
    # Remove the axes for a cleaner image
    ax.axis('off')
    
    # Display the image
    plt.show()

# Create and display the image with the custom settings
create_custom_image()
