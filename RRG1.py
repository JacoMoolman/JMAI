import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

# Load the CSV files
data_dir = 'DATA2000'  # replace with your actual path
files = ['EURUSD_C.csv', 'GBPUSD_C.csv', 'USDCHF_C.csv', 'USDJPY_C.csv']

# Function to load data
def load_data(filename):
    df = pd.read_csv(f"{data_dir}/{filename}")
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    return df

# Load the data into dataframes
dfs = {file.split('_')[0]: load_data(file) for file in files}

# Function to resample data to hourly intervals
def resample_data(df):
    df_resampled = df.resample('h').ohlc()
    df_resampled['Volume'] = df['Volume'].resample('h').sum()
    df_resampled.columns = ['_'.join(col).strip() for col in df_resampled.columns.values]
    df_resampled.reset_index(inplace=True)
    return df_resampled

# Resample data for each dataframe
for key in dfs:
    dfs[key] = resample_data(dfs[key])

# Ensure all dataframes have the same time frames
common_index = dfs['EURUSD'].set_index('Date').index
for key in dfs:
    common_index = common_index.intersection(dfs[key].set_index('Date').index)

for key in dfs:
    dfs[key] = dfs[key][dfs[key]['Date'].isin(common_index)]

# Function to calculate RS-Ratio and RS-Momentum
def calculate_rs(df):
    df['Price_Relative'] = df['Close_close'] / df['Close_close'].iloc[0]  # Relative price to the first value
    df['RS-Ratio'] = df['Price_Relative'].rolling(window=10, min_periods=1).mean() * 100  # Adjusted window size
    df['RS-Momentum'] = df['RS-Ratio'].diff() * 100  # Scaled for better visibility
    df = df.fillna(0)  # Fill NaN values with 0
    return df

# Calculate RS-Ratio and RS-Momentum for each dataframe
for key in dfs:
    dfs[key] = calculate_rs(dfs[key])

# # Debug: Print out the first few rows of each dataframe to ensure calculations are correct
# for key in dfs:
#     print(f"{key} dataframe head:\n", dfs[key].head())

# Prepare the animation data by slicing the pre-calculated data
animation_data = []
tail_length = 1

for i in range(tail_length, len(common_index)):
    frame_data = {key: dfs[key].iloc[i-tail_length:i].copy() for key in dfs}
    animation_data.append(frame_data)

# # Debug: Print out the length of animation_data and the first frame
# print("Number of frames in animation data:", len(animation_data))
# print("First frame data:", animation_data[0])

# Plotting the RRG
fig, ax = plt.subplots()

colors = {'EURUSD': 'r', 'GBPUSD': 'g', 'USDCHF': 'b', 'USDJPY': 'y'}
quadrants = {'Leading': (1, 1), 'Weakening': (1, -1), 'Lagging': (-1, -1), 'Improving': (-1, 1)}

def update(num):
    ax.clear()
    
    for key, trail in animation_data[num].items():
        x = trail['RS-Ratio']
        y = trail['RS-Momentum']
        ax.plot(x, y, marker='o', color=colors[key], label=key)
        ax.annotate(key, (x.iloc[-1], y.iloc[-1]))

        # Add tails
        for i in range(len(trail) - 1):
            ax.plot(trail['RS-Ratio'].iloc[i:i+2], trail['RS-Momentum'].iloc[i:i+2], color=colors[key], alpha=0.6)
    
    # Add quadrant lines
    ax.axhline(y=0, color='k', linestyle='--')
    ax.axvline(x=100, color='k', linestyle='--')

    # Add labels for quadrants
    for quadrant, pos in quadrants.items():
        ax.text(100 + pos[0]*20, pos[1]*20, quadrant, fontsize=12, ha='center', va='center')

    # Set limits to zoom in on the relevant part of the graph
    ax.set_xlim([80, 120])
    ax.set_ylim([-50, 50])

    ax.set_xlabel('RS-Ratio')
    ax.set_ylabel('RS-Momentum')
    ax.legend()
    plt.title('Relative Rotation Graph')
    
    # Add timestamp
    current_time = animation_data[num]['EURUSD']['Date'].iloc[-1]
    ax.text(0.05, 0.95, str(current_time), transform=ax.transAxes, fontsize=12, verticalalignment='top')

ani = animation.FuncAnimation(fig, update, frames=len(animation_data), repeat=False)
plt.show()
