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

        # Calculate the minimum and maximum values in High, Low, Open, and Close columns
        min_value_hlop = latest_entries[['High', 'Low', 'Open', 'Close']].min().min()
        max_value_hlop = latest_entries[['High', 'Low', 'Open', 'Close']].max().max()

        # Calculate the minimum and maximum values in the Volume column
        min_value_volume = latest_entries['Volume'].min()
        max_value_volume = latest_entries['Volume'].max()

        print(f'Minimum Value (High, Low, Open, Close): {min_value_hlop}')
        print(f'Maximum Value (High, Low, Open, Close): {max_value_hlop}')
        print(f'Minimum Value (Volume): {min_value_volume}')
        print(f'Maximum Value (Volume): {max_value_volume}')

        # Normalize the Volume column
        volume_range = max_value_volume - min_value_volume
        if volume_range > 0:
            normalized_volume = (latest_entries['Volume'] - min_value_volume) / volume_range
        else:
            normalized_volume = 0  # If min and max are the same, set all values to 0

        print("Normalized Volume:")
        print(normalized_volume)

        # Sleep to simulate time between reads (remove in real usage)
        time.sleep(2)
