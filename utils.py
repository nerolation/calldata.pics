from datetime import datetime
import pandas as pd
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from sqlalchemy import text

from config import MAX_BLOCKS_TO_FETCH, init_heroku

testing = False

conn = init_heroku(testing)

def slot_to_time(slot):
    timestamp = 1606824023 + slot * 12
    dt_object = datetime.utcfromtimestamp(timestamp)
    formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time

def prep_livedata(_df):
    df = _df.copy()
    df.sort_values("slot", inplace=True)
    df.reset_index(drop=True, inplace=True)
    df["time"] = df["slot"].apply(lambda x: slot_to_time(x))    
    return df

def read_table_from_heroku(dataset_name, columns = "*"):
    return pd.read_sql_query(text(f"SELECT {columns} FROM {dataset_name} ORDER BY SLOT desc LIMIT {MAX_BLOCKS_TO_FETCH}"), conn)

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