import pandas as pd
from PIL import Image
import os

# Custom variables
NUM_BARS = 500  # Number of bars to display
H1_HEIGHT = 100  # Height of H1 chart in pixels
M5_HEIGHT = 100  # Height of M5 chart in pixels
TOTAL_HEIGHT = H1_HEIGHT + M5_HEIGHT

# Ensure the output directory exists
os.makedirs('DATA/TEST1IMAGES', exist_ok=True)

# Read the CSV file
df_5min = pd.read_csv('DATA/EURUSD_C.csv', parse_dates=['Date'], usecols=['Date', 'Open', 'High', 'Low', 'Close'])

# Convert to H1 timeframe
df_1hour = df_5min.resample('h', on='Date').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last'
}).dropna()

def normalize_data(df_h1, df_m5):
    price_columns = ['Open', 'High', 'Low', 'Close']
    price_data = pd.concat([df_h1[price_columns], df_m5[price_columns]])
    min_price = price_data.min().min()
    max_price = price_data.max().max()
    
    df_h1_norm = df_h1.copy()
    df_m5_norm = df_m5.copy()
    
    for col in price_columns:
        df_h1_norm[col] = (df_h1[col] - min_price) / (max_price - min_price)
        df_m5_norm[col] = (df_m5[col] - min_price) / (max_price - min_price)
    
    return df_h1_norm, df_m5_norm

def plot_data(df, start_y, height):
    for i, (_, row) in enumerate(df.iterrows()):
        high = int(row['High'] * (height - 1))
        low = int(row['Low'] * (height - 1))
        open_price = int(row['Open'] * (height - 1))
        close_price = int(row['Close'] * (height - 1))
        
        # Plot high-low (black)
        for y in range(low, high + 1):
            pixels[i, start_y + height - 1 - y] = (0, 0, 0)
        
        # Plot open-close
        color = (0, 0, 255) if close_price >= open_price else (255, 0, 0)  # Blue for up, Red for down
        start = min(open_price, close_price)
        end = max(open_price, close_price)
        for y in range(start, end + 1):
            pixels[i, start_y + height - 1 - y] = color

# Iterate through each 5-minute entry
for i in range(len(df_5min) - NUM_BARS + 1):
    # Select the current window of data
    df_5min_window = df_5min.iloc[i:i+NUM_BARS]
    df_1hour_window = df_1hour[df_1hour.index >= df_5min_window.iloc[0]['Date']]
    df_1hour_window = df_1hour_window[df_1hour_window.index <= df_5min_window.iloc[-1]['Date']]

    # Normalize data for both timeframes
    df_1hour_norm, df_5min_norm = normalize_data(df_1hour_window, df_5min_window)

    # Create a new image
    img = Image.new('RGB', (NUM_BARS, TOTAL_HEIGHT), color='white')
    pixels = img.load()

    # Plot H1 data
    plot_data(df_1hour_norm, 0, H1_HEIGHT)

    # Plot M5 data
    plot_data(df_5min_norm, H1_HEIGHT, M5_HEIGHT)

    # Save the image
    img.save(f'DATA/TEST1IMAGES/forex_chart_{i:05d}.png')

    if i % 100 == 0:
        print(f"Processed {i} images")

print("All images saved in DATA/TEST1IMAGES/")