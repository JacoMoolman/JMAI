import pandas as pd
import os

# Define the input directory and output directory
input_dir = 'E:/Projects/JMAI/DATA - Copy'
output_dir = 'E:/Projects/JMAI/DATA - 2000'

# Make sure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# List of CSV files to process
csv_files = ['EURUSD_C.csv', 'GBPUSD_C.csv', 'USDCHF_C.csv', 'USDJPY_C.csv']

for file in csv_files:
    # Read the CSV file
    df = pd.read_csv(os.path.join(input_dir, file))
    
    # Convert the 'Date' column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter the data for the year 2000
    df_2000 = df[df['Date'].dt.year == 2000]
    
    # Save the filtered data to a new CSV file
    df_2000.to_csv(os.path.join(output_dir, file), index=False)

print("Data extraction completed.")
