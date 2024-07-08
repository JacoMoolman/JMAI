import pandas as pd
import os
import concurrent.futures

# Directory containing the files
data_dir = os.path.join(os.path.dirname(__file__), 'DATA')

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

    # Add the new column for weekday (as numbers)
    data['Weekday'] = data['Date'].dt.dayofweek + 1  # Adding 1 so Monday=1, Tuesday=2, etc.

    # Add Price_Change and High_Low_Diff features, rounded to 4 decimal places
    data['Price_Change'] = (data['Close'] - data['Open']).round(4)
    data['High_Low_Diff'] = (data['High'] - data['Low']).round(4)

    # Save the cleaned DataFrame back to the original file with UTF-8 encoding
    data.to_csv(file_path, index=False, encoding='utf-8', float_format='%.4f')

    # Rename the original file to include _C suffix
    base_name = os.path.basename(file_path).split('.')[0]
    new_file_path = os.path.join(data_dir, f'{base_name}_C.csv')
    os.rename(file_path, new_file_path)

    print(f"Data cleaned and saved to '{new_file_path}'")

if __name__ == "__main__":
    # Get the list of files to process
    file_paths = [os.path.join(data_dir, file_name) for file_name in os.listdir(data_dir) if file_name.endswith('.csv') and '_C' not in file_name]

    # Use ProcessPoolExecutor to process files concurrently
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(process_file, file_paths)