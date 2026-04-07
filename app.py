import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import io

# Disable pandas chained assignment warning
pd.options.mode.chained_assignment = None


def get_gen_speed():
    match st.session_state.gen_speed:
        case "Gen3":
            return 4000
        case "Gen4":
            return 7000
        case "Gen5":
            return 14000


def on_submit_click():
    with st.spinner("Processing Data..."):
        st.toast("Processing Data!")

        # =========================
        # IoMeter Data Processing
        # =========================
        iometer_data = pd.read_csv(
            iometer_log_file,
            skiprows=13,
            skipfooter=5,
            engine="python",
        )

        needed_iometer_data = iometer_data[["TimeStamp", "MBps (Decimal)"]]
        needed_iometer_data[["Date", "Time"]] = needed_iometer_data[
            "TimeStamp"
        ].str.split(" ", expand=True)

        needed_iometer_data["Time"] = (
            needed_iometer_data["Time"]
            .str.split(":")
            .str[:3]
            .str.join(":")
        )

        needed_iometer_data = needed_iometer_data[
            ["Time", "MBps (Decimal)"]
        ]

        # Add dummy date (required for stable resampling)
        needed_iometer_data["Time"] = pd.to_datetime(
            "2024-01-01 " + needed_iometer_data["Time"].astype(str),
            errors="coerce",
        )

        needed_iometer_data = needed_iometer_data.dropna(subset=["Time"])
        needed_iometer_data = needed_iometer_data.sort_values("Time")
        needed_iometer_data.set_index("Time", inplace=True)

        # =========================
        # SMART Temperature Data
        # =========================
        smart_temperature_data = pd.read_csv(
            smart_temperature_log_file, engine="python"
        )

        needed_smart_temperature_data = smart_temperature_data[
            [
                "Time",
                "Composite Temperature (Celsius)",
                "NAND Temperature (Celsius)",
                "Asic Temperature (Celsius)",
            ]
        ]

        needed_smart_temperature_data["Time"] = pd.to_datetime(
            "2024-01-01 " + needed_smart_temperature_data["Time"].astype(str),
            errors="coerce",
        )

        needed_smart_temperature_data = needed_smart_temperature_data.dropna(
            subset=["Time"]
        )
        needed_smart_temperature_data = (
            needed_smart_temperature_data.sort_values("Time")
        )
        needed_smart_temperature_data.set_index("Time", inplace=True)

        # ✅ Critical fix: resample requires DatetimeIndex
        needed_smart_temperature_data_resampled = (
            needed_smart_temperature_data.resample("1S").mean().ffill()
        )

        # =========================
        # Merge Data
        # =========================
        merged_data = needed_iometer_data.join(
            needed_smart_temperature_data_resampled, how="left"
        )

        merged_data.reset_index(inplace=True)
        merged_data["Time"] = merged_data["Time"].dt.strftime("%H:%M:%S")
        merged_data["70 Degrees"] = 70

        # =========================
        # Plotting
        # =========================
        window_size = 10
        screen_width, screen_height = (1920, 1080)

        fig, ax1 = plt.subplots(
            figsize=(screen_width / 100, screen_height / 100)
        )

        for column in merged_data.columns:
            if column not in ("Time", "MBps (Decimal)"):
                smoothed = (
                    merged_data[column]
                    .rolling(window=window_size)
                    .mean()
                )
                ax1.plot(merged_data["Time"], smoothed, label=column)

        ax1.set_xlabel("Time")
        ax1.set_ylabel("Temperatures (C)")

        ax2 = ax1.twinx()
        ax2.plot(
            merged_data["Time"],
            merged_data["MBps (Decimal)"],
            color="blue",
            label="MBps (Decimal)",
        )
        ax2.set_ylabel("MBps (Decimal)", color="blue")

        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")

        plt.xticks(rotation=45)
        ax1.xaxis.set_major_locator(plt.MaxNLocator(nbins=6))
        ax2.set_ylim(1000, get_gen_speed())

        plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format="png")
        img.seek(0)

        st.session_state.image_data = [fig, img]

    st.success("Results generated!")


# =========================
# Streamlit App
# =========================
try:
    if "image_data" not in st.session_state:
        st.session_state.image_data = [None, None]

    st.set_page_config(
        page_title="Acer Thermal Parser",
        page_icon="🔥",
        menu_items={
            "Get Help": "mailto:tushar.verma@sandisk.com",
            "About": (
                "IoMeter and SMART Temperature logger data parser "
                "for acer thermal test cases.\n\n"
                "Developed by Tushar Verma"
            ),
        },
    )

    st.header("Acer Thermal Parser", divider="rainbow")
    st.caption(
        "IoMeter and SMART Temperature logger data parser "
        "for acer thermal test cases."
    )

    # =========================
    # Input Section
    # =========================
    if (
        st.session_state.image_data[0] is None
        and st.session_state.image_data[1] is None
    ):
        with st.container(border=True):
            st.session_state.fw_name = st.text_input(
                "Select Firmware", placeholder="AO31AMFO"
            )

            st.session_state.gen_speed = st.selectbox(
                "Select Gen Speed",
                ("Gen3", "Gen4", "Gen5"),
                index=1,
            )

            st.session_state.drive_capacity = st.selectbox(
                "Select Drive Capacity",
                ("256GB", "512GB", "1TB", "2TB"),
                index=None,
            )

            st.session_state.run_type = st.selectbox(
                "Select Run Type",
                ("With StorPSCTL", "Without StorPSCTL"),
                index=None,
            )

            iometer_log_file = st.file_uploader(
                "Choose IoMeter Log File"
            )
            smart_temperature_log_file = st.file_uploader(
                "Choose SMART Temperature Log File"
            )

            submit_enabled = (
                iometer_log_file
                and smart_temperature_log_file
                and st.session_state.drive_capacity
                and st.session_state.run_type
                and len(st.session_state.fw_name) > 4
            )

            st.button(
                "Start Processing",
                type="primary",
                disabled=not submit_enabled,
                on_click=on_submit_click,
            )

    # =========================
    # Output Section
    # =========================
    else:
        st.pyplot(st.session_state.image_data[0])

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Download Graph",
                data=st.session_state.image_data[1],
                mime="image/png",
                file_name=(
                    f"Acer Thermal "
                    f"{st.session_state.fw_name} "
                    f"{st.session_state.run_type} "
                    f"{st.session_state.drive_capacity}.png"
                ),
                type="primary",
                use_container_width=True,
            )

        with col2:
            st.button(
                "Reset",
                use_container_width=True,
                on_click=lambda: st.session_state.clear(),
            )

except Exception as e:
    st.error("Exception Occurred 🚨")
    st.exception(e)