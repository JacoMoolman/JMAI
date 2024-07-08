import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
from matplotlib.gridspec import GridSpec
import platform

# Determine the operating system and import appropriate module for beep
if platform.system() == "Windows":
    import winsound
else:
    import os

# User-defined variables
MAIN_BARS = 300  # Number of bars in the main chart
ADDITIONAL_BARS = 4  # Number of bars for calculation (not shown)
PRICE_CHANGE_THRESHOLD = 0.005  # 0.5% change threshold (adjust as needed)

# Function to play a beep
def play_beep():
    if platform.system() == "Windows":
        winsound.Beep(1000, 200)  # Frequency: 1000Hz, Duration: 200ms
    else:
        os.system('play -nq -t alsa synth 0.2 sine 1000')  # For Linux/macOS

# Read the CSV file
df = pd.read_csv('DATA/EURUSD_C.csv', parse_dates=['Date'])

# Sort the dataframe by date
df = df.sort_values('Date')

# Set the Date column as the index
df.set_index('Date', inplace=True)

# Resample to 1-hour timeframe
df_h1 = df.resample('1H', label='right', closed='right').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}).dropna()

# Reset index to make Date a column again
df_h1.reset_index(inplace=True)

# Create the figure and axes
fig = plt.figure(figsize=(16, 8))
gs = GridSpec(2, 1, height_ratios=[3, 1])
ax1 = fig.add_subplot(gs[0, 0])  # Main price chart
ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)  # Main volume chart

# Set the titles and labels
# fig.suptitle('EURUSD Price Movement (H1) - Normalized', fontsize=16)
ax1.set_ylabel('Normalized Price')
ax2.set_xlabel('Date')
ax2.set_ylabel('Normalized Volume')

# Function to create a single candlestick
def create_candlestick(ax, row, y_min, y_max):
    bottom = (min(row['Open'], row['Close']) - y_min) / (y_max - y_min)
    top = (max(row['Open'], row['Close']) - y_min) / (y_max - y_min)
    height = top - bottom
    color = 'g' if row['Close'] >= row['Open'] else 'r'
    
    # Draw the wick first (behind the body)
    wick_low = (row['Low'] - y_min) / (y_max - y_min)
    wick_high = (row['High'] - y_min) / (y_max - y_min)
    ax.plot([row.name, row.name], [wick_low, wick_high], color='black', linewidth=1, zorder=1)
    
    # Draw the body
    rect = Rectangle((row.name - 0.4, bottom), 0.8, height, color=color, zorder=2)
    ax.add_patch(rect)

# Function to create a single volume bar
def create_volume_bar(ax, row, vol_max):
    color = 'g' if row['Close'] >= row['Open'] else 'r'
    height = row['Volume'] / vol_max
    rect = Rectangle((row.name - 0.4, 0), 0.8, height, color=color, alpha=0.5)
    ax.add_patch(rect)

# Function to initialize the plot
def init():
    for ax in [ax1, ax2]:
        ax.clear()
    return []

# Variable to track if beep has been played
beep_played = False

# Function to update the plot for each frame
def update(frame):
    global beep_played
    for ax in [ax1, ax2]:
        ax.clear()
    
    main_data = df_h1.iloc[max(0, frame-MAIN_BARS):frame]
    additional_data = df_h1.iloc[frame:frame+ADDITIONAL_BARS]
    
    # Plot main chart
    plot_data(ax1, ax2, main_data)
    
    # Check for significant price change
    last_main_price = main_data['Close'].iloc[-1]
    max_change = max(abs(additional_data['Close'] / last_main_price - 1))
    
    if max_change > PRICE_CHANGE_THRESHOLD:
        if not beep_played:
            play_beep()
            beep_played = True
    else:
        beep_played = False
    
    # Set x-axis limits and labels for main chart
    ax1.set_xlim(main_data.index.min() - 1, main_data.index.max() + 1)
    ax2.set_xlim(main_data.index.min() - 1, main_data.index.max() + 1)
    ax1.set_xticks(main_data.index[::10])  # Show every 10th date
    ax1.set_xticklabels(main_data['Date'].dt.strftime('%Y-%m-%d %H:%M')[::10], rotation=45, ha='right')
    
    # Remove x-axis labels from volume chart
    ax2.set_xticklabels([])
    
    # Add grid
    for ax in [ax1, ax2]:
        ax.grid(True, linestyle=':', alpha=0.6)
    
    return ax1.patches + ax1.lines + ax2.patches

def plot_data(price_ax, volume_ax, data):
    y_min, y_max = data[['Low', 'High']].min().min(), data[['Low', 'High']].max().max()
    vol_max = data['Volume'].max()
    
    # Plot candlesticks
    for _, row in data.iterrows():
        create_candlestick(price_ax, row, y_min, y_max)
    
    # Plot volume bars
    for _, row in data.iterrows():
        create_volume_bar(volume_ax, row, vol_max)
    
    # Set y-axis limits
    price_ax.set_ylim(0, 1)
    volume_ax.set_ylim(0, 1)

# Create the animation
anim = FuncAnimation(fig, update, frames=range(MAIN_BARS, len(df_h1)), init_func=init, blit=False, interval=200)

# Show the plot
plt.tight_layout()
plt.show()

# To save the animation (optional)
# anim.save('eurusd_h1_normalized_candlestick_animation.gif', writer='pillow', fps=5)
