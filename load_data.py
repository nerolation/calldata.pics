import pickle
import pandas as pd
import os

chart_filenames = [
    "gasusageperday.pickle",
    "beaconblock.pickle",
    "calldataovertime.pickle",
    "calldatacumdist.pickle",
    "calldataslotlorenz.pickle",
    "calldatahist.pickle",
    "gas_used_over_time.pickle",
    "cumulative_data_over_time.pickle",
    "beaconblock_over_time.pickle",
    "calldataentities_over_time.pickle",
    "fields4.pickle",
    "entity_pie.pickle"
]

# Function to print file sizes in MB
def print_file_sizes(filenames):
    for filename in filenames:
        # Get size in bytes
        size_bytes = os.path.getsize(filename)
        # Convert to MB
        size_mb = size_bytes / (1024 * 1024)
        print(f"{filename}: {size_mb:.2f} MB")

# Call the function
print_file_sizes(chart_filenames)

avgs = pd.read_parquet("averages.parquet")
calldatatxs = pd.read_parquet("calldatatxs.parquet")
entities_calldata_summary = pd.read_parquet("entities_calldata_summary.parquet")
with open("gasusageperday.pickle", "rb") as file:
    gasuageperday = pickle.load(file)
print("gasusageperday.pickle loaded")
with open("beaconblock.pickle", "rb") as file:
    beaconblock = pickle.load(file)
print("beaconblock.pickle loaded")
with open("calldataovertime.pickle", "rb") as file:
    calldataovertime = pickle.load(file)
print("calldataovertime.pickle loaded")
with open("calldatacumdist.pickle", "rb") as file:
    calldatacumdist = pickle.load(file)
print("calldatacumdist.pickle loaded")
with open("calldataslotlorenz.pickle", "rb") as file:
    calldataslotlorenz = pickle.load(file)
print("calldataslotlorenz.pickle loaded")
with open("calldatahist.pickle", "rb") as file:
    calldatahist = pickle.load(file)
print("calldatahist.pickle loaded")
with open("gas_used_over_time.pickle", "rb") as file:
    gas_used_over_time = pickle.load(file)
print("gas_used_over_time.pickle loaded")
with open("cumulative_data_over_time.pickle", "rb") as file:
    cumulative_data_over_time = pickle.load(file)
print("cumulative_data_over_time.pickle loaded")
with open("beaconblock_over_time.pickle", "rb") as file:
    beaconblock_over_time = pickle.load(file)
print("beaconblock_over_time.pickle loaded")
with open("calldataentities_over_time.pickle", "rb") as file:
    calldataentities_over_time = pickle.load(file)
print("calldataentities_over_time.pickle loaded")
with open("fields4.pickle", "rb") as file:
    fields4 = pickle.load(file)
print("fields4.pickle loaded")
with open("entity_pie.pickle", "rb") as file:
    entity_pie = pickle.load(file)
print("entity_pie.pickle loaded")
with open("calldata_ratio.txt", "r") as file:
    calldata_gas_ratio = float(file.read())
print("calldata_ratio.txt loaded")
with open("zeros_ratio.txt", "r") as file:
    zeros_ratio = float(file.read())
print("zeros_ratio.txt loaded")
with open("calldata_summary.csv", "r") as file:
    calldata_summary = file.read().split(",")
print("calldata_summary.csv loaded")

    