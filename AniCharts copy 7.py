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
MAIN_BARS_H1 = 300  # Number of bars in the main H1 chart
MAIN_BARS_M5 = 100   # Number of bars in the main M5 chart
ADDITIONAL_BARS = 4  # Number of bars for calculation (not shown)
PRICE_CHANGE_THRESHOLD = 0.005  # 0.5% change threshold (adjust as needed)
CHART_HEIGHT = 225  # Height of the chart in pixels

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

# Resample to 5-minute timeframe
df_m5 = df.resample('5T', label='right', closed='right').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}).dropna()

# Reset index to make Date a column again
df_h1.reset_index(inplace=True)
df_m5.reset_index(inplace=True)

# Create the figure and axes
dpi = plt.rcParams['figure.dpi']
fig = plt.figure(figsize=(MAIN_BARS_H1/dpi, CHART_HEIGHT/dpi), dpi=dpi)
gs = GridSpec(4, 1, height_ratios=[3, 1, 3, 1], hspace=0)  # Set hspace to 0
ax1 = fig.add_subplot(gs[0, 0])  # H1 price chart
ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)  # H1 volume chart
ax3 = fig.add_subplot(gs[2, 0])  # M5 price chart
ax4 = fig.add_subplot(gs[3, 0], sharex=ax3)  # M5 volume chart

# Remove labels
ax1.set_ylabel('')
ax2.set_ylabel('')
ax3.set_ylabel('')
ax4.set_xlabel('')
ax4.set_ylabel('')

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
    for ax in [ax1, ax2, ax3, ax4]:
        ax.clear()
    return []

# Variable to track if beep has been played
beep_played = False

# Function to update the plot for each frame
def update(frame):
    global beep_played
    for ax in [ax1, ax2, ax3, ax4]:
        ax.clear()
    
    # Calculate data for M5 chart
    end_time = df_m5['Date'].iloc[frame]
    start_time_m5 = end_time - pd.Timedelta(minutes=5*(MAIN_BARS_M5-1))
    main_data_m5 = df_m5[(df_m5['Date'] > start_time_m5) & (df_m5['Date'] <= end_time)].tail(MAIN_BARS_M5)
    
    # Calculate data for H1 chart
    start_time_h1 = end_time - pd.Timedelta(hours=MAIN_BARS_H1)
    main_data_h1 = df_h1[(df_h1['Date'] > start_time_h1) & (df_h1['Date'] <= end_time)]
    
    # Plot H1 chart
    plot_data(ax1, ax2, main_data_h1)
    
    # Plot M5 chart
    plot_data(ax3, ax4, main_data_m5)
    
    # Check for significant price change
    last_m5_price = main_data_m5['Close'].iloc[-1]
    previous_m5_price = main_data_m5['Close'].iloc[-2] if len(main_data_m5) > 1 else last_m5_price
    price_change = abs(last_m5_price / previous_m5_price - 1)
    
    if price_change > PRICE_CHANGE_THRESHOLD:
        if not beep_played:
            play_beep()
            beep_played = True
    else:
        beep_played = False
    
    # Set x-axis limits for H1 chart
    ax1.set_xlim(main_data_h1.index.min() - 1, main_data_h1.index.max() + 1)
    ax2.set_xlim(main_data_h1.index.min() - 1, main_data_h1.index.max() + 1)
    
    # Set x-axis limits for M5 chart
    ax3.set_xlim(main_data_m5.index.min() - 1, main_data_m5.index.max() + 1)
    ax4.set_xlim(main_data_m5.index.min() - 1, main_data_m5.index.max() + 1)
    
    # Remove x-axis labels for all charts
    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_xticklabels([])
    
    # Remove y-axis labels and ticks
    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_yticklabels([])
        ax.set_yticks([])
    
    # Add grid
    for ax in [ax1, ax2, ax3, ax4]:
        ax.grid(True, linestyle=':', alpha=0.6)
    
    # Remove spines
    for ax in [ax1, ax2, ax3, ax4]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
    
    return ax1.patches + ax1.lines + ax2.patches + ax3.patches + ax3.lines + ax4.patches

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
anim = FuncAnimation(fig, update, frames=range(MAIN_BARS_M5, len(df_m5)), init_func=init, blit=False, interval=0)

# Adjust the layout
plt.tight_layout()
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

# Show the plot
plt.show()