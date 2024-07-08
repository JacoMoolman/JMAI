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

# Convert to H1 timeframe
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
    if min_price == max_price:
        return price_data - min_price
    return (price_data - min_price) / (max_price - min_price)

def plot_data(df, start_y, height, pixels):
    normalized_df = normalize_data(df)
    normalized_df = normalized_df.replace([np.inf, -np.inf, np.nan], 0)
    
    opens = (normalized_df['Open'] * (height - 1)).astype(int)
    closes = (normalized_df['Close'] * (height - 1)).astype(int)
    highs = (normalized_df['High'] * (height - 1)).astype(int)
    lows = (normalized_df['Low'] * (height - 1)).astype(int)
    
    for i in range(min(NUM_BARS, len(normalized_df))):
        low, high = lows.iloc[i], highs.iloc[i]
        open_, close = opens.iloc[i], closes.iloc[i]
        
        # Plot high-low line
        pixels[start_y + height - 1 - high:start_y + height - 1 - low, i] = [255, 255, 0]  # Yellow
        
        # Overwrite with blue for high prices
        blue_start = max(close, open_)
        pixels[start_y + height - 1 - high:start_y + height - 1 - blue_start, i] = [0, 0, 255]  # Blue
        
        # Plot open-close bar
        color = [0, 255, 0] if close >= open_ else [255, 0, 0]  # Green or Red
        start, end = min(open_, close), max(open_, close)
        pixels[start_y + height - 1 - end:start_y + height - 1 - start, i] = color

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

start_index = df_1hour.index.searchsorted(start_date)
if start_index == len(df_1hour):
    start_index -= 1

up_count, down_count, neutral_count = 0, 0, 0

for current_index in range(start_index, len(df_1hour) - FUTURE_BARS):
    current_time = df_1hour.index[current_index]
    
    if current_time > end_date:
        break

    if current_index < NUM_BARS:
        continue

    # Check future price movement using H1 data
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
    if len(h1_data) < NUM_BARS:
        print(f"Skipping {current_time}: Not enough H1 data")
        continue
    plot_data(h1_data, 0, H1_HEIGHT, pixels)

    # Plot M5 data
    m5_end_time = current_time
    m5_start_time = m5_end_time - timedelta(minutes=5*NUM_BARS)
    df_5min_window = df_5min.loc[m5_start_time:m5_end_time]
    if len(df_5min_window) < NUM_BARS:
        print(f"Skipping {current_time}: Not enough M5 data")
        continue
    plot_data(df_5min_window, H1_HEIGHT, M5_HEIGHT, pixels)

    # Convert numpy array to PIL Image
    img = Image.fromarray(pixels)

    # Save the image
    timestamp = current_time.strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(OUTPUT_DIR, f'forex_chart_{timestamp}_{price_direction}.png')
    # img.save(image_path)

    if (up_count + down_count + neutral_count) % 100 == 0:
        print(f"Processed: {current_time}, UP: {up_count}, DOWN: {down_count}, NEUTRAL: {neutral_count}")

print(f"Chart generation complete. Final counts - UP: {up_count}, DOWN: {down_count}, NEUTRAL: {neutral_count}")