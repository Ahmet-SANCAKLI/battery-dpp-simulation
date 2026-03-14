import csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# dataset file given in the assignment
CSV_FILE = "LR1865SZ_cycles201217_001_2.xlsx - 记录表.csv"

# Voltage limits defined in Part 3 for using for alert detection
LOW_VOLTAGE_THRESHOLD = 3.0
HIGH_VOLTAGE_THRESHOLD = 4.2

# simulate device holding registers as mentioned in Part 5
HOLDING_REGISTERS = {
    "Voltage(V)": 40001,
    "Current(A)": 40002,
    "Energy(Wh)": 40003,
    "Cycle_Index": 40004
}


# convert float value into integer register value
def float_to_register(value, scale=10000):
    return int(round(float(value) * scale))


# convert register value back to float
def register_to_float(value, scale=10000):
    return value / scale

#Main Function
def stream_battery_data(csv_file):

    # lists for plotting voltage over time
    timestamps = []
    voltages = []

    # lists for low voltage alert points
    low_times = []
    low_voltages = []

    # lists for high voltage alert points
    high_times = []
    high_voltages = []

    # store alert events and cycle completion events
    alert_updates = []
    cycle_updates = []

    # simulated register memory
    holding_registers = {}

    previous_cycle = None
    last_timestamp = None
    last_voltage = None

    with open(csv_file, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        # Part 5 requirement:
        # read the CSV row by row to simulate a device data stream
        for row_number, row in enumerate(reader, start=1):
            try:
                # Part 5 instruction:
                # use Date_Time as the real-world timestamp
                timestamp = datetime.strptime(row["Date_Time"], "%m/%d/%y %H:%M")

                # raw values coming from the dataset
                voltage_raw = float(row["Voltage(V)"])
                current_raw = float(row["Current(A)"])
                energy_raw = float(row["Energy(Wh)"])
                cycle_index = int(float(row["Cycle_Index"]))

                # write values into simulated holding registers
                holding_registers[HOLDING_REGISTERS["Voltage(V)"]] = float_to_register(voltage_raw)
                holding_registers[HOLDING_REGISTERS["Current(A)"]] = float_to_register(current_raw)
                holding_registers[HOLDING_REGISTERS["Energy(Wh)"]] = float_to_register(energy_raw)
                holding_registers[HOLDING_REGISTERS["Cycle_Index"]] = cycle_index

                # read voltage back from register
                voltage = register_to_float(
                    holding_registers[HOLDING_REGISTERS["Voltage(V)"]]
                )

                timestamps.append(timestamp)
                voltages.append(voltage)

                # Part 3 logic:
                # simple anomaly detection based on voltage thresholds
                if voltage < LOW_VOLTAGE_THRESHOLD:
                    low_times.append(timestamp)
                    low_voltages.append(voltage)

                    alert_updates.append({
                        "timestamp": timestamp,
                        "type": "LOW_VOLTAGE",
                        "voltage": voltage
                    })

                elif voltage > HIGH_VOLTAGE_THRESHOLD:
                    high_times.append(timestamp)
                    high_voltages.append(voltage)

                    alert_updates.append({
                        "timestamp": timestamp,
                        "type": "HIGH_VOLTAGE",
                        "voltage": voltage
                    })

                # Part 3 requirement:
                # Cycle_Index stays the same for many rows and changes when a cycle finishes
                # so we only prepare an update when the cycle number changes
                if previous_cycle is None:
                    previous_cycle = cycle_index

                elif cycle_index != previous_cycle:
                    cycle_updates.append({
                        "completed_cycle": previous_cycle,
                        "timestamp": last_timestamp,
                        "last_voltage": last_voltage
                    })
                    previous_cycle = cycle_index

                last_timestamp = timestamp
                last_voltage = voltage

            except (ValueError, KeyError) as error:
                print(f"Row {row_number} skipped: {error}")

    # also include the last observed cycle at the end of the file
    if previous_cycle is not None and last_timestamp is not None:
        cycle_updates.append({
            "completed_cycle": previous_cycle,
            "timestamp": last_timestamp,
            "last_voltage": last_voltage
        })

    return {
        "timestamps": timestamps,
        "voltages": voltages,
        "low_times": low_times,
        "low_voltages": low_voltages,
        "high_times": high_times,
        "high_voltages": high_voltages,
        "alert_updates": alert_updates,
        "cycle_updates": cycle_updates
    }


def plot_voltage_chart(results):
    # Part 5 requirement:
    # create a Voltage vs Date_Time chart
    # a static chart after processing is enough for this assignment
    plt.figure(figsize=(14, 6))

    plt.plot(results["timestamps"], results["voltages"], label="Voltage")

    # mark low voltage alerts on the chart
    if results["low_times"]:
        plt.scatter(
            results["low_times"],
            results["low_voltages"],
            color="red",
            s=20,
            label=f"Low voltage (< {LOW_VOLTAGE_THRESHOLD} V)"
        )

    # mark high voltage alerts on the chart
    if results["high_times"]:
        plt.scatter(
            results["high_times"],
            results["high_voltages"],
            color="orange",
            s=20,
            label=f"High voltage (> {HIGH_VOLTAGE_THRESHOLD} V)"
        )

    plt.title("Battery Voltage Over Time")
    plt.xlabel("Date and Time")
    plt.ylabel("Voltage (V)")

    plt.grid(True)
    plt.legend()

    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    print("Starting simulation...")

    results = stream_battery_data(CSV_FILE)

    print("Simulation finished.")
    print(f"Rows processed: {len(results['timestamps'])}")
    print(f"Low voltage alerts: {len(results['low_times'])}")
    print(f"High voltage alerts: {len(results['high_times'])}")
    print(f"Total alert events: {len(results['alert_updates'])}")
    print(f"Cycle updates prepared: {len(results['cycle_updates'])}")

    # print only the first few alert events for quick inspection
    print("\nFirst 10 alert events:")
    for i, alert in enumerate(results["alert_updates"][:10], start=1):
        print(
            f"{i}. {alert['timestamp']} | "
            f"{alert['type']} | "
            f"{alert['voltage']:.4f} V"
        )

    # show the first cycle completion events detected from the stream
    print("\nFirst 10 cycle completion events:")
    for i, update in enumerate(results["cycle_updates"][:10], start=1):
        print(
            f"{i}. Completed Cycle: {update['completed_cycle']}, "
            f"Timestamp: {update['timestamp']}, "
            f"Last Voltage: {update['last_voltage']:.4f}"
        )

    plot_voltage_chart(results)