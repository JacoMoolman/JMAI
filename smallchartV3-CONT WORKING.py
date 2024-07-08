import pandas as pd
import numpy as np
from PIL import Image
import os
from datetime import datetime, timedelta

# Custom variables
START_END_DATE = '2000-02-01 00:00:00'  # Start date and time
NUM_BARS = 500  # Number of bars to display
H1_HEIGHT = 250  # Height of H1 chart in pixels
M5_HEIGHT = 150  # Height of M5 chart in pixels
TOTAL_HEIGHT = H1_HEIGHT + M5_HEIGHT
FUTURE_BARS = 4  # Number of bars to look ahead for price prediction
PRICE_CHANGE_THRESHOLD = 0.005  # 0.5% change threshold

# Create directory for images if it doesn't exist
OUTPUT_DIR = 'DATA/TEST1IMAGES'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read the CSV file
df_5min = pd.read_csv('DATA/EURUSD_C.csv', parse_dates=['Date'], usecols=['Date', 'Open', 'Close', 'High', 'Low'])
df_5min.set_index('Date', inplace=True)

# Clean the data
df_5min = df_5min.dropna()  # Remove rows with NaN values
df_5min = df_5min.replace([np.inf, -np.inf], np.nan).dropna()  # Remove rows with inf values

# Convert to H1 timeframe once
df_1hour = df_5min.resample('h').agg({
    'Open': 'first',
    'Close': 'last',
    'High': 'max',
    'Low': 'min'
}).dropna()

def normalize_data(df):
    price_data = df[['Open', 'Close', 'High', 'Low']]
    min_price = price_data.min().min()
    max_price = price_data.max().max()
    normalized = (price_data - min_price) / (max_price - min_price)
    return normalized.fillna(0).replace([np.inf, -np.inf], 0)  # Replace NaN and inf with 0

def plot_data(df, start_y, height, pixels):
    normalized_df = normalize_data(df)
    img_slice = np.zeros((height, NUM_BARS, 3), dtype=np.uint8)
    
    # Ensure we don't exceed the available data
    num_bars = min(NUM_BARS, len(normalized_df))
    
    for col in ['Open', 'Close', 'High', 'Low']:
        normalized_df[col] = (normalized_df[col] * (height - 1)).clip(0, height - 1).astype(int)
    
    for i in range(num_bars):
        low, high = normalized_df['Low'].iloc[i], normalized_df['High'].iloc[i]
        open_, close = normalized_df['Open'].iloc[i], normalized_df['Close'].iloc[i]
        
        # Plot high-low line
        img_slice[height - 1 - high:height - 1 - low, i] = [255, 255, 0]  # Yellow
        
        # Overwrite with blue for high prices
        blue_start = max(close, open_)
        img_slice[height - 1 - high:height - 1 - blue_start, i] = [0, 0, 255]  # Blue
        
        # Plot open-close bar
        color = [0, 255, 0] if close >= open_ else [255, 0, 0]  # Green or Red
        start, end = min(open_, close), max(open_, close)
        img_slice[height - 1 - end:height - 1 - start, i] = color
    
    pixels[start_y:start_y+height, :num_bars] = img_slice[:, :num_bars]

def check_future_price(df, current_index):
    if current_index + FUTURE_BARS >= len(df):
        return 'END_OF_DATA'
    
    current_price = df.iloc[current_index]['Close']
    future_prices = df.iloc[current_index + 1 : current_index + FUTURE_BARS + 1]['Close']
    
    max_change = (future_prices.max() / current_price) - 1
    min_change = (future_prices.min() / current_price) - 1
    
    if max_change > PRICE_CHANGE_THRESHOLD:
        print("UP")
        return 'UP'
    elif min_change < -PRICE_CHANGE_THRESHOLD:
        print("DOWN")
        return 'DOWN'
    else:
        return 'NEUTRAL'

start_date = pd.to_datetime(START_END_DATE)
end_date = df_1hour.index[-1] - timedelta(hours=FUTURE_BARS)

# Find the closest starting index
start_index = df_1hour.index.searchsorted(start_date)
if start_index == len(df_1hour):
    start_index -= 1

up_count, down_count, neutral_count = 0, 0, 0

# Initialize the 5-minute window
m5_start_time = df_1hour.index[start_index] - timedelta(minutes=5*NUM_BARS)
m5_end_time = df_1hour.index[start_index]
df_5min_window = df_5min.loc[m5_start_time:m5_end_time]

for current_index in range(start_index, len(df_1hour) - FUTURE_BARS):
    current_time = df_1hour.index[current_index]
    
    if current_time > end_date:
        break

    if current_index < NUM_BARS:
        continue

    # Check future price movement
    price_direction = check_future_price(df_1hour, current_index)

    if price_direction == 'UP':
        up_count += 1
    elif price_direction == 'DOWN':
        down_count += 1
    else:
        neutral_count += 1

    # Create a new image with black background
    pixels = np.zeros((TOTAL_HEIGHT, NUM_BARS, 3), dtype=np.uint8)

    # Plot H1 data
    h1_data = df_1hour.iloc[current_index-NUM_BARS+1:current_index+1]
    plot_data(h1_data, 0, H1_HEIGHT, pixels)

    # Update 5-minute window
    m5_end_time = current_time
    m5_start_time = m5_end_time - timedelta(minutes=5*NUM_BARS)
    new_m5_data = df_5min.loc[df_5min_window.index[-1]:m5_end_time]
    df_5min_window = pd.concat([df_5min_window, new_m5_data]).iloc[-NUM_BARS:]

    # Plot M5 data
    plot_data(df_5min_window, H1_HEIGHT, M5_HEIGHT, pixels)

    # Convert numpy array to PIL Image
    img = Image.fromarray(pixels)

    # Save the image with a unique filename including the price direction
    timestamp = current_time.strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(OUTPUT_DIR, f'forex_chart_{timestamp}_{price_direction}.png')
    img.save(image_path)

    if (up_count + down_count + neutral_count) % 100 == 0:
        print(f"Processed: {current_time}, UP: {up_count}, DOWN: {down_count}, NEUTRAL: {neutral_count}")

print(f"Chart generation complete. Final counts - UP: {up_count}, DOWN: {down_count}, NEUTRAL: {neutral_count}")