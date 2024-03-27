import dash
from dash import html, dcc, dash_table
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import numpy as np
import pickle
import time
import dash_cytoscape as cyto
import uuid
import copy
from appdesigns import tab_style, tab_selected_style, tabs_styles
import sqlite3
from sqlalchemy import create_engine, text
import sqlalchemy

from utils import *
from config import *
from load_data import *

import logging

logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.themes.DARKLY])

card_content_calldatasum_median = create_card("Median Calldata Per Block", f"{calldata_summary[0]} MB")
card_content_calldatasum_mean = create_card("Mean Calldata Per Block", f"{calldata_summary[1]} MB")
card_content_calldatasum_variance = create_card("Variance of Calldata Per Block", f"{calldata_summary[4]} MB")
card_content_calldatasum_max = create_card(f"Max Calldata Per Block (Block Number {calldata_summary[3]})", f"{calldata_summary[2]} MB")
card_content_median_gas_used = create_card("Median Gas Used Per Block", f"{int(avgs.iloc[0]['median_gas_used']):,} gas")
card_content_avg_gas_used = create_card("Avg. Gas Used Per Block (last 30d)", f"{int(avgs.iloc[0]['average_gas_used']):,} gas")
card_content_median_gas_max = create_card("Avg. Gas Used / Max. Possible (last 30d)", f"{int(avgs.iloc[0]['median_gas_used'])/30_000_000*100:,.2f} %")
card_content_blocksize_avg = create_card("Beacon Block Size / Snappy Compr. (last 30d)", f"{avgs.iloc[0]['median_size']:,.2f} MB / {avgs.iloc[0]['median_size_compressed']:,.2f} MB")
card_content_payload_avg = create_card("Avg. EL Payload Size / Snappy Compr. (last 30d)", f"{avgs.iloc[0]['median_el_size']:,.2f} MB / {avgs.iloc[0]['median_el_size_compressed']:,.2f} MB")
card_content_payload_share = create_card("EL Part of Beacon Block (last 30d)", f"{avgs.iloc[0]['median_el_size']/avgs.iloc[0]['median_size']*100:,.2f} %")
card_content_beacon_share = create_card("CL Part of Beacon Block (last 30d)", f"{(1-avgs.iloc[0]['median_el_size']/avgs.iloc[0]['median_size'])*100:,.2f} %")
card_content_calldata_ratio = create_card("Calldata Costs (last 30d)", f"{calldata_gas_ratio:,.0f} % of Gas is spent on Calldata")
card_content_evm_ratio = create_card("EVM Costs (last 30d)", f"{100-calldata_gas_ratio:,.0f} % of Gas is spent on EVM Operations")
card_content_zeros_ratio = create_card("Zero-Byte Ratio of Calldata (last 30d)", f"{zeros_ratio:,.0f} % of Calldata are Zero-Bytes")
card_content_non_zero_ratio = create_card("Non-Zero Byte Ratio of Calldata (last 30d)", f"{100-zeros_ratio:,.0f} % are Non-Zero Bytes")
card_content_calldata_size_avg = create_card("Avg. Calldata Non-Zero Bytes (last 30d)", f"{avgs.iloc[0]['median_calldatanonzeros']:,.0f} bytes")
card_content_calldata_size_median = create_card("Avg. Calldata Zero-Bytes (last 30d)", f"{avgs.iloc[0]['median_calldatazeros']:,.0f} bytes")
card_content_calldata_zero_ratio = create_card("Non-Zero Byte Ratio of Calldata (last 30d)", f"{100-zeros_ratio:,.0f} % are Non-Zero Bytes")
card_content_30q_ratio = create_card("30% of transactions calldata size", f'have less than {calldatatxs["percentile03"].iloc[0]+1:,.0f} bytes')
card_content_50q_ratio = create_card("50% of transactions calldata size", f'have less than {calldatatxs["percentile05"].iloc[0]+1:,.0f} bytes')
card_content_70q_ratio = create_card("70% of transactions calldata size", f'have less than {calldatatxs["percentile07"].iloc[0]+1:,.0f} bytes')
card_content_90q_ratio = create_card("90% of transactions calldata size", f'have less than {calldatatxs["percentile09"].iloc[0]+1:,.0f} bytes')

card_content_total_blobs = create_card(
    "Total Blobs (last 24h)", 
    f"{blob_summary_data['Total Blobs']} " + f"({blob_summary_data['delta_total']}%" + (" ⬆️)" if int(blob_summary_data["delta_total"]) > 0 else " ⬇️)")
)

card_content_total_blobs_in_gib = create_card(
    "Total Blobs in MiB (last 24h)", 
    f"{blob_summary_data['Total Blobs in GB']} " + f"({blob_summary_data['delta_total_gb']}%" + (" ⬆️)" if int(blob_summary_data["delta_total_gb"]) > 0 else " ⬇️)")
)

card_content_avg_blob_per_slot = create_card(
    "Avg. #Blobs Per Slot (last 24h)", 
    f"{blob_summary_data['Avg. #Blobs Per Slot']} " + f"({blob_summary_data['delta_avg']}%" + (" ⬆️)" if int(blob_summary_data["delta_avg"]) > 0 else " ⬇️)")
)

card_content_avg_blob_price = create_card(
    "Avg. Blob Gas Price (last 24h)", 
    f"{blob_summary_data['Avg. Blob Gas Price']} " + f"({blob_summary_data['delta_price']}%" + (" ⬆️)" if int(blob_summary_data["delta_price"]) > 0 else " ⬇️)")
)


row_blob = create_row([
    card_content_total_blobs, 
    card_content_total_blobs_in_gib,
    card_content_avg_blob_per_slot,
    card_content_avg_blob_price
])


row_1 = create_row([
    card_content_avg_gas_used, 
    card_content_median_gas_used, 
    card_content_median_gas_max
])

row_2 = create_row([
    card_content_blocksize_avg, 
    card_content_payload_avg, 
    card_content_payload_share
])

row_3 = create_row([
    card_content_calldata_ratio, 
    card_content_evm_ratio, 
    card_content_zeros_ratio, 
    card_content_non_zero_ratio
])

row_4 = create_row([
    card_content_30q_ratio, 
    card_content_50q_ratio, 
    card_content_70q_ratio, 
    card_content_90q_ratio
])

row_5 = create_row([
    card_content_calldata_size_avg, 
    card_content_calldata_size_median, 
    card_content_calldata_zero_ratio
])

row_6 = create_row([
    card_content_beacon_share, 
    card_content_payload_share
])

row_61 = create_row([
    card_content_evm_ratio, 
    card_content_calldata_ratio
])

row_7 = create_row([
    card_content_calldatasum_median, 
    card_content_calldatasum_mean, 
    card_content_calldatasum_max, 
    card_content_calldatasum_variance
])

#cards = html.Div([row_2, row_3], style={'padding-top': '20px', 'marginLeft': '1vw', 'marginRight': '1vw'})
cards0 = html.Div([row_1], style={'padding-top': '20px', 'marginLeft': '2vw', 'marginRight': '2vw'})
#cards2 = html.Div([row_4], style={'padding-top': '20px', 'marginLeft': '2vw', 'marginRight': '2vw'})
cards3 = html.Div([row_5], style={'padding-top': '20px', 'marginLeft': '2vw', 'marginRight': '2vw'})
cards4 = html.Div([row_2], style={'padding-top': '20px', 'marginLeft': '2vw', 'marginRight': '2vw'})
cards5 = html.Div([row_6], style={'padding-top': '20px', 'marginLeft': '1vw', 'marginRight': '1vw'})
cards51 = html.Div([row_61], style={'padding-top': '20px', 'marginLeft': '1vw', 'marginRight': '1vw'})
cards6 = html.Div([row_7], style={'padding-top': '20px', 'marginLeft': '1vw', 'marginRight': '1vw'})

cards_blobs_0 =  html.Div([row_blob], style={'padding-top': '0px', 'marginLeft': '1vw', 'marginRight': '1vw', 'marginBottom': '0vw'})


entity_table = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in entities_calldata_summary.columns if i != "tx_count"],
    data=entities_calldata_summary.to_dict('records'),
    style_table={'height': '450px', 'overflowY': 'auto', "paddingLeft": "2vw", "paddingRight": "2vw", "display": "inline-block", "fontSize": "10pt"},
    style_cell={
        'color': 'white',
        'backgroundColor': 'black',
        'border': 'none'
    },
    style_header={
        'backgroundColor': '#222',
        'fontWeight': 'bold',
        'color': 'white',
        'border': 'none'
    },
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#303030'
        },
        {
            'if': {'row_index': 'even'},
            'backgroundColor': 'black'
        }
    ],
)

entity_table_blobs = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in entities_blob_summary.columns],
    data=entities_blob_summary.to_dict('records'),
    style_table={'height': '450px', 'overflowY': 'auto', "paddingLeft": "2vw", "paddingRight": "2vw", "display": "inline-block", "fontSize": "10pt", "marginBottom":"10vh"},
    style_cell={
        'color': 'white',
        'backgroundColor': 'black',
        'border': 'none'
    },
    style_header={
        'backgroundColor': '#222',
        'fontWeight': 'bold',
        'color': 'white',
        'border': 'none'
    },
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#303030'
        },
        {
            'if': {'row_index': 'even'},
            'backgroundColor': 'black'
        }
    ],
)

builder_table_blobs = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in builder_blob_summary.columns],
    data=builder_blob_summary.to_dict('records'),
    style_table={'height': '450px', 'overflowY': 'auto', "paddingLeft": "2vw", "paddingRight": "2vw", "display": "inline-block", "fontSize": "10pt", "marginBottom":"10vh"},
    style_cell={
        'color': 'white',
        'backgroundColor': 'black',
        'border': 'none'
    },
    style_header={
        'backgroundColor': '#222',
        'fontWeight': 'bold',
        'color': 'white',
        'border': 'none'
    },
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#303030'
        },
        {
            'if': {'row_index': 'even'},
            'backgroundColor': 'black'
        }
    ],
)

relay_table_blobs = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in relay_blob_summary.columns],
    data=relay_blob_summary.to_dict('records'),
    style_table={'height': '450px', 'overflowY': 'auto', "paddingLeft": "2vw", "paddingRight": "2vw", "display": "inline-block", "fontSize": "10pt", "paddingBottom":"10vh"},
    style_cell={
        'color': 'white',
        'backgroundColor': 'black',
        'border': 'none'
    },
    style_header={
        'backgroundColor': '#222',
        'fontWeight': 'bold',
        'color': 'white',
        'border': 'none'
    },
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#303030'
        },
        {
            'if': {'row_index': 'even'},
            'backgroundColor': 'black'
        }
    ],
)



def generate_blob_data_content():
    content = html.Div(
        [
            cards_blobs_0,
            html.Div(
                [
                    html.H4("Blobs per Entity"),
                    dcc.Graph(
                        figure=blobentities_over_time,
                        style={"marginBottom": "0vh"},
                        config={"displayModeBar": False},
                    ),
                ],
                style={"width": "100%", "marginBottom": "0vh", "marginTop": "5vh"},
            ),
            dbc.Row(entity_table_blobs),
            
            
            html.Div(
                [
                    html.H4("Blobs per Block Builder"),
                    dcc.Graph(
                        figure=builder_over_time,
                        style={"marginBottom": "0vh"},
                        config={"displayModeBar": False},
                    ),
                ],
                style={"width": "100%", "marginBottom": "0vh"},
            ),
            dbc.Row(builder_table_blobs),
            html.Div(
                [
                    html.H4("Blobs per MEV-Boost Relay"),
                    dcc.Graph(
                        figure=relay_over_time,
                        style={"marginBottom": "0vh"},
                        config={"displayModeBar": False},
                    ),
                ],
                style={"width": "100%", "marginBottom": "0vh"},
            ),
            dbc.Row(relay_table_blobs,  style={"marginTop": "0vh"}),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H4("Cumulative Nr. of Blobs"),
                                dcc.Graph(
                                    figure=blobs_over_time,
                                    style={"marginBottom": "10vh"},
                                    config={"displayModeBar": False},
                                ),
                            ],
                            style={"width": "100%", "marginBottom": "1vh"},
                        ),
                        width=12,
                        md=6,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H4("Blob Share (last 7 days)"),
                                dcc.Graph(
                                    id="daily-transactions3",
                                    figure=entity_calldata_blob,
                                    className="graph-container",
                                    config={"displayModeBar": False},
                                ),
                            ]
                        ),
                        width=12,
                        md=6,
                    ),
                ],
                style={"width": "100%", "marginBottom": "1vh"},
            ),
            html.Div(
                [
                    html.H4("Blobs over Slots in Epoch"),
                    dcc.Graph(
                        figure=blob_for_rollup,
                        style={"marginBottom": "10vh"},
                        config={"displayModeBar": False},
                    ),
                ],
                style={"width": "100%", "marginBottom": "10vh"},
            ),       
        ],
    )
    return content


def generate_rollup_data_content():
    content = html.Div(
        [
            html.Div(
                [
                    html.H4("Daily Calldata Usage Per Entity"),
                    dcc.Graph(
                        figure=calldataentities_over_time,
                        style={"marginBottom": "10vh"},
                        config={"displayModeBar": False},
                    ),
                ],
                style={"width": "100%", "marginBottom": "10vh"},
            ),
            html.Div(
                [
                    html.H4("Calldata Posting Over Slot in Epoch (last 30 days)"),
                    dcc.Graph(
                        figure=rollupslot,
                        style={"marginBottom": "10vh"},
                        config={"displayModeBar": False},
                    ),
                ],
                style={"width": "100%", "marginBottom": "10vh"},
            ),
            dbc.Row(
                [
                    dbc.Col(entity_table, width=12, md=6),
                    dbc.Col(
                        html.Div(
                            [
                                html.H4("Calldata Share (last 30 days)"),
                                dcc.Graph(
                                    id="daily-transactions3",
                                    figure=entity_pie,
                                    className="graph-container",
                                    config={"displayModeBar": False},
                                ),
                            ]
                        ),
                        width=12,
                        md=6,
                    ),
                ],
                style={"width": "100%", "marginBottom": "10vh"},
            ),
            
        ],
    )
    return content


def generate_calldata_data_content():
    content = dcc.Loading([
            html.Div(
                [
                    html.H4("Calldata Used Per Day"),
                    dcc.Graph(figure=cumulative_data_over_time, config={"displayModeBar": False}),
                    cards3,
                ],
                style={
                    "width": "100%",
                    "marginBottom": "10vh",
                    "margin-top": "2vh",
                },
            ),
            html.Div(
                [
                    html.H4("Average and Max. Calldata Usage Over Time"),
                    dcc.Graph(figure=calldataovertime, config={"displayModeBar": False}),
                    cards6,
                ],
                style={"width": "100%", "marginBottom": "10vh"},
            ),
            html.Div(
                [
                    dcc.Graph(
                        id="calldata_evm_gas_share",
                        figure=gasuageperday,
                        config={"displayModeBar": False}
                    ),
                    cards51,
                ],
                style={"width": "100%", "marginBottom": "10vh"},
            ),
            html.Div(
                [
                    html.H4("Calldata Usage (In-)Equality"),
                    dcc.Graph(
                        id="calldatacumdist",
                        figure=calldatacumdist,
                        className="graph-container",
                        style={"width": "100%"},
                        config={"displayModeBar": False}
                    ),
                ],
                style={"width": "100%", "marginBottom": "10vh"},
            ),
        
            html.Div(
                children=[
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    children=[
                                        html.H4("Calldata Distribution"),
                                        dcc.Graph(
                                            id="daily-transactions2",
                                            figure=calldatahist,
                                            className="graph-container",
                                            style={"width": "50%"},
                                            config={"displayModeBar": False}
                                        )
                                    ]
                                )
                            ),
                            dbc.Col(
                                dcc.Graph(
                                    id="daily-transactions4",
                                    figure=calldataslotlorenz,
                                    className="graph-container",
                                    style={"width": "50%"},
                                    config={"displayModeBar": False}
                                )),
                        ]
                    )
                    
                ]
            ),
        ])
        
    return content
    
def generate_historic_data_content():
    content = html.Div(
        [
            html.Div(
                children=[
                    dcc.Loading(
                        id="loading-0",
                        type="default",
                        children=[
                            html.Div(
                                [
                                    html.H4("Gas Usage Per Day"),
                                    dcc.Graph(figure=gas_used_over_time, config={"displayModeBar": False}),
                                    cards0,
                                ],
                                style={
                                    "width": "100%",
                                    "marginBottom": "10vh",
                                    "margin-top": "2vh",
                                },
                        )]
                    ),
                    dcc.Loading(
                        html.Div(
                            [
                                html.H4("Snappy Compressed Beacon Block Size over Time"),
                                dcc.Graph(figure=beaconblock_over_time, config={"displayModeBar": False}),
                                cards4,
                            ],
                            style={
                                "width": "100%",
                                "marginBottom": "10vh",
                                "margin-top": "2vh",
                            },
                        )
                    ),
                    dcc.Loading(
                        html.Div(
                            [
                                html.H4("Snappy Compressed Beacon Block Size over Time"),
                                dcc.Graph(figure=maxblockvsavg, config={"displayModeBar": False}),
                                cards4,
                            ],
                            style={
                                "width": "100%",
                                "marginBottom": "10vh",
                                "margin-top": "2vh",
                            },
                        )
                    ),
                    html.H4("Beacon Block Components"),
                    dcc.Graph(
                        id="beaconblock_el_share",
                        figure=beaconblock,
                        config={"displayModeBar": False},
                    ),
                    cards5
                ],
                style={"padding-bottom": "10vh"},
            ),            
        ],
    )
    return content


spinner = html.Div(
    children=[
        dbc.Spinner(spinner_style={"width": "3rem", "height": "3rem"}), 
        html.Span(["       "], style={"paddingRight":"1vw"}),
        "Loading..."
    ],
    id="loadingspinner", style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', "paddingTop": "3vh"}
)

spinner1 = html.Div(
    children=[
        dbc.Spinner(spinner_style={"width": "3rem", "height": "3rem"}), 
        html.Span(["       "], style={"paddingRight":"1vw"}),
        "Loading..."
    ],
    id="loadingspinner1", style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', "paddingTop": "3vh"}
)



spinner2 = html.Div(
    children=[
        dbc.Spinner(spinner_style={"width": "3rem", "height": "3rem"}), 
        html.Span(["       "], style={"paddingRight":"1vw"}),
        "Loading..."
    ],
    id="loadingspinner2", style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', "paddingTop": "3vh"}
)

spinner3 = html.Div(
    children=[
        dbc.Spinner(spinner_style={"width": "3rem", "height": "3rem"}), 
        html.Span(["       "], style={"paddingRight":"1vw"}),
        "Loading..."
    ],
    id="loadingspinner3", style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', "paddingTop": "3vh"}
)


app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-ZS0X24WZTE"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'G-ZS0X24WZTE');
        </script>
        <meta charset="UTF-8">
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:site" content="@nero_ETH">
        <meta name="twitter:title" content="Ethereum Calldata Dashboard">
        <meta name="twitter:description" content="Insights into block sizes and calldata + blob usage on the Ethereum blockchain.">
        <meta name="twitter:image" content="https://raw.githubusercontent.com/nerolation/calldata.pics/main/assets/calldatagames_og_image.jpg">
        <meta property="og:title" content="Calldata.pics" relay="" api="" dashboard="">
        <meta property="og:site_name" content="calldata.pics">
        <meta property="og:url" content="calldata.pics">
        <meta property="og:description" content="Insights into block sizes and calldata + blob usage on the Ethereum blockchain.">
        <meta property="og:type" content="website">
        <meta property="og:image" content="https://raw.githubusercontent.com/nerolation/calldata.pics/main/assets/calldatagames_og_image.jpg">
        <meta name="description" content="Insights into block sizes and calldata + blob usage on the Ethereum blockchain.">
        <meta name="keywords" content="Ethereum, Calldata, Blobs, DotPics, Dashboard">
        <meta name="author" content="Toni Wahrstätter">
        <link rel="shortcut icon" href="https://raw.githubusercontent.com/nerolation/calldata.pics/main/assets/favicon.png">
        {%metas%}
        <title>{%title%}</title>
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.clientside_callback(
    "window.dash_clientside.update_window_size",
    Output('window-size-store', 'data'),
    Input('window-size-trigger', 'n_intervals')
)

app.title = 'Calldata.pics'
server = app.server

app.layout = html.Div(
    [
        html.H1("Calldata.pics", style={"textAlign": "center", "marginBottom": "2vh", "marginTop": "2vh"}),
        dbc.Row(dcc.Interval(id='window-size-trigger', interval=1000, n_intervals=0, max_intervals=1)),
        dcc.Store(id='window-size-store', data={'width': None}),
        dcc.Store(id="timezone-store"),
        dcc.Store(id="stored-data"),
        dcc.Store(id="stored-data2"),
        dbc.Row([
            dbc.Col(html.Div([
                html.H6([
                    "Built with 🤍 by ",
                    html.A("Toni Wahrstätter", href="https://twitter.com/nero_eth", target="_blank", 
                           style={'color': '#ffffff'})
                ], style={'color': '#ffffff'}),
            ], style={'display': 'flex', 'align-items': 'center'}), width=6),
            dbc.Col(
                html.Div(
                    id="last-updated",
                    children=[html.H6(f"Last time updated: {last_updated}", style={'color': '#ffffff', "text-align": 'right', "paddingRight":"1vw"})],
                    style={'display': 'flex', 'align-items': 'center', 'justify-content': 'flex-end'},
                ), width=6
            )
        ]),
        dbc.Row([
            dbc.Col(html.Div(
                children=[html.P("")],
                style={'display': 'flex', 'align-items': 'center'},
            ), width=6),
            dbc.Col(html.Div(
                id="timezone-display",
                children=[html.H6("Time zone: ")],
                style={'color': '#ffffff', "text-align": 'right', "paddingRight":"1vw"},
            ), width=6),
        ]),
        html.Div([], className="mobilespace"),
        dcc.Interval(
            id="interval-timezone-update", interval=3600 * 1000, n_intervals=0
        ),
        html.Div([
            dcc.Tabs(
                id="tabs",
                value="tab-1",
                children=[
                    dcc.Tab(
                        label="Live Data",
                        value="tab-1",
                        children=[
                            html.H2("Live Blob Usage", style={"margin-top": "5vh"}),
                            dcc.Graph(
                                id="live-blob-chart",
                                style={"margin-bottom": "5vh", "height": "40vh"},
                                config={"displayModeBar": False},
                            ),
                            html.H2("Live Blob Gas Price", style={"margin-top": "5vh"}),
                            dcc.Graph(
                                id="live-bubble-chart6",
                                style={"margin-bottom": "5vh", "height": "40vh"},
                                config={"displayModeBar": False},
                            ),
                            html.H2("Live Block Size", style={"margin-top": "5vh"}),
                            dcc.Graph(
                                id="live-bubble-chart",
                                style={"margin-bottom": "5vh", "height": "40vh"},
                                config={"displayModeBar": False},
                            ),
                            dcc.Interval(
                                id="interval-component", interval=2000, n_intervals=0
                            ),
                            html.H2("Live Gas Usage"),
                            dcc.Graph(
                                id="live-bubble-chart2",
                                style={"margin-bottom": "5vh", "height": "40vh"},
                                config={"displayModeBar": False},
                            ),
                            html.H2("Beacon Block Compression (Snappy)"),
                            dcc.Graph(
                                id="live-bubble-chart3",
                                style={"margin-bottom": "5vh", "height": "40vh"},
                                config={"displayModeBar": False},
                            ),
                            html.H2("Live Calldata Usage", style={"margin-top": "5vh"}),
                            dcc.Graph(
                                id="live-bubble-chart4",
                                style={"margin-bottom": "5vh", "height": "40vh"},
                                config={"displayModeBar": False},
                            ),
                            html.H2("Live Blob Usage", style={"margin-top": "5vh"}),
                            dcc.Graph(
                                id="live-bubble-chart5",
                                style={"margin-bottom": "5vh", "height": "40vh"},
                                config={"displayModeBar": False},
                            ),
                        ],
                        style={},
                        selected_className='tab-selected-style',
                        className='tab-style custom-tab'
                    ),
                    dcc.Tab(
                        label='Historic Size Data', 
                        value='tab-2', 
                        children=[
                            spinner,
                            html.Div(id='historic-data-content')
                        ], 
                        style={},
                        selected_className='tab-selected-style',
                        className='tab-style custom-tab'
                    ),
                    dcc.Tab(
                        label='Blob Data', 
                        value='tab-blob', 
                        children=[
                            spinner1,
                            html.Div(id='blob-data-content')
                        ], 
                        style={},
                        selected_className='tab-selected-style',
                        className='tab-style custom-tab'
                    ),
                    dcc.Tab(
                        label='Rollups/L2s', 
                        value='tab-3', 
                        children=[
                            spinner2,
                            html.Div(id='rollup-data-content')
                        ], 
                        style={},
                        selected_className='tab-selected-style',
                        className='tab-style custom-tab'
                    ),
                    dcc.Tab(
                        label='Calldata', 
                        value='tab-4', 
                        children=[
                            spinner3,
                            html.Div(id='calldata-data-content')
                        ], 
                        style={},
                        selected_className='tab-selected-style',
                        className='tab-style custom-tab'
                    ),
                ],
                style={},
                className="tabs-styles",
            )
        ], style={}, className="tab-container"),
    ],
    style={"marginLeft": "1vw"},
)


def generate_live_blobs_per_entity_chart(_df, _font_size_delta):
    df = _df.copy()
    df['entity_id'] = df['entity'].astype('category').cat.codes
    df['size'] = df['nr_blobs'] * 1  # Scale factor for bubble size
    fig = px.scatter(df, x='time', y='entity_id', size='size', color='entity', hover_name='entity',
                     size_max=10, title='Blobs Posted to Ethereum Mainnet Over Time', custom_data=["size","slot"]
    )
    hovertext = '%{customdata[1]:,.0f}<br>%{y}: %{customdata[0]:,.0f} blobs<extra></extra>'
    fig.update_traces(hovertemplate=hovertext)
    fig.update_yaxes(tickvals=df['entity_id'], ticktext=df['entity'])
    #ticks = list(range(df['slot'].min() - df['slot'].min()%32, df['slot'].max()))
    #if len(ticks) > 32*2:
    #    ticks =  ticks[::32] + list(range(ticks[-32], ticks[-1])) + [ticks[-1] + 2]
    #    ticktext = [i//32 for i in list(range(df['slot'].min() - df['slot'].min()%32 + 32, df['slot'].max(), 32))]
    #    ticktext = ticktext + [str(i) for i in list(range(ticks[-32], ticks[0]))]
    #else:
    #    ticks = ticks[::2] + [ticks[-1] + 2]
    #    ticktext = [f"{i:,}" for i in ticks]
    
    fig.update_layout(
        title=None,
        xaxis_title="Slot/Epochs",
        yaxis_title=None,
        margin={"t": 0, "b": 50, "r": 50, "l": 50},
        dragmode=False,
        plot_bgcolor="#0a0a0a",
        paper_bgcolor="#0a0a0a",
        font=dict(
            color="white",
            size=16-_font_size_delta
        ),
        legend=dict(
            yanchor="top",
            y=1,
            xanchor="left",
            x=0.91,
            bgcolor='rgba(10, 10, 10, 0)',
            font=dict(
                color="white",
                size=16-_font_size_delta
            ),
        ),
        showlegend=False,
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="white",
            font_size=16-_font_size_delta,
            font_family="Ubuntu Mono",
            font_color="black"
        ),

        xaxis=dict(
            fixedrange=True,
            gridcolor="rgba(255, 255, 255, 0.5)",
            #tickvals = ticks,
            #ticktext = ticktext
        ),
        yaxis=dict(
            fixedrange=True,
            gridcolor="rgba(255, 255, 255, 0.5)"
        ),
    )
    return fig



app.clientside_callback(
    """
    function(n_intervals) {
        return window.dash_clientside.timezone || 'UTC';
    }
    """,
    Output('timezone-store', 'data'),
    [Input('interval-timezone-update', 'n_intervals')]
)

@app.callback([
    Output('live-bubble-chart', 'figure'),
    Output('live-bubble-chart2', 'figure'),
    Output('live-bubble-chart3', 'figure'),
    Output('live-bubble-chart4', 'figure'),
    Output('live-bubble-chart5', 'figure'),
    Output('live-bubble-chart6', 'figure'),
    Output('live-blob-chart', 'figure'),
    Output('stored-data', 'data'),
    Output('stored-data2', 'data'),
    Output('timezone-display', 'children'),
    Output('last-updated', 'children')
], [
    Input('interval-component', 'n_intervals'),
    State('timezone-store', 'data'),
    State('stored-data', 'data'),
    State('stored-data2', 'data'),
    Input('window-size-store', 'data')]
)
def update_line_chart(n, tz_info, stored_data, stored_data2, size_data): 
    width = size_data['width']
    df = pd.DataFrame() if n == 0 or stored_data is None else pd.DataFrame.from_records(stored_data)
    df_blobs = pd.DataFrame(columns=["slot", "time"]) if n == 0 or stored_data2 is None else pd.DataFrame.from_records(stored_data2)
    last_updated_new = last_updated
    if (n == 0 or stored_data is None or n % (MAX_BLOCKS_TO_FETCH - 25) == 0) and n <= 600:
        #print("extending data")
        _df = read_table_from_heroku("blocks")
        _df_blobs = read_table_from_heroku("blobs", "*", "slot")
        _df = prep_livedata(_df)
        _df_blobs = prepare_blob_data(_df_blobs)
        df = pd.concat([df, _df], ignore_index=True).drop_duplicates()
        df_blobs = pd.concat([df_blobs, _df_blobs], ignore_index=True).drop_duplicates()
        stored_data = df.to_dict('records')
        stored_data2 = df_blobs.to_dict('records')
    elif stored_data is None:
        raise PreventUpdate
    
    SHOW_INITIALLY = 10
    user_timezone = tz_info if tz_info else 'UTC'
    df['time'] = pd.to_datetime(df['time'])
    df_blobs['time'] = pd.to_datetime(df_blobs['time'])
    last_updated_new = convert_utc_to_timezone(last_updated, user_timezone)
    if df['time'].dt.tz is None:
        df['time'] = pd.to_datetime(df['time']).dt.tz_localize('UTC').dt.tz_convert(user_timezone)
        df_blobs['time'] = pd.to_datetime(df_blobs['time']).dt.tz_localize('UTC').dt.tz_convert(user_timezone)
    else:
        df['time'] = df['time'].dt.tz_convert(user_timezone)
        df_blobs['time'] = df_blobs['time'].dt.tz_convert(user_timezone)
    timezone_text = f"Time zone: {tz_info}"
    
    block_size_compressed = df.iloc[0:n+SHOW_INITIALLY]["size_compressed"]/1024**2
    el_block_size_compressed = df.iloc[0:n+SHOW_INITIALLY]["el_size_compressed"]/1024**2
    block_size_nc = df.iloc[0:n+SHOW_INITIALLY]["size"]/1024**2
    calldata_zeros = df.iloc[0:n+SHOW_INITIALLY]["calldatazeros"]/1024**2
    calldata_nonzeros = df.iloc[0:n+SHOW_INITIALLY]["calldatanonzeros"]/1024**2
    nr_blobs = df.iloc[0:n+SHOW_INITIALLY]["nr_blobs"] * 128/1024
    gas_usage = df.iloc[0:n+SHOW_INITIALLY]["gas_used"]
    days = df.iloc[0:n+SHOW_INITIALLY]["time"]
    slots = df.iloc[0:n+SHOW_INITIALLY]["slot"]

    if width <= 800:
        _font_size_delta = 4
    else:
        _font_size_delta = 0
        
    blobs_to_show = df_blobs[df_blobs["slot"].isin(slots)]
    if len(blobs_to_show.index) > 0:
        figure_blobs = generate_live_blobs_per_entity_chart(blobs_to_show, _font_size_delta)
    else:
        figure_blobs = go.Figure()
        figure_blobs.update_layout(
            plot_bgcolor="#0a0a0a",
            paper_bgcolor="#0a0a0a",
            xaxis=dict(
                    fixedrange=True,
                    showgrid=False
                ),
            yaxis=dict(
                    fixedrange=True,
                    showgrid=False
                ), 
        )     
    
    figure = go.Figure(data=[go.Scatter(
        x=days,
        y=block_size_compressed,
        mode='lines+markers',
        fillcolor='rgba(92, 185, 250, 0.6)', line_color='rgba(92, 185, 250, 0.6)',
        line_width=4,
        name="Beacon Block",
        customdata=slots,
        hovertemplate='Slot: %{customdata:,}<br>Beacon Block Size: %{y:.2f} MB<extra></extra>',

    ), go.Scatter(
        x=days,
        y=el_block_size_compressed,
        mode='lines+markers',
        fillcolor='rgba(255, 127, 14, 0.6)', line_color='rgba(255, 127, 14, 0.6)',
        name="EL Payload",
        line_width=4,
        customdata=slots,
        hovertemplate='EL Payload Size: %{y:.2f} MB<extra></extra>',

    )])
    figure.add_trace(go.Scatter(
        x=days,
        y=avgs["median_size_compressed"].tolist()*len(days),
        mode='lines',
        line=dict(color='red', dash='longdash', width=2),
        hovertemplate='30d Avg Calldata Size: %{y:.2f} MB<extra></extra>',
        name='30d average'
    ))

    figure.update_layout(
        title=None,
        xaxis_title="Time",
        yaxis_title="MB",
        dragmode=False,
        plot_bgcolor="#0a0a0a",
        paper_bgcolor="#0a0a0a",
        margin={"t": 0, "b": 0, "r": 50, "l": 50},
        font=dict(
            color="white",
            size=16-_font_size_delta
        ),
        legend=dict(
            yanchor="top",
            y=1,
            xanchor="left",
            x=0.91,
            bgcolor='rgba(10, 10, 10, 0)',
            font=dict(
                color="white",
                size=16-_font_size_delta
            ),
        ),
        hovermode="x unified",
        xaxis=dict(
            fixedrange=True,
            gridcolor="rgba(255, 255, 255, 0.5)"
        ),
        yaxis=dict(
            fixedrange=True,
            gridcolor="rgba(255, 255, 255, 0.5)"
        ),
    )
    figure2 = go.Figure(data=[go.Scatter(
        x=days,
        y=gas_usage,
        mode='lines+markers',
        fillcolor='rgba(255, 127, 14, 0.6)', line_color='rgba(255, 127, 14, 0.6)',
        line_width=4,
        name="Beacon Block",
        customdata=slots,
        hovertemplate='Slot: %{customdata:,}<br>Gas Used: %{y:,.0f} GAS<extra></extra>',

    )])
    figure2.add_trace(go.Scatter(
        x=days,
        y=avgs["median_gas_used"].tolist()*len(days),
        mode='lines',
        line=dict(color='red', dash='longdash', width=2),
        name='30d average',
        hovertemplate='Median: %{y:,.0f} GAS<extra></extra>',
        
    ))

    figure2.update_layout(
        title=None,
        xaxis_title="Time",
        yaxis_title="MB",
        margin={"t": 0, "b": 0, "r": 50, "l": 50},
        dragmode=False,
        plot_bgcolor="#0a0a0a",
        paper_bgcolor="#0a0a0a",
        font=dict(
            color="white",
            size=16-_font_size_delta
        ),
        legend=dict(
            yanchor="top",
            y=1,
            xanchor="left",
            x=0.91,
            bgcolor='rgba(10, 10, 10, 0)',
            font=dict(
                color="white",
                size=16-_font_size_delta
            ),
        ),
        hovermode="x unified",
        xaxis=dict(
            fixedrange=True,
            gridcolor="rgba(255, 255, 255, 0.5)"
        ),
        yaxis=dict(
            fixedrange=True,
            gridcolor="rgba(255, 255, 255, 0.5)"
        ),
    )

    figure3 = go.Figure(data=[go.Scatter(
        x=days,
        y=block_size_compressed,
        mode='lines+markers',
        fillcolor='rgba(255, 127, 14, 0.6)', line_color='rgba(255, 127, 14, 0.6)',
        line_width=4,
        name="Snappy Compressed",
        customdata=slots,
        hovertemplate='Slot: %{customdata:,}<br>Compressed Size: %{y:.2f} MB<extra></extra>',

    ), go.Scatter(
        x=days,
        y=block_size_nc,
        mode='lines+markers',
        fillcolor='rgba(92, 185, 250, 0.6)', line_color='rgba(92, 185, 250, 0.6)',
        name="No Compression",
        line_width=4,
        customdata=slots,
        hovertemplate='Non-Compressed Size: %{y:.2f} MB<extra></extra>',

    )])

    figure3.update_layout(
        title=None,
        xaxis_title="Time",
        yaxis_title="MB",
        dragmode=False,
        margin={"t": 0, "b": 0, "r": 50, "l": 50},
        plot_bgcolor="#0a0a0a",
        paper_bgcolor="#0a0a0a",
        font=dict(
            color="white",
            size=16-_font_size_delta
        ),
        legend=dict(
            yanchor="top",
            y=1,
            xanchor="left",
            x=0.89,
            bgcolor='rgba(10, 10, 10, 0)',
            font=dict(
                color="white",
                size=16-_font_size_delta
            ),
        ),
        hovermode="x unified",
        xaxis=dict(
            fixedrange=True,
            gridcolor="rgba(255, 255, 255, 0.5)"
        ),
        yaxis=dict(
            fixedrange=True,
            gridcolor="rgba(255, 255, 255, 0.5)"
        ),
    )
    figure4 = go.Figure(data=[go.Scatter(
        x=days,
        y=calldata_zeros,
        mode='lines+markers',
        fillcolor='rgba(255, 127, 14, 0.6)', line_color='rgba(255, 127, 14, 0.6)',
        line_width=4,
        name="Zero-Bytes",
        customdata=slots,
        hovertemplate='Slot: %{customdata:,}<br>Zero-Bytes: %{y:.2f} MB<extra></extra>',

    ), go.Scatter(
        x=days,
        y=calldata_nonzeros,
        mode='lines+markers',
        fillcolor='rgba(92, 185, 250, 0.6)', line_color='rgba(92, 185, 250, 0.6)',
        name="Non-Zero Bytes",
        line_width=4,
        customdata=slots,
        hovertemplate='Non-Zero Bytes: %{y:.2f} MB<extra></extra>',

    )])
    figure4.update_layout(
        title=None,
        xaxis_title="Time",
        yaxis_title="MB",
        margin={"t": 0, "b": 0, "r": 50, "l": 50},
        plot_bgcolor="#0a0a0a",
        paper_bgcolor="#0a0a0a",
        font=dict(
            color="white",
            size=16-_font_size_delta
        ),
        legend=dict(
            yanchor="top",
            y=1,
            xanchor="left",
            x=0.91,
            bgcolor='rgba(10, 10, 10, 0)',
            font=dict(
                color="white",
                size=16-_font_size_delta
            ),
        ),
        dragmode=False,
        hovermode="x unified",
        xaxis=dict(
            fixedrange=True,
            gridcolor="rgba(255, 255, 255, 0.5)"
        ),
        yaxis=dict(
            fixedrange=True,
            gridcolor="rgba(255, 255, 255, 0.5)"
        ),
    )
    figure5 = go.Figure(data=[go.Scatter(
        x=days,
        y=nr_blobs,
        mode='lines+markers',
        fillcolor='rgba(255, 127, 14, 0.6)', line_color='rgba(255, 127, 14, 0.6)',
        line_width=4,
        name="Blobs",
        customdata=slots,
        hovertemplate='Slot: %{customdata:,}<br>Zero-Bytes: %{y:.2f} MB<extra></extra>',

    )])
    figure5.add_trace(go.Scatter(
        x=days,
        y=[3*128/1024]*len(days),
        mode='lines',
        line=dict(color='red', dash='longdash', width=2),
        hovertemplate='Blob Target: %{y:.2f} MB<extra></extra>',
        name='Blob Target'
    ))
    figure5.update_layout(
        title=None,
        xaxis_title="Time",
        yaxis_title="MB",
        margin={"t": 0, "b": 0, "r": 50, "l": 50},
        plot_bgcolor="#0a0a0a",
        paper_bgcolor="#0a0a0a",
        font=dict(
            color="white",
            size=16-_font_size_delta
        ),
        legend=dict(
            yanchor="top",
            y=1,
            xanchor="left",
            x=0.91,
            bgcolor='rgba(10, 10, 10, 0)',
            font=dict(
                color="white",
                size=16-_font_size_delta
            ),
        ),
        dragmode=False,
        hovermode="x unified",
        xaxis=dict(
            fixedrange=True,
            gridcolor="rgba(255, 255, 255, 0.5)"
        ),
        yaxis=dict(
            fixedrange=True,
            gridcolor="rgba(255, 255, 255, 0.5)"
        ),
    )
    if len(blobs_to_show) > 0:
        figure6.add_trace(go.Scatter(
            x=days,
            y=blobs_to_show["blob_gas_price"].tolist(),
            mode='lines',
            line=dict(color='red', dash='longdash', width=2),
            hovertemplate='Blob Gas Price: %{y:.2f} gwei<extra></extra>',
            name='Blob Target'
        ))
        figure6.update_layout(
            title=None,
            xaxis_title="Time",
            yaxis_title="Gwei",
            margin={"t": 0, "b": 0, "r": 50, "l": 50},
            plot_bgcolor="#0a0a0a",
            paper_bgcolor="#0a0a0a",
            font=dict(
                color="white",
                size=16-_font_size_delta
            ),
            legend=dict(
                yanchor="top",
                y=1,
                xanchor="left",
                x=0.91,
                bgcolor='rgba(10, 10, 10, 0)',
                font=dict(
                    color="white",
                    size=16-_font_size_delta
                ),
            ),
            dragmode=False,
            hovermode="x unified",
            xaxis=dict(
                fixedrange=True,
                gridcolor="rgba(255, 255, 255, 0.5)"
            ),
            yaxis=dict(
                fixedrange=True,
                gridcolor="rgba(255, 255, 255, 0.5)"
            ),
        )
    else:
        figure6 = go.Figure()
        figure6.update_layout(
            plot_bgcolor="#0a0a0a",
            paper_bgcolor="#0a0a0a"
        ),
        xaxis=dict(
                fixedrange=True,
                showgrid=False
            ),
        yaxis=dict(
                fixedrange=True,
                showgrid=False
            ),
        width=1,
        height=1
        
    
    
    
    return (
        figure, 
        figure2, 
        figure3, 
        figure4, 
        figure5, 
        figure6, 
        figure_blobs, 
        stored_data, 
        stored_data2, 
        html.H6(timezone_text, style={'color': '#ffffff', "text-align": 'right'}), 
        last_updated_new
    )


@app.callback(
    [
        Output('historic-data-content', 'children'),
        Output('rollup-data-content', 'children'),
        Output('calldata-data-content', 'children'),
        Output('blob-data-content', 'children'),
        Output('loadingspinner', 'children'),
        Output('loadingspinner2', 'children'),
        Output('loadingspinner3', 'children'),
        Output('loadingspinner1', 'children')
    ], [   
        Input('tabs', 'value')
    ]
)
def update_tab_content(selected_tab):
    if selected_tab == 'tab-2':
        return generate_historic_data_content(), [], [], [], [], [], [], []
    if selected_tab == 'tab-3':
        return [], generate_rollup_data_content(), [], [], [], [], [], []
    if selected_tab == 'tab-4':
        return [], [], generate_calldata_data_content(), [], [], [], [], []
    if selected_tab == 'tab-blob':
        return [], [], [], generate_blob_data_content(), [], [], [], []
    return [], [], [], [], spinner, spinner2, spinner3, spinner1


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)