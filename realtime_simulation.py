import os
import pandas as pd

class RealTimeSimulator:
    def __init__(self, file_path, split_date):
        self.split_date = split_date
        self.base_name = os.path.splitext(os.path.basename(file_path))[0]
        self.past_data = pd.DataFrame()
        self.future_data = pd.DataFrame()
        self._load_and_split_data(file_path)
        
    def _load_and_split_data(self, file_path):
        # Load the CSV file
        df = pd.read_csv(file_path, parse_dates=['Date'], index_col='Date')
        
        # Split the data into past and future based on the split_date
        self.past_data = df[df.index <= self.split_date].copy()
        self.future_data = df[df.index > self.split_date].copy()
        
        print(f'Successfully split the data into past and future data frames.')
    
    def move_line(self):
        if not self.future_data.empty:
            # Get the first row of the future data
            next_line = self.future_data.iloc[0:1]
            
            # Append the next line to the past data
            self.past_data = pd.concat([self.past_data, next_line], ignore_index=False)
            
            # Remove the first row from the future data
            self.future_data = self.future_data.iloc[1:]
            
            print(f'Moved one line from future to past for {self.base_name}')
        else:
            print('No more lines in the future data.')

    def get_past_data(self, x):
        return self.past_data.tail(x)
