import pandas as pd
from io import StringIO
import os
import time

# Define the maximum number of rows to keep in memory
max_rows = 10

# Initialize an empty DataFrame to hold the latest 50 entries
latest_entries = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

# Open the file
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
        
        # Append the new entry to the DataFrame
        latest_entries = pd.concat([latest_entries, new_entry], ignore_index=True)
        
        # Keep only the latest 50 entries
        if len(latest_entries) > max_rows:
            latest_entries = latest_entries.iloc[-max_rows:]
        
        # Clear the console and display the latest 50 entries
        clear_console()
        print(latest_entries)

        # Calculate the minimum and maximum values in High, Low, Open, and Close columns
        min_value_hlop = latest_entries[['High', 'Low', 'Open', 'Close']].min().min()
        max_value_hlop = latest_entries[['High', 'Low', 'Open', 'Close']].max().max()

        print(f'Minimum Value (High, Low, Open, Close): {min_value_hlop}')
        print(f'Maximum Value (High, Low, Open, Close): {max_value_hlop}')

        # Sleep to simulate time between reads (remove in real usage)
        time.sleep(0.5)
