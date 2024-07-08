import pandas as pd
import os

# Directory containing the files
data_dir = 'DATA'

# Function to process and clean the data files
def process_file(file_path):
    # Read the file as binary
    with open(file_path, 'rb') as f:
        raw_data = f.read()

    # Decode the binary content
    decoded_data = raw_data.decode('latin1')

    # Clean up unwanted characters (like '\x00')
    cleaned_data = decoded_data.replace('\x00', '')

    # Save the cleaned data back to the original file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_data)

    # Read the cleaned CSV file into a pandas DataFrame
    data = pd.read_csv(file_path)

    # Renaming the columns if they have issues
    data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

    # Converting the 'Date' column to datetime
    data['Date'] = pd.to_datetime(data['Date'])

    # Save the cleaned DataFrame back to the original file with UTF-8 encoding
    data.to_csv(file_path, index=False, encoding='utf-8')

    # Rename the original file to include _C suffix
    base_name = os.path.basename(file_path).split('.')[0]
    new_file_path = os.path.join(data_dir, f'{base_name}_C.csv')
    os.rename(file_path, new_file_path)

    print(f"Data cleaned and saved to '{new_file_path}'")

# Loop through all files in the directory and process them
for file_name in os.listdir(data_dir):
    if file_name.endswith('.csv') and '_C' not in file_name:
        file_path = os.path.join(data_dir, file_name)
        process_file(file_path)
