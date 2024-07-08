import pandas as pd
import numpy as np
from PIL import Image
import os

NUM_BARS = 500
H1_HEIGHT = 100
M5_HEIGHT = 100
TOTAL_HEIGHT = H1_HEIGHT + M5_HEIGHT
START_FRAME = 90000

os.makedirs('DATA/TEST1IMAGES', exist_ok=True)

df_5min = pd.read_csv('DATA/EURUSD_C.csv', parse_dates=['Date'], usecols=['Date', 'Open', 'High', 'Low', 'Close'])

# Calculate H1 data for the entire dataset
df_1hour = df_5min.resample('h', on='Date').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last'
}).dropna()

def normalize_data(df):
    price_columns = ['Open', 'High', 'Low', 'Close']
    df_norm = df[price_columns].copy()
    min_price = df_norm.min().min()
    max_price = df_norm.max().max()
    for col in price_columns:
        df_norm[col] = (df[col] - min_price) / (max_price - min_price)
    return df_norm.ffill().bfill()  # Use ffill() and bfill() instead of fillna()

def plot_data(df, start_y, height):
    for i in range(NUM_BARS):
        if i < len(df):
            row = df.iloc[i]
            high = max(0, min(int(row['High'] * (height - 1)), height - 1))
            low = max(0, min(int(row['Low'] * (height - 1)), height - 1))
            open_price = max(0, min(int(row['Open'] * (height - 1)), height - 1))
            close_price = max(0, min(int(row['Close'] * (height - 1)), height - 1))
            
            for y in range(low, high + 1):
                pixels[i, start_y + height - 1 - y] = (0, 0, 0)
            
            color = (0, 0, 255) if close_price >= open_price else (255, 0, 0)
            start = min(open_price, close_price)
            end = max(open_price, close_price)
            for y in range(start, end + 1):
                pixels[i, start_y + height - 1 - y] = color

for i in range(START_FRAME, len(df_5min) - NUM_BARS + 1):
    df_5min_window = df_5min.iloc[i:i+NUM_BARS]
    end_time = df_5min_window.iloc[-1]['Date']
    
    # Calculate start time for H1 data (NUM_BARS * 5 minutes earlier)
    start_time = end_time - pd.Timedelta(minutes=NUM_BARS * 5)
    
    df_1hour_window = df_1hour[(df_1hour.index >= start_time) & (df_1hour.index <= end_time)]
    
    # Ensure we have exactly NUM_BARS for H1 data
    if len(df_1hour_window) < NUM_BARS:
        padding = pd.DataFrame(index=pd.date_range(end=df_1hour_window.index[0], periods=NUM_BARS, freq='h'))
        df_1hour_window = pd.concat([padding, df_1hour_window]).tail(NUM_BARS)
        df_1hour_window = df_1hour_window.ffill().bfill()  # Forward fill then backward fill

    df_5min_norm = normalize_data(df_5min_window)
    df_1hour_norm = normalize_data(df_1hour_window)

    img = Image.new('RGB', (NUM_BARS, TOTAL_HEIGHT), color='white')
    pixels = img.load()

    plot_data(df_1hour_norm, 0, H1_HEIGHT)
    plot_data(df_5min_norm, H1_HEIGHT, M5_HEIGHT)

    img.save(f'DATA/TEST1IMAGES/forex_chart_{i:05d}.png')

    if i % 100 == 0:
        print(f"Processed {i} images")

print("All images saved in DATA/TEST1IMAGES/")