import pandas as pd
import matplotlib.pyplot as plt

# Custom variables
NUM_BARS = 500
H1_HEIGHT = 100
M5_HEIGHT = 100

# Read the CSV file
df_5min = pd.read_csv('DATA/EURUSD_C.csv', parse_dates=['Date'], usecols=['Date', 'Open', 'High', 'Low', 'Close'])

# Convert to H1 timeframe
df_1hour = df_5min.resample('H', on='Date').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last'
}).dropna()

# Select the first NUM_BARS rows for each dataframe
df_1hour = df_1hour.head(NUM_BARS)
df_5min = df_5min.head(NUM_BARS)

# Create the figure and subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(NUM_BARS/100, (H1_HEIGHT + M5_HEIGHT)/100), dpi=100)

# Plot H1 data
ax1.bar(range(NUM_BARS), df_1hour['High'] - df_1hour['Low'], bottom=df_1hour['Low'], width=1, color='k')
ax1.bar(range(NUM_BARS), df_1hour['Close'] - df_1hour['Open'], bottom=df_1hour['Open'], width=0.8, color=['g' if close > open else 'r' for close, open in zip(df_1hour['Close'], df_1hour['Open'])])

# Plot M5 data
ax2.bar(range(NUM_BARS), df_5min['High'] - df_5min['Low'], bottom=df_5min['Low'], width=1, color='k')
ax2.bar(range(NUM_BARS), df_5min['Close'] - df_5min['Open'], bottom=df_5min['Open'], width=0.8, color=['g' if close > open else 'r' for close, open in zip(df_5min['Close'], df_5min['Open'])])

# Remove all axes, labels, and ticks
for ax in [ax1, ax2]:
    ax.axis('off')

# Remove any padding
plt.subplots_adjust(left=0, right=1, top=1, bottom=0, hspace=0)

# Save the plot
plt.savefig('forex_chart.png', bbox_inches='tight', pad_inches=0)

plt.close()

print("Chart saved as forex_chart.png")