import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

# Define the time frame and the tail length
time_frame = '1D'  # Change this to '5T', '1h', '1D', etc.
tail_length = 2
grid_size = 20  # Number of blocks per axis

# Define colors for each currency pair
colors = {
    'AUDUSD': 'blue',
    'GBPUSD': 'orange',
    'USDCHF': 'green',
    'USDJPY': 'red'
}

# Function to read and resample data
def read_and_resample(file_path, time_frame):
    df = pd.read_csv(file_path, parse_dates=['Date'], index_col='Date')
    resampled_df = df.resample(time_frame).agg({'Open': 'first', 
                                                'High': 'max', 
                                                'Low': 'min', 
                                                'Close': 'last', 
                                                'Volume': 'sum'}).dropna()
    return resampled_df

# Read data for each currency pair
data_directory = './DATA'
currency_pairs = [f for f in os.listdir(data_directory) if f.endswith('_C.csv')]

data = {}
for pair in currency_pairs:
    pair_name = pair.split('_')[0]
    file_path = os.path.join(data_directory, pair)
    data[pair_name] = read_and_resample(file_path, time_frame)

# Calculate Relative Strength (RS)
def calculate_rs(data, benchmark):
    rs = {}
    for pair in data:
        if pair != benchmark:
            rs[pair] = data[pair]['Close'] / data[benchmark]['Close']
    return rs

# Calculate RS-Ratio and RS-Momentum
def calculate_rrg_components(rs):
    rs_ratio = {}
    rs_momentum = {}
    for pair in rs:
        rs_ratio[pair] = rs[pair].rolling(window=10).mean() / rs[pair].rolling(window=40).mean()
        rs_momentum[pair] = rs_ratio[pair].diff()
        # Normalize the values
        rs_ratio[pair] = (rs_ratio[pair] - rs_ratio[pair].min()) / (rs_ratio[pair].max() - rs_ratio[pair].min())
        rs_momentum[pair] = (rs_momentum[pair] - rs_momentum[pair].min()) / (rs_momentum[pair].max() - rs_momentum[pair].min())
    return rs_ratio, rs_momentum

# Function to create background grid based on dot density and colors
def create_background(ax, rs_ratio, rs_momentum, num):
    heatmap = np.zeros((grid_size, grid_size, 3))
    counts = np.zeros((grid_size, grid_size))
    
    for pair in rs_ratio:
        x = rs_ratio[pair].values[:num]
        y = rs_momentum[pair].values[:num]
        color = np.array(plt.get_cmap('tab10')(list(colors.keys()).index(pair))[:3])
        
        if len(x) > 0 and len(y) > 0:
            for i in range(len(x)):
                if not np.isnan(x[i]) and not np.isnan(y[i]):
                    xi = int(x[i] * grid_size)
                    yi = int(y[i] * grid_size)
                    xi = min(xi, grid_size - 1)  # Ensure within bounds
                    yi = min(yi, grid_size - 1)  # Ensure within bounds
                    heatmap[yi, xi] += color
                    counts[yi, xi] += 1
    
    with np.errstate(divide='ignore', invalid='ignore'):
        heatmap = np.divide(heatmap, counts[..., None], where=counts[..., None] != 0)
    
    heatmap = np.clip(heatmap, 0, 1)  # Clip the values to the range 0-1
    
    for xi in range(grid_size):
        for yi in range(grid_size):
            if counts[yi, xi] > 0:
                color = heatmap[yi, xi]
                ax.add_patch(plt.Rectangle((xi/grid_size, yi/grid_size), 1/grid_size, 1/grid_size, color=color, alpha=1))
            else:
                ax.add_patch(plt.Rectangle((xi/grid_size, yi/grid_size), 1/grid_size, 1/grid_size, color='white', alpha=1))

# Function to update the graph
def update_graph(num, rs_ratio, rs_momentum, dates, tail_length):
    plt.cla()
    plt.title('Relative Rotation Graph (RRG)')
    plt.xlabel('Normalized RS-Ratio')
    plt.ylabel('Normalized RS-Momentum')
    plt.grid(True)
    
    # Create background grid
    create_background(plt.gca(), rs_ratio, rs_momentum, num)

    for pair in rs_ratio:
        x = rs_ratio[pair].values[:num]
        y = rs_momentum[pair].values[:num]
        
        if len(x) > 0 and len(y) > 0:
            sizes = np.linspace(100, 10, min(tail_length, len(x)))[::-1]  # Scale the dots from big to small
            plt.scatter(x[-len(sizes):], y[-len(sizes):], s=sizes, color=colors[pair])
            plt.plot(x[-len(sizes):], y[-len(sizes):], linestyle='-', linewidth=1, color=colors[pair])
    
    # Add a single date annotation for all pairs
    if num < len(dates):
        date_label = dates[num]
        plt.annotate(date_label.strftime('%Y-%m-%d %H:%M'), (0.95, 0.04), textcoords="offset points", xytext=(0,10), ha='center')

    plt.xlim(0, 1)
    plt.ylim(0, 1)

# Initialize the data for RRG
benchmark = 'EURUSD'
rs = calculate_rs(data, benchmark)
rs_ratio, rs_momentum = calculate_rrg_components(rs)
dates = data[benchmark].index

# Event handler to close the animation gracefully
def on_close(event):
    plt.close()
    ani.event_source.stop()

# Set up the figure and animation
fig, ax = plt.subplots(figsize=(10, 8))
fig.canvas.mpl_connect('close_event', on_close)
ani = animation.FuncAnimation(fig, update_graph, fargs=(rs_ratio, rs_momentum, dates, tail_length), frames=len(dates), interval=100, cache_frame_data=False)

plt.show()
