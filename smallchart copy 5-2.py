import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg

# Custom variables
NUM_BARS = 100  # Number of bars to display
H1_HEIGHT = 200  # Height of H1 chart in pixels
M5_HEIGHT = 100  # Height of M5 chart in pixels

# Read the CSV file
df_5min = pd.read_csv('DATA/EURUSD_C.csv', parse_dates=['Date'], usecols=['Date', 'Open', 'Close'])

# Convert to H1 timeframe
df_1hour = df_5min.resample('H', on='Date').agg({
    'Open': 'first',
    'Close': 'last'
}).dropna()

# Select the last NUM_BARS rows for each dataframe
df_1hour = df_1hour.tail(NUM_BARS)
df_5min = df_5min.tail(NUM_BARS)

# Create the figure and subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(NUM_BARS/100, (H1_HEIGHT + M5_HEIGHT)/100), dpi=100)

def plot_candlesticks(ax, df):
    for i, (_, row) in enumerate(df.iterrows()):
        color = 'green' if row['Close'] >= row['Open'] else 'red'
        y_min, y_max = min(row['Open'], row['Close']), max(row['Open'], row['Close'])
        ax.vlines(i, y_min, y_max, colors=color, linewidths=1)

# Plot H1 data
plot_candlesticks(ax1, df_1hour)

# Plot M5 data
plot_candlesticks(ax2, df_5min)

# Remove all axes, labels, and ticks
for ax in [ax1, ax2]:
    ax.axis('off')
    ax.set_xlim(0, NUM_BARS - 1)

# Remove any padding
plt.subplots_adjust(left=0, right=1, top=1, bottom=0, hspace=0)

# Render the plot to a canvas
canvas = FigureCanvasAgg(fig)
canvas.draw()

# Get the renderer and extract the image data
renderer = canvas.get_renderer()
raw_data = renderer.buffer_rgba()

# Create a new figure with exact pixel dimensions
fig_clean = plt.figure(figsize=(NUM_BARS/100, (H1_HEIGHT + M5_HEIGHT)/100), dpi=100)
ax_clean = fig_clean.add_axes([0, 0, 1, 1])
ax_clean.imshow(raw_data, aspect='auto', interpolation='nearest')
ax_clean.axis('off')

# Save the clean plot
plt.savefig('forex_chart_clean_no_shadows.png', bbox_inches='tight', pad_inches=0, dpi=100)
plt.close(fig)
plt.close(fig_clean)

print("Chart saved as forex_chart_clean_no_shadows.png")