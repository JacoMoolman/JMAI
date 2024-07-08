import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

data_dir = 'DATA'  
files = ['EURUSD_C.csv', 'GBPUSD_C.csv', 'USDCHF_C.csv', 'USDJPY_C.csv']


def load_data(filename):
    df = pd.read_csv(f"{data_dir}/{filename}")
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    return df


dfs = {file.split('_')[0]: load_data(file) for file in files}


def resample_data(df):
    df_resampled = df.resample('D').ohlc()
    df_resampled['Volume'] = df['Volume'].resample('D').sum()
    df_resampled.columns = ['_'.join(col).strip() for col in df_resampled.columns.values]
    df_resampled.reset_index(inplace=True)
    return df_resampled


for key in dfs:
    dfs[key] = resample_data(dfs[key])


for key in dfs:
    print(f"{key} resampled dataframe:\n", dfs[key].head())


def calculate_and_normalize_rs_relative(df, reference_df):
    df = df[df['Date'].isin(reference_df['Date'])]
    df['Price_Relative'] = df['Close_close'] / reference_df['Close_close']
    df['RS-Ratio'] = df['Price_Relative'].rolling(window=10).mean() * 100  # Adjusted window size
    df['RS-Momentum'] = df['RS-Ratio'].diff() * 100  # Scaled for better visibility
    # Normalize RS-Ratio and RS-Momentum
    df['RS-Ratio'] = (df['RS-Ratio'] - df['RS-Ratio'].min()) / (df['RS-Ratio'].max() - df['RS-Ratio'].min())
    df['RS-Momentum'] = (df['RS-Momentum'] - df['RS-Momentum'].min()) / (df['RS-Momentum'].max() - df['RS-Momentum'].min())
    return df

# Calculate and normalize RS-Ratio and RS-Momentum for each dataframe relative to EURUSD
reference_df = dfs['EURUSD'].copy()
for key in dfs:
    if key != 'EURUSD':
        dfs[key] = calculate_and_normalize_rs_relative(dfs[key], reference_df)

# Prepare animation data
animation_data = []

# Iterate through each day in the EURUSD data
for i in range(len(dfs['EURUSD'])):
    current_date = dfs['EURUSD'].iloc[i]['Date']
    frame_data = {}
    for key in dfs:
        temp_df = dfs[key][dfs[key]['Date'] <= current_date].copy()
        if key != 'EURUSD':
            temp_df = calculate_and_normalize_rs_relative(temp_df, reference_df[reference_df['Date'] <= current_date])
        frame_data[key] = temp_df.iloc[-20:].copy()
    animation_data.append((current_date, frame_data))

# Debug: Print the first frame of animation data
print("First frame of animation data:", animation_data[0])

# Plotting the RRG
fig, ax = plt.subplots()

colors = {'EURUSD': 'r', 'GBPUSD': 'g', 'USDCHF': 'b', 'USDJPY': 'y'}
quadrants = {'Leading': (1, 1), 'Weakening': (1, -1), 'Lagging': (-1, -1), 'Improving': (-1, 1)}

def update(num):
    current_date, trails = animation_data[num]
    ax.clear()
    
    for key, trail in trails.items():
        if key != 'EURUSD' and not trail.empty:
            x = trail['RS-Ratio']
            y = trail['RS-Momentum']
            ax.plot(x, y, marker='o', color=colors[key], label=key)
            ax.annotate(key, (x.iloc[-1], y.iloc[-1]))
            
            # Add tails
            for i in range(len(trail) - 1):
                ax.plot(trail['RS-Ratio'].iloc[i:i+2], trail['RS-Momentum'].iloc[i:i+2], color=colors[key], alpha=0.6)
    
    # Add quadrant lines
    ax.axhline(y=0.5, color='k', linestyle='--')  # Updated for normalized range [0, 1]
    ax.axvline(x=0.5, color='k', linestyle='--')  # Updated for normalized range [0, 1]

    # Add labels for quadrants
    for quadrant, pos in quadrants.items():
        ax.text(0.5 + pos[0]*0.25, 0.5 + pos[1]*0.25, quadrant, fontsize=12, ha='center', va='center')  # Updated for normalized range [0, 1]

    # Set limits to zoom in on the relevant part of the graph
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])

    ax.set_xlabel('Normalized RS-Ratio')
    ax.set_ylabel('Normalized RS-Momentum')
    ax.legend()
    plt.title('Normalized Relative Rotation Graph')
    
    # Add timestamp
    ax.text(0.05, 0.95, str(current_date.date()), transform=ax.transAxes, fontsize=12, verticalalignment='top')

ani = animation.FuncAnimation(fig, update, frames=len(animation_data), repeat=False)
plt.show()
