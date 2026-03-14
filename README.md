# Battery Stream Simulation

This project demonstrates a simple IoT telemetry simulation for battery data as part of a Digital Product Passport (DPP) case study.

## Dataset
LR1865SZ lithium-ion battery cycle dataset used for laboratory battery testing.

## Features
- Simulates device telemetry stream by reading the CSV file row-by-row
- Uses `Date_Time` as the real-world timestamp
- Maps selected telemetry values to simulated holding registers
- Detects voltage threshold alerts
- Aggregates telemetry into cycle completion events
- Generates a static Voltage vs Time visualization

## Holding Register Representation
To reflect a simple device communication model, some telemetry values are mapped to simulated holding registers before being processed.

Example register mapping used in the script:

| Parameter | Register |
|----------|----------|
| Voltage(V) | 40001 |
| Current(A) | 40002 |
| Energy(Wh) | 40003 |
| Cycle_Index | 40004 |

The values are written into these registers and then read back again, which helps simulate how telemetry may be exposed by an edge device or industrial controller.

## Alert Logic
Low voltage alert: < 3.0 V  
High voltage alert: > 4.2 V

## Cycle Logic
The script only generates an update when `Cycle_Index` changes, representing a completed battery cycle.

## Visualization
Voltage vs `Date_Time` chart using Matplotlib.

## Simple Flow of the Script

```text
Battery Test Data (CSV)
        │
        ▼
Row-by-row Stream Simulation
        │
        ▼
Parse Date_Time and Telemetry Values
        │
        ▼
Write Values into Simulated Holding Registers
        │
        ▼
Read Values Back from Registers
        │
        ├── Check Voltage Thresholds
        │         ├── Low Voltage Alert
        │         └── High Voltage Alert
        │
        ├── Check Cycle_Index Changes
        │         └── Create Cycle Completion Event
        │
        ▼
Store Processed Data for Visualization
        │
        ▼
Generate Static Voltage vs Time Chart