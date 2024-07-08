import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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

# Function to calculate RS-Ratio and RS-Momentum
def calculate_rs(df):
    df['Price_Relative'] = df['Close_close'] / df['Close_close'].iloc[0]  # Relative price to the first value
    df['RS-Ratio'] = df['Price_Relative'].rolling(window=10).mean() * 100  # Adjusted window size
    df['RS-Momentum'] = df['RS-Ratio'].diff() * 100  # Scaled for better visibility
    return df

# Calculate RS-Ratio and RS-Momentum for each dataframe
for key in dfs:
    dfs[key] = calculate_rs(dfs[key])

# Extract the last 5 data points for each currency pair
trails = {key: dfs[key].iloc[-20:] for key in dfs}

# Plotting the RRG
fig, ax = plt.subplots()

colors = {'EURUSD': 'r', 'GBPUSD': 'g', 'USDCHF': 'b', 'USDJPY': 'y'}
quadrants = {'Leading': (1, 1), 'Weakening': (1, -1), 'Lagging': (-1, -1), 'Improving': (-1, 1)}

for key, trail in trails.items():
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
plt.show()
