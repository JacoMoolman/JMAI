import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

# Define the time frame and the tail length
time_frame = '1D'  # Change this to '5T', '1h', '1D', etc.
tail_length = 20

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

# Function to update the graph
def update_graph(num, rs_ratio, rs_momentum, dates, tail_length):
    plt.cla()
    plt.title('Relative Rotation Graph (RRG)')
    plt.xlabel('Normalized RS-Ratio')
    plt.ylabel('Normalized RS-Momentum')
    plt.grid(True)

    # Color the quadrants
    plt.axhline(y=0.5, color='k', linewidth=0.5, linestyle='--')
    plt.axvline(x=0.5, color='k', linewidth=0.5, linestyle='--')
    
    plt.fill_between([0, 0.5], 0.5, 1, color='green', alpha=0.1)  # Leading
    plt.fill_between([0.5, 1], 0.5, 1, color='yellow', alpha=0.1)  # Weakening
    plt.fill_between([0, 0.5], 0, 0.5, color='red', alpha=0.1)  # Lagging
    plt.fill_between([0.5, 1], 0, 0.5, color='blue', alpha=0.1)  # Improving

    for pair in rs_ratio:
        x = rs_ratio[pair].values[:num]
        y = rs_momentum[pair].values[:num]
        
        if len(x) > 0 and len(y) > 0:
            sizes = np.linspace(100, 10, min(tail_length, len(x)))[::-1]  # Scale the dots from big to small
            plt.scatter(x[-len(sizes):], y[-len(sizes):], s=sizes)
            plt.plot(x[-len(sizes):], y[-len(sizes):], linestyle='-', linewidth=1)
    
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

# Set up the figure and animation
fig, ax = plt.subplots(figsize=(10, 8))
ani = animation.FuncAnimation(fig, update_graph, fargs=(rs_ratio, rs_momentum, dates, tail_length), frames=len(dates), interval=100, cache_frame_data=False)

plt.show()
