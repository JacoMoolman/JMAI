import pandas as pd
from PIL import Image

# Custom variables
NUM_BARS = 500  # Number of bars to display
H1_HEIGHT = 200  # Height of H1 chart in pixels
M5_HEIGHT = 200  # Height of M5 chart in pixels
TOTAL_HEIGHT = H1_HEIGHT + M5_HEIGHT

# Read the CSV file
df_5min = pd.read_csv('DATA/EURUSD_C.csv', parse_dates=['Date'], usecols=['Date', 'Open', 'Close', 'High', 'Low'])

# Convert to H1 timeframe
df_1hour = df_5min.resample('H', on='Date').agg({
    'Open': 'first',
    'Close': 'last',
    'High': 'max',
    'Low': 'min'
}).dropna()

# Select the first NUM_BARS rows for each dataframe
df_1hour = df_1hour.head(NUM_BARS)
df_5min = df_5min.head(NUM_BARS)

# Print the start and end times for the two timeframes
print("H1 timeframe start time:", df_1hour.index[0])
print("H1 timeframe end time:", df_1hour.index[-1])
print("M5 timeframe start time:", df_5min['Date'].iloc[0])
print("M5 timeframe end time:", df_5min['Date'].iloc[-1])

# Create a new image with black background
img = Image.new('RGB', (NUM_BARS, TOTAL_HEIGHT), color='black')
pixels = img.load()

def normalize_data(df):
    price_data = df[['Open', 'Close', 'High', 'Low']]
    min_price = price_data.min().min()
    max_price = price_data.max().max()
    return (price_data - min_price) / (max_price - min_price)

def plot_data(df, start_y, height):
    normalized_df = normalize_data(df)
    for i, (_, row) in enumerate(normalized_df.iterrows()):
        open_price = int(row['Open'] * (height - 1))
        close_price = int(row['Close'] * (height - 1))
        high_price = int(row['High'] * (height - 1))
        low_price = int(row['Low'] * (height - 1))

        color = (0, 255, 0) if close_price >= open_price else (255, 0, 0)

        # Plot high-low line
        for y in range(low_price, high_price + 1):
            if y <= close_price or y <= open_price:
                pixels[i, start_y + height - 1 - y] = (255, 255, 0)  # Yellow for low prices
            else:
                pixels[i, start_y + height - 1 - y] = (0, 0, 255)  # Blue for high prices

        # Plot open-close bar
        start = min(open_price, close_price)
        end = max(open_price, close_price)
        for y in range(start, end + 1):
            pixels[i, start_y + height - 1 - y] = color

# Plot H1 data
plot_data(df_1hour, 0, H1_HEIGHT)

# Plot M5 data
plot_data(df_5min, H1_HEIGHT, M5_HEIGHT)

# Save the image
img.save('forex_chart_pixel_perfect.png')

print("Chart saved as forex_chart_pixel_perfect.png")
