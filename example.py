import streamlit as st
import pandas as pd
import numpy as np

st.title("Uber pickups in NYC")

DATE_COLUMN = "date/time"
key = "6a3b16cf358e1b21ed1ce04e12c415f7e1184dca"  # TODO : Put this in a text file and read it


interval = ""
DATA_URL = (
    "https://s3-us-west-2.amazonaws.com/"
    "streamlit-demo-data/uber-raw-data-sep14.csv.gz"
)


def load_data(inerval, asset):  # TODO: use cache
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data
