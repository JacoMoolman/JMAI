import pandas as pd
from io import StringIO
import os
import time

# Define the maximum number of rows to keep in memory
max_rows = 10

# Initialize an empty DataFrame to hold the latest entries
latest_entries = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

# Path to the CSV file
csv_file = 'DATA/EURUSD_volume_C.csv'

def clear_console():
    # Clear the console output
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For macOS and Linux
        os.system('clear')

# Read the file line by line
with open(csv_file, 'r') as file:
    # Skip the header
    header = file.readline()
    
    for line in file:
        # Read the line into a DataFrame
        new_entry = pd.read_csv(StringIO(header + line), parse_dates=['Date'])
        
        # Ensure the Volume column is of type float
        new_entry['Volume'] = new_entry['Volume'].astype(float)
        
        # Append the new entry to the DataFrame
        latest_entries = pd.concat([latest_entries, new_entry], ignore_index=True)
        
        # Keep only the latest entries
        if len(latest_entries) > max_rows:
            latest_entries = latest_entries.iloc[-max_rows:]
        
        # Clear the console and display the latest entries
        clear_console()
        print(latest_entries)

        # Calculate the global minimum and maximum values across Open, High, Low, and Close columns
        min_value_hlop = latest_entries[['High', 'Low', 'Open', 'Close']].min().min()
        max_value_hlop = latest_entries[['High', 'Low', 'Open', 'Close']].max().max()

        print(f'Global Minimum Value (Open, High, Low, Close): {min_value_hlop}')
        print(f'Global Maximum Value (Open, High, Low, Close): {max_value_hlop}')

        # Normalize the Open, High, Low, and Close columns using the global min and max
        hlop_range = max_value_hlop - min_value_hlop
        if hlop_range > 0:
            normalized_open = (latest_entries['Open'] - min_value_hlop) / hlop_range
            normalized_high = (latest_entries['High'] - min_value_hlop) / hlop_range
            normalized_low = (latest_entries['Low'] - min_value_hlop) / hlop_range
            normalized_close = (latest_entries['Close'] - min_value_hlop) / hlop_range
        else:
            normalized_open = normalized_high = normalized_low = normalized_close = 0

        # Normalize the Volume column independently
        min_value_volume = latest_entries['Volume'].min()
        max_value_volume = latest_entries['Volume'].max()
        volume_range = max_value_volume - min_value_volume
        if volume_range > 0:
            normalized_volume = (latest_entries['Volume'] - min_value_volume) / volume_range
        else:
            normalized_volume = 0

        # print("Normalized Columns (Open, High, Low, Close, Volume):")
        # print("Normalized Open:", normalized_open)
        # print("Normalized High:", normalized_high)
        # print("Normalized Low:", normalized_low)
        # print("Normalized Close:", normalized_close)
        # print("Normalized Volume:", normalized_volume)

        # Create a new DataFrame with the normalized values
        normalized_df = latest_entries.copy()
        normalized_df['Open'] = normalized_open
        normalized_df['High'] = normalized_high
        normalized_df['Low'] = normalized_low
        normalized_df['Close'] = normalized_close
        normalized_df['Volume'] = normalized_volume

        print("FIN (New DataFrame with Normalized Columns):")
        print(normalized_df)

        # Sleep to simulate time between reads (remove in real usage)
        time.sleep(1)

