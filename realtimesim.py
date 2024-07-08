import os
import pandas as pd

def split_file(file_path, split_date, output_dir='STREAM'):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Split the data into past and future based on the split_date
    past_data = df[df['Date'] <= split_date]
    future_data = df[df['Date'] > split_date]
    
    # Extract the base name of the file (without extension)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # Generate output file names
    past_file = os.path.join(output_dir, f'{base_name}_past.csv')
    future_file = os.path.join(output_dir, f'{base_name}_future.csv')
    
    # Save the split data
    past_data.to_csv(past_file, index=False)
    future_data.to_csv(future_file, index=False)
    
    print(f'Successfully split the file into {past_file} and {future_file}.')

def move_line(base_name, output_dir='STREAM'):
    past_file = os.path.join(output_dir, f'{base_name}_past.csv')
    future_file = os.path.join(output_dir, f'{base_name}_future.csv')
    
    # Load the CSV files
    past_data = pd.read_csv(past_file)
    future_data = pd.read_csv(future_file)
    
    if not future_data.empty:
        # Get the first row of the future data
        next_line = future_data.iloc[0:1]
        
        # Append the next line to the past data
        past_data = pd.concat([past_data, next_line], ignore_index=True)
        
        # Remove the first row from the future data
        future_data = future_data.iloc[1:]
        
        # Save the updated files
        past_data.to_csv(past_file, index=False)
        future_data.to_csv(future_file, index=False)
        
        print(f'Moved one line from future to past for {base_name}')
    else:
        print('No more lines in the future data.')
