import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

# Define the time frame and the tail length
time_frame = '1h'  # Change this to '5T', '1h', '1D', etc.
tail_length = 5

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
    return rs_ratio, rs_momentum

# Function to update the graph
def update_graph(num, rs_ratio, rs_momentum, dates, tail_length):
    plt.cla()
    plt.title('Relative Rotation Graph (RRG)')
    plt.xlabel('RS-Ratio')
    plt.ylabel('RS-Momentum')
    plt.grid(True)
    
    # Draw quadrant lines
    plt.axhline(y=0, color='k', linewidth=0.5)
    plt.axvline(x=1, color='k', linewidth=0.5)
    
    for pair in rs_ratio:
        x = rs_ratio[pair].values[:num]
        y = rs_momentum[pair].values[:num]
        plt.plot(x[-tail_length:], y[-tail_length:], marker='o', label=pair)
    
    # Add a single date annotation for all pairs
    if num < len(dates):
        date_label = dates[num]
        plt.annotate(date_label.strftime('%Y-%m-%d %H:%M'), (0.95, 0.04), textcoords="offset points", xytext=(0,10), ha='center')
    
    plt.xlim(0.95, 1.05)
    plt.ylim(-0.05, 0.05)
    plt.legend()

# Initialize the data for RRG
benchmark = 'EURUSD'
rs = calculate_rs(data, benchmark)
rs_ratio, rs_momentum = calculate_rrg_components(rs)
dates = data[benchmark].index

# Set up the figure and animation
fig = plt.figure()
ani = animation.FuncAnimation(fig, update_graph, fargs=(rs_ratio, rs_momentum, dates, tail_length), frames=len(dates), interval=100, cache_frame_data=False)

plt.show()
