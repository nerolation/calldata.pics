from datetime import datetime
import pandas as pd
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from sqlalchemy import text
import pytz

from config import MAX_BLOCKS_TO_FETCH, init_heroku

try:
    with open("config/testing.txt", "r") as file:
        testing = file.read().strip()
except:
    testing = False

conn = init_heroku(testing)

def slot_to_time(slot):
    timestamp = 1606824023 + slot * 12
    dt_object = datetime.utcfromtimestamp(timestamp)
    formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time

entities = {
    '0xc1b634853cb333d3ad8663715b08f41a3aec47cc': 'Arbitrum Batch Submitter',
    '0x6887246668a3b87f54deb3b94ba47a6f63f32985': 'Optimism Batcher',
    '0x5050f69a9786f081509234f1a7f4684b5e5b76c9': 'Base Batcher',
    '0x3527439923a63f8c13cf72b8fe80a77f6e572092': 'ZK Sync Validator',
    '0x01c3a1a6890a146ac187a019f9863b3ab2bff91e': 'zkSync: L2 Operator V1',
    '0x0d3250c3d5facb74ac15834096397a3ef790ec99': 'zkSync',
    '0x148ee7daf16574cd020afa34cc658f8f3fbd2800': 'Polygon zk EVM Sequencer',
    '0x22a82147a80747cfb1562e0f72f6be39f18b5f76': 'Starknet Operator',
    '0xc662c410c0ecf747543f5ba90660f6abebd9c8c4': 'Starknet Operator',
    '0xff6b2185e357b6e9136a1b2ca5d7c45765d5c591': 'Starknet Operator',
    '0x2c169dfe5fbba12957bdd0ba47d9cedbfe260ca7' : 'Starknet Operator',
    '0x356483dc32b004f32ea0ce58f7f88879886e9074': 'Scroll Batch Committer',
    '0xcf2898225ed05be911d3709d9417e86e0b4cfc8f': 'Scroll Batch Finalizer',
    '0x9228624c3185fcbcf24c1c9db76d8bef5f5dad64': 'Linea Finalization Operator',
    '0xa9268341831efa4937537bc3e9eb36dbece83c7e': 'Linea Data Operator',
    '0x6667961f5e9c98a76a48767522150889703ed77d': 'Mantle Rollup Asserter',
    '0x9cb01d516d930ef49591a05b09e0d33e6286689d': 'Metis State Commitment',
    '0x16d5783a96ab20c9157d7933ac236646b29589a4': 'SHARP Writer',
    '0x625726c858dbf78c0125436c943bf4b4be9d9033': 'Zora',
    '0x889e21d7ba3d6dd62e75d4980a4ad1349c61599d': 'Aevo',
    '0x41b8cd6791de4d8f9e0eaf7861ac506822adce12': 'Kroma',
    '0xfa46908b587f9102e81ce6c43b7b41b52881c57f': 'Boba',
    '0x14e4e97bdc195d399ad8e7fc14451c279fe04c8e': 'Lyra',
    '0x99199a22125034c808ff20f377d91187e8050f2e': 'Mode',
    '0x415c8893d514f9bc5211d36eeda4183226b84aa7': 'Blast',
    '0x6017f75108f251a488b045a7ce2a7c15b179d1f2': 'Fraxtal',
    '0x99526b0e49a95833e734eb556a6abaffab0ee167': 'PGN',
    '0xc70ae19b5feaa5c19f576e621d2bad9771864fe2': 'Paradex',
}

def prepare_blob_data(_df):
    df = _df.copy()
    df = df[df["slot"] > df["slot"].max() - 32*10]
    df["entity"] = df["address_from"].apply(lambda x: entities[x] if x in entities.keys() else x[0:10] + "...")
    largest = df.groupby("entity")["nr_blobs"].sum().reset_index().sort_values("nr_blobs", ascending=False)["entity"].tolist()[0:10]
    df = df[df["entity"].isin(largest)]
    df = df.groupby(["entity", "slot"])["nr_blobs"].sum().reset_index().sort_values("slot")
    df.set_index("entity", inplace=True)
    df = df.loc[largest]
    df.reset_index(inplace=True)
    df["slot"] = df["slot"].astype(int)
    df["time"] = df["slot"].apply(lambda x: slot_to_time(x))  
    return df


def prep_livedata(df):
    #df = _df.copy()
    df.sort_values("slot", inplace=True)
    df.reset_index(drop=True, inplace=True)
    df["time"] = df["slot"].apply(lambda x: slot_to_time(x))    
    return df

def read_table_from_heroku(dataset_name, columns = "*", sort_column="id"):
    return pd.read_sql_query(text(f"SELECT DISTINCT {columns} FROM {dataset_name} ORDER BY {sort_column} desc LIMIT {MAX_BLOCKS_TO_FETCH}"), conn)

def create_card(header, body):
    return dbc.Card([
        dbc.CardHeader(header),
        dbc.CardBody([
            html.H5(body, className="card-title"),
        ])
    ])

def create_row(args: list):
    return dbc.Row(
        [
            dbc.Col(dbc.Card(i, color="primary", outline=True)) for i in args
        ],
        className="mb-4",
    )

def convert_utc_to_timezone(utc_date_str, timezone_str):
    utc_date = datetime.strptime(utc_date_str, '%Y-%m-%d %H:%M')
    utc_date = utc_date.replace(tzinfo=pytz.utc)
    target_timezone = pytz.timezone(timezone_str)
    local_date = utc_date.astimezone(target_timezone)
    return html.H6(f"Last time updated: {local_date.strftime('%Y-%m-%d %H:%M')}", style={'color': '#ffffff', "text-align": 'right', "paddingRight":"1vw"})
