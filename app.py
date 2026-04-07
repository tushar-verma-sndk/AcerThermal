import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import io

# Disable pandas warning
pd.options.mode.chained_assignment = None  # default='warn'


def on_submit_click():
    print("Submit button pressed!")
    with st.spinner("Processing Data!"):

        st.toast("Processing Data!")

        # Process IoMeter Data
        iometer_data = pd.read_csv(
            iometer_log_file, skiprows=13, skipfooter=5, engine="python")
        needed_iometer_data = iometer_data[['TimeStamp', 'MBps (Decimal)']]
        needed_iometer_data[['Date', 'Time']] = needed_iometer_data['TimeStamp'].str.split(
            ' ', expand=True)
        needed_iometer_data['Time'] = needed_iometer_data['Time'].str.split(
            ':').str[:3].str.join(':')
        needed_iometer_data.drop(['Date', 'TimeStamp'], axis=1)
        needed_iometer_data = needed_iometer_data[["Time", "MBps (Decimal)"]]
        # print(needed_iometer_data.head())

        # Process SMART Temperature Data
        smart_temperature_data = pd.read_csv(
            smart_temperature_log_file, engine="python")
        needed_smart_temperature_data = smart_temperature_data[[
            "Time", "Composite Temperature (Celsius)", "NAND Temperature (Celsius)", "Asic Temperature (Celsius)"]]
        # print(needed_smart_temperature_data.head())

        # Convert the 'Time' column in both DataFrames to datetime objects
        needed_iometer_data['Time'] = pd.to_datetime(
            needed_iometer_data['Time'], format="%H:%M:%S")
        needed_smart_temperature_data['Time'] = pd.to_datetime(
            needed_smart_temperature_data['Time'], format="%H:%M:%S")

        # Set 'Time' as the index in both DataFrames
        needed_iometer_data.set_index('Time', inplace=True)
        needed_smart_temperature_data.set_index('Time', inplace=True)

        # Resample needed_smart_temperature_data to match 1-second intervals (you can choose different aggregation methods if needed)
        needed_smart_temperature_data_resampled = needed_smart_temperature_data.resample(
            '1S').mean().ffill()

        # Merge the two DataFrames
        merged_data = needed_iometer_data.join(
            needed_smart_temperature_data_resampled, how='left')

        # Reset the index if needed
        merged_data.reset_index(inplace=True)

        merged_data['Time'] = merged_data['Time'].dt.strftime('%H:%M:%S')
        merged_data['70 Degrees'] = 70

        # Print the merged DataFrame
        # print(merged_data.head(20))

        # Set the window size for the rolling mean (adjust as needed)
        window_size = 10  # You can change this to a different value

        # # Get the screen width and height (resolution)
        screen_width, screen_height = (1920, 1080)

        # Set the figure size to match the screen resolution
        fig, ax1 = plt.subplots(
            figsize=(screen_width / 100, screen_height / 100))

        # Plot all columns except 'Time' with the primary y-axis (left)
        for column in merged_data.columns:
            # Exclude 'MBps (Decimal)'
            if column != 'Time' and column != 'MBps (Decimal)':
                # Calculate the rolling mean for the column
                smoothed_data = merged_data[column].rolling(
                    window=window_size).mean()
                ax1.plot(merged_data['Time'], smoothed_data, label=f'{column}')

        # Set labels for the primary y-axis
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Temperatures (C)')

        # Create a secondary y-axis (right) for 'MBps (Decimal)'
        ax2 = ax1.twinx()
        ax2.plot(merged_data['Time'], merged_data['MBps (Decimal)'],
                 label='MBps (Decimal)', color='blue')
        ax2.set_ylabel('MBps (Decimal)', color='blue')

        # Add legends for both y-axes
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        # Rotate the x-axis labels to 45 degrees for better readability
        plt.xticks(rotation=45)

        # Reduce the number of x-axis ticks as needed
        ax1.xaxis.set_major_locator(plt.MaxNLocator(nbins=6))

        # Set the y-axis limit to 7500
        ax2.set_ylim(1000, get_gen_speed())

        # Show the plot
        plt.tight_layout()  # Ensure labels are not cut off
        img = io.BytesIO()
        plt.savefig(img, format='png')
        st.session_state.image_data = [fig, img]
    st.success("Results generated!")

def get_gen_speed():
    match st.session_state.gen_speed:
        case 'Gen3':
            return 4000
        case 'Gen4':
            return 7000
        case 'Gen5':
            return 14000

try:
    # Store the initial value of widgets in session state
    if "image_data" not in st.session_state:
        st.session_state.image_data = [None, None]
    st.session_state.submit_enabled = False

    st.set_page_config(
        page_title="Acer Thermal Parser",
        page_icon="🔥",
        menu_items={
            'Get Help': "mailto:tushar.verma@sandisk.com",
            'About': "IoMeter and SMART Temperature logger data parser for acer thermal test cases. Developed by Tushar Verma (tushar.verma@sandisk.com)"
        },
        
    )

    with st.container():
        st.header("Acer Thermal Parser", divider='rainbow')
        with st.container(border=True):
            st.caption(
                "IoMeter and SMART Temperature logger data parser for acer thermal test cases.")
            st.caption("By Tushar Verma (tushar.verma@sandisk.com)")

    if (st.session_state.image_data[0] and st.session_state.image_data[1]) is None:
        with st.container(border=True):
            st.session_state.fw_name = st.text_input(
                'Select Firmware',
                placeholder="AO31AMFO",
                help="Enter the firmware name"
            )

            st.session_state.gen_speed = st.selectbox(
                "Select Gen Speed",
                ("Gen3", "Gen4", "Gen5"),
                index=1,
                placeholder="Gen4",
            )
            st.session_state.drive_capacity = st.selectbox(
                "Select the drive capacity",
                ("256GB", "512GB", "1TB", "2TB"),
                index=None,
                placeholder="Select Drive Capacity",
            )
            st.session_state.run_type = st.selectbox(
                "Select the run type",
                ("With StorPSCTL", "Without StorPSCTL"),
                index=None,
                placeholder="Select Run Type",
            )
            iometer_log_file = st.file_uploader(
                "Choose IoMeter Log File"
            )
            smart_temperature_log_file = st.file_uploader(
                "Choose SMART Temperature Data File"
            )

            if ((smart_temperature_log_file and iometer_log_file and st.session_state.run_type and st.session_state.drive_capacity) is not None) and (len(st.session_state.fw_name) > 4):
                st.session_state.submit_enabled = True

            st.button(
                "Start Processing",
                type="primary",
                disabled=not (st.session_state.submit_enabled),
                help="Enter all the options above.",
                on_click=on_submit_click
            )

    if (st.session_state.image_data[0] and st.session_state.image_data[1]) is not None:
        st.pyplot(st.session_state.image_data[0])
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Download Graph",
                data=st.session_state.image_data[1],
                mime="image/png",
                file_name=f"Acer Thermal {st.session_state.fw_name} {st.session_state.run_type} {st.session_state.drive_capacity}.png",
                type='primary',
                use_container_width=True
            )
        with col2:
            st.button(
                label="Reset",
                use_container_width=True,
                on_click=st.session_state.clear()
            )
except Exception as e:
    st.error('Exception Occured!', icon="🚨")
    st.error(f"{e}")
