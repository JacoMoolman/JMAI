from realtimesim import split_file,move_line


# Split the file (uncomment and adjust the parameters as needed)
split_file('DATA/AUDUSD_C.csv', '2002.01.01 00:00')
split_file('DATA/EURUSD_C.csv', '2002.01.01 00:00')
split_file('DATA/GBPUSD_C.csv', '2002.01.01 00:00')
split_file('DATA/USDJPY_C.csv', '2002.01.01 00:00')
    
# Move one line from future to past (uncomment to use)
# move_line('AUDUSD_C')
# move_line('EURUSD_C')
# move_line('GBPUSD_C')
# move_line('USDJPY_C')

