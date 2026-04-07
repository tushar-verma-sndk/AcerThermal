from lib_csv_parser import select_csv_file
import pandas as pd
import matplotlib.pyplot as plt

try:
    iometer_log_file, smart_temperature_log_file = select_csv_file()

    # Process IoMeter Data
    iometer_data = pd.read_csv(iometer_log_file, skiprows=13, skipfooter=5, engine="python")
    needed_iometer_data = iometer_data[['TimeStamp', 'MBps (Decimal)']]
    needed_iometer_data[['Date', 'Time']] = needed_iometer_data['TimeStamp'].str.split(' ', expand=True)
    needed_iometer_data['Time'] = needed_iometer_data['Time'].str.split(':').str[:3].str.join(':')
    needed_iometer_data.drop(['Date', 'TimeStamp'], axis=1, inplace=True)
    needed_iometer_data = needed_iometer_data[["Time", "MBps (Decimal)"]]
    # print(needed_iometer_data.head())


    # Process SMART Temperature Data
    smart_temperature_data = pd.read_csv(smart_temperature_log_file, engine="python")
    needed_smart_temperature_data = smart_temperature_data[["Time", "Composite Temperature (Celsius)", "NAND Temperature (Celsius)", "Asic Temperature (Celsius)"]]
    # print(needed_smart_temperature_data.head())


    # Convert the 'Time' column in both DataFrames to datetime objects
    needed_iometer_data['Time'] = pd.to_datetime(needed_iometer_data['Time'])
    needed_smart_temperature_data['Time'] = pd.to_datetime(needed_smart_temperature_data['Time'])

    # Set 'Time' as the index in both DataFrames
    needed_iometer_data.set_index('Time', inplace=True)
    needed_smart_temperature_data.set_index('Time', inplace=True)

    # Resample needed_smart_temperature_data to match 1-second intervals (you can choose different aggregation methods if needed)
    needed_smart_temperature_data_resampled = needed_smart_temperature_data.resample('1S').mean().ffill()

    # Merge the two DataFrames
    merged_data = needed_iometer_data.join(needed_smart_temperature_data_resampled, how='left')

    # Reset the index if needed
    merged_data.reset_index(inplace=True)

    merged_data['Time'] = merged_data['Time'].dt.strftime('%H:%M:%S')
    merged_data['70 Degrees'] = 70

    # Print the merged DataFrame
    # print(merged_data.head(20))

    # Set the window size for the rolling mean (adjust as needed)
    window_size = 10  # You can change this to a different value

    # Get the screen width and height (resolution)
    screen_width, screen_height = (1920,1080)

    # Set the figure size to match the screen resolution
    fig, ax1 = plt.subplots(figsize=(screen_width / 100, screen_height / 100))

    # Plot all columns except 'Time' with the primary y-axis (left)
    for column in merged_data.columns:
        if column != 'Time' and column != 'MBps (Decimal)':  # Exclude 'MBps (Decimal)'
            # Calculate the rolling mean for the column
            smoothed_data = merged_data[column].rolling(window=window_size).mean()
            ax1.plot(merged_data['Time'], smoothed_data, label=f'{column}')

    # Set labels for the primary y-axis
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Temperatures (C)')

    # Create a secondary y-axis (right) for 'MBps (Decimal)'
    ax2 = ax1.twinx()
    ax2.plot(merged_data['Time'], merged_data['MBps (Decimal)'], label='MBps (Decimal)', color='blue')
    ax2.set_ylabel('MBps (Decimal)', color='blue')

    # Add legends for both y-axes
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    # Rotate the x-axis labels to 45 degrees for better readability
    plt.xticks(rotation=45)

    # Reduce the number of x-axis ticks as needed
    ax1.xaxis.set_major_locator(plt.MaxNLocator(nbins=6))

    # Set the y-axis limit to 7500
    ax2.set_ylim(1000,7000)

    # Show the plot
    plt.tight_layout()  # Ensure labels are not cut off

    # Prompt the user to enter a filename and save the plot as a PNG
    filename = input("Enter a filename to save the plot as a PNG: ")
    if filename:
        plt.savefig(filename + '.png', bbox_inches='tight', dpi=300)
        print(f"Plot saved as {filename}.png")

    plt.show()
except Exception as e:
    print(f"Exception Occured: {e}")
    input("Press Enter to exit: ")