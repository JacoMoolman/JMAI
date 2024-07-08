import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import mplfinance as mpf

# Set the interval for animation (in milliseconds)
animation_interval = 20  # Adjust this value to change the speed (1000 ms = 1 second)

# Set the window size for the number of bars in the chart
window_size = 500  # Adjust this value to change the number of bars displayed

# Load the data
file_path = 'DATA/GBPUSD_C.csv'
data = pd.read_csv(file_path)

# Convert the Date column to datetime and set it as index
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

# Initialize the figure and axes
fig = plt.figure(figsize=(10, 6))
ax1 = fig.add_axes([0.05, 0.3, 0.9, 0.6])
ax2 = fig.add_axes([0.05, 0.1, 0.9, 0.2], sharex=ax1)

# Function to animate the candlestick chart with volume
def animate(start):
    end = start + window_size
    if end > len(data):
        end = len(data)
    subset = data[start:end]
    ax1.clear()
    ax2.clear()
    
    # Plot candlestick on ax1
    mpf.plot(subset, type='candle', ax=ax1, volume=ax2, style='charles')
    ax1.set_title(f'Volume from {subset.index[0]} to {subset.index[-1]}')
    ax1.set_ylabel('Price')
    ax2.set_ylabel('Volume')

# Set up the animation
ani = animation.FuncAnimation(fig, animate, frames=range(0, len(data)-window_size), interval=animation_interval, repeat=False)

# Display the plot
plt.show()
