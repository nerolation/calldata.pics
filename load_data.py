import pickle
import pandas as pd

avgs = pd.read_parquet("averages.parquet")
calldatatxs = pd.read_parquet("calldatatxs.parquet")
entities_calldata_summary = pd.read_parquet("entities_calldata_summary.parquet")
with open("gasusageperday.pickle", "rb") as file:
    gasuageperday = pickle.load(file)
with open("beaconblock.pickle", "rb") as file:
    beaconblock = pickle.load(file)
with open("calldataovertime.pickle", "rb") as file:
    calldataovertime = pickle.load(file)
with open("calldatacumdist.pickle", "rb") as file:
    calldatacumdist = pickle.load(file)
with open("calldataslotlorenz.pickle", "rb") as file:
    calldataslotlorenz = pickle.load(file)
with open("calldatahist.pickle", "rb") as file:
    calldatahist = pickle.load(file)
with open("gas_used_over_time.pickle", "rb") as file:
    gas_used_over_time = pickle.load(file)
with open("cumulative_data_over_time.pickle", "rb") as file:
    cumulative_data_over_time = pickle.load(file)
with open("beaconblock_over_time.pickle", "rb") as file:
    beaconblock_over_time = pickle.load(file)
with open("calldataentities_over_time.pickle", "rb") as file:
    calldataentities_over_time = pickle.load(file)
with open("fields4.pickle", "rb") as file:
    fields4 = pickle.load(file)
with open("entity_pie.pickle", "rb") as file:
    entity_pie = pickle.load(file)
with open("calldata_ratio.txt", "r") as file:
    calldata_gas_ratio = float(file.read())
with open("zeros_ratio.txt", "r") as file:
    zeros_ratio = float(file.read())
with open("calldata_summary.csv", "r") as file:
    calldata_summary = file.read().split(",")
    
    