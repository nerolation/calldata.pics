import pickle
import pandas as pd
import os

DATA_LOC = "./data/"
CHART_LOC =  DATA_LOC + "chart/"

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
    "entity_pie.pickle",
    "maxblockvsavg.pickle",
    "blobs_over_time.pickle",
    "entity_calldata_blob.pickle",
    "blobentities_over_time.pickle",
    "blob_for_rollup.pickle",
    "blobs_fee_over_time.pickle",
    "builder_over_time.pickle",
    "relay_over_time.pickle"
]

# Function to print file sizes in MB
def print_file_sizes(filenames):
    for filename in filenames:
        # Get size in bytes
        size_bytes = os.path.getsize(CHART_LOC+filename)
        # Convert to MB
        size_mb = size_bytes / (1024 * 1024)
        print(f"{filename}: {size_mb:.2f} MB")

# Call the function
print_file_sizes(chart_filenames)
print("----------------------------------------------")
avgs = pd.read_parquet(CHART_LOC+"averages.parquet")
calldatatxs = pd.read_parquet(CHART_LOC+"calldatatxs.parquet")
entities_calldata_summary = pd.read_parquet(CHART_LOC+"entities_calldata_summary.parquet")
entities_blob_summary = pd.read_parquet(CHART_LOC+"entities_blob_summary.parquet")
blob_summary_data = pd.read_csv(CHART_LOC+"blob_summary_data.csv").to_dict('records')[0]
builder_blob_summary = pd.read_parquet(CHART_LOC+"builder_blob_summary.parquet")
relay_blob_summary = pd.read_parquet(CHART_LOC+"relay_blob_summary.parquet")


with open(CHART_LOC+"gasusageperday.pickle", "rb") as file:
    gasuageperday = pickle.load(file)
print("gasusageperday.pickle loaded")
with open(CHART_LOC+"beaconblock.pickle", "rb") as file:
    beaconblock = pickle.load(file)
print("beaconblock.pickle loaded")
with open(CHART_LOC+"calldataovertime.pickle", "rb") as file:
    calldataovertime = pickle.load(file)
print("calldataovertime.pickle loaded")
with open(CHART_LOC+"calldatacumdist.pickle", "rb") as file:
    calldatacumdist = pickle.load(file)
print("calldatacumdist.pickle loaded")
with open(CHART_LOC+"calldataslotlorenz.pickle", "rb") as file:
    calldataslotlorenz = pickle.load(file)
print("calldataslotlorenz.pickle loaded")
with open(CHART_LOC+"calldatahist.pickle", "rb") as file:
    calldatahist = pickle.load(file)
print("calldatahist.pickle loaded")
with open(CHART_LOC+"gas_used_over_time.pickle", "rb") as file:
    gas_used_over_time = pickle.load(file)
print("gas_used_over_time.pickle loaded")
with open(CHART_LOC+"cumulative_data_over_time.pickle", "rb") as file:
    cumulative_data_over_time = pickle.load(file)
print("cumulative_data_over_time.pickle loaded")
with open(CHART_LOC+"maxblockvsavg.pickle", "rb") as file:
    maxblockvsavg = pickle.load(file)
print("maxblockvsavg.pickle loaded")
with open(CHART_LOC+"rollupslot.pickle", "rb") as file:
    rollupslot = pickle.load(file)
print("rollupslot.pickle loaded")
with open(CHART_LOC+"beaconblock_over_time.pickle", "rb") as file:
    beaconblock_over_time = pickle.load(file)
print("beaconblock_over_time.pickle loaded")
with open(CHART_LOC+"calldataentities_over_time.pickle", "rb") as file:
    calldataentities_over_time = pickle.load(file)
print("calldataentities_over_time.pickle loaded")
with open(CHART_LOC+"fields4.pickle", "rb") as file:
    fields4 = pickle.load(file)
print("fields4.pickle loaded")
with open(CHART_LOC+"entity_pie.pickle", "rb") as file:
    entity_pie = pickle.load(file)
print("entity_pie.pickle loaded")
with open(CHART_LOC+"calldata_ratio.txt", "r") as file:
    calldata_gas_ratio = float(file.read())
print("calldata_ratio.txt loaded")
with open(CHART_LOC+"zeros_ratio.txt", "r") as file:
    zeros_ratio = float(file.read())
print("zeros_ratio.txt loaded")
with open(CHART_LOC+"calldata_summary.csv", "r") as file:
    calldata_summary = file.read().split(",")
print("calldata_summary.csv loaded")
with open(CHART_LOC+"blobs_over_time.pickle", "rb") as file:
    blobs_over_time = pickle.load(file)
print("blobs_over_time.pickle loaded")
with open(CHART_LOC+"entity_calldata_blob.pickle", "rb") as file:
    entity_calldata_blob = pickle.load(file)
print("entity_calldata_blob.pickle loaded")
with open(CHART_LOC+"blobentities_over_time.pickle", "rb") as file:
    blobentities_over_time = pickle.load(file)
print("blobentities_over_time.pickle loaded")
with open(CHART_LOC+"blob_for_rollup.pickle", "rb") as file:
    blob_for_rollup = pickle.load(file)
print("blob_for_rollup.pickle loaded")
with open(CHART_LOC+"blobs_fee_over_time.pickle", "rb") as file:
    blobs_fee_over_time = pickle.load(file)
print("blobs_fee_over_time.pickle loaded")
with open(CHART_LOC+'last_updated.txt', 'r') as f:
    last_updated = f.read().strip()
with open(CHART_LOC+"builder_over_time.pickle", "rb") as file:
    builder_over_time = pickle.load(file)
print("builder_over_time.pickle loaded")
with open(CHART_LOC+"relay_over_time.pickle", "rb") as file:
    relay_over_time = pickle.load(file)
print("relay_over_time.pickle loaded")
    