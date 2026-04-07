import os
import glob


def __find_csv_files(folder_path):
    csv_files = []

    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))

    return csv_files


def __select_csv_file(csv_files, prompt):
    if not csv_files:
        return None

    print("CSV files found:")
    for i, file in enumerate(csv_files):
        print(f"{i + 1}: {file}")

    while True:
        try:
            choice = int(input(prompt))
            if 1 <= choice <= len(csv_files):
                return csv_files[choice - 1]
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def select_csv_file():
    # Specify the folder path to start scanning from
    folder_path = "Results"  # Replace with your folder path

    if os.path.exists(folder_path):
        csv_files = __find_csv_files(folder_path)

        if csv_files:
            print("Select the IoMeter results file:")
            iometer_result_file = __select_csv_file(
                csv_files,
                "Enter the number of the IoMeter results file (or 0 to exit): ",
            )

            if iometer_result_file:
                print(f"Selected IoMeter results file: {iometer_result_file}")

                print("\nSelect the SMART temperature log file:")
                # Remove the selected CSV file from the list to avoid selecting the same file again
                remaining_csv_files = [
                    file for file in csv_files if file != iometer_result_file
                ]
                smart_temperature_logger_file = __select_csv_file(
                    remaining_csv_files,
                    "Enter the number of the SMART temperature log file (or 0 to exit): ",
                )

                if smart_temperature_logger_file:
                    print(
                        f"Selected SMART temperature log file: {smart_temperature_logger_file}"
                    )
                    # Add your further processing code here
                    return iometer_result_file, smart_temperature_logger_file
                else:
                    raise Exception("No SMART temperature log file selected.")
            else:
                raise Exception("No IoMeter results file selected.")
        else:
            raise Exception("No CSV files found in the specified folder and its subdirectories.")
    else:
        raise Exception(f"The specified folder \"{folder_path}\" does not exist.")


if __name__ == "__main__":
    iometer_result_file, smart_temperature_logger_file = select_csv_file()
    print(f"Selected IoMeter result file: {iometer_result_file}\nSelected SMART temperature logger file: {smart_temperature_logger_file}")