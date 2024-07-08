import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.animation import FuncAnimation
from realtimesim import split_file, move_line

# Define the data directory
data_dir = 'STREAM'

# Get all '_past.csv' files from the STREAM directory
files = [f for f in os.listdir(data_dir) if f.endswith('_C_past.csv')]

# Determine the number of lines to read (X)
X = 50

def load_data(filename):
    df = pd.read_csv(f"{data_dir}/{filename}", parse_dates=['Date'], index_col='Date')
    return df.tail(X)

def calculate_and_normalize_rs_relative(df, reference_df):
    df['Price_Relative'] = df['Close'] / reference_df['Close']
    df['RS-Ratio'] = df['Price_Relative'].rolling(window=10).mean() * 100
    df['RS-Momentum'] = df['RS-Ratio'].diff() * 100
    df['RS-Ratio'] = (df['RS-Ratio'] - df['RS-Ratio'].min()) / (df['RS-Ratio'].max() - df['RS-Ratio'].min())
    df['RS-Momentum'] = (df['RS-Momentum'] - df['RS-Momentum'].min()) / (df['RS-Momentum'].max() - df['RS-Momentum'].min())
    return df

colors = {'AUDUSD': 'r', 'EURUSD': 'b', 'GBPUSD': 'g', 'USDJPY': 'y'}
quadrants = {'Leading': (1, 1), 'Weakening': (1, -1), 'Lagging': (-1, -1), 'Improving': (-1, 1)}

fig, ax = plt.subplots(figsize=(10, 8))

def update(frame):
    ax.clear()
    
    # Load data for each currency pair
    dfs = {file.split('_')[0]: load_data(file) for file in files}
    
    # Calculate and normalize RS-Ratio and RS-Momentum for each dataframe relative to EURUSD
    reference_df = dfs['EURUSD'].copy()
    for key in dfs:
        if key != 'EURUSD':
            dfs[key] = calculate_and_normalize_rs_relative(dfs[key], reference_df)
    
    for key, df in dfs.items():
        if key != 'EURUSD':
            valid_data = df.dropna(subset=['RS-Ratio', 'RS-Momentum'])
            x = valid_data['RS-Ratio']
            y = valid_data['RS-Momentum']
            
            if len(x) > 0 and len(y) > 0:
                ax.plot(x, y, marker='o', color=colors[key], label=key)
                ax.annotate(key, (x.iloc[-1], y.iloc[-1]))
                
                tail_length = min(20, len(x))
                for i in range(-tail_length, -1):
                    ax.plot(x.iloc[i:i+2], y.iloc[i:i+2], color=colors[key], alpha=0.6)
            else:
                print(f"Warning: No valid data points for {key}")

    # Add quadrant lines
    ax.axhline(y=0.5, color='k', linestyle='--')
    ax.axvline(x=0.5, color='k', linestyle='--')

    # Add labels for quadrants
    for quadrant, pos in quadrants.items():
        ax.text(0.5 + pos[0]*0.25, 0.5 + pos[1]*0.25, quadrant, fontsize=12, ha='center', va='center')

    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.set_xlabel('Normalized RS-Ratio')
    ax.set_ylabel('Normalized RS-Momentum')
    ax.legend()
    ax.set_title('Normalized Relative Rotation Graph')

    # Add timestamp of the last date in the data
    last_date = dfs['EURUSD'].index[-1]
    ax.text(0.05, 0.95, str(last_date.date()), transform=ax.transAxes, fontsize=12, verticalalignment='top')

    # Move lines for each currency pair
    move_line('AUDUSD_C')
    move_line('EURUSD_C')
    move_line('GBPUSD_C')
    move_line('USDJPY_C')
    print("DONE")

# Create the animation
ani = FuncAnimation(fig, update, frames=100, interval=1000, repeat=False)

plt.show()