from mimetypes import init
from os import terminal_size
from numpy.core.fromnumeric import std
import pandas as pd 
import streamlit as st 
from prophet import Prophet, forecaster
import datetime
from prophet.plot import plot, plot_components, plot_plotly
from plotly import graph_objects as go
import plotly.express as px 
from streamlit.type_util import data_frame_to_bytes
import yfinance as yf
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from stock_object import Stock

st.set_page_config(layout='wide',initial_sidebar_state='expanded')

#------ layout setting---------------------------
window_selection_c=st.sidebar.container()
sub_columns=window_selection_c.columns(2)

change_c=st.sidebar.container()

#----------Time window selection-----------------
TODAY=datetime.date.today()
START=sub_columns[0].date_input('From',value=TODAY-datetime.timedelta(days=700),max_value=TODAY-datetime.timedelta(days=1))
END=sub_columns[1].date_input('To',value=TODAY,max_value=TODAY)


#---------------stock selection------------------
STOCKS=np.array(['AAPL','GOOG','MSFT','GME']) #TODO : include all stocks

selected_stocks=window_selection_c.multiselect('Select stocks ',STOCKS,default='GOOG')



#------------------------Plot stock linecharts--------------------


fig =go.Figure()
for choice in selected_stocks:
    stock=Stock(symbol=choice)
    stock.load_data(START,END,inplace=True)
    fig=stock.plot_raw_data(fig)

    with change_c:
        stock.show_delta()

fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0,pad=0),
    width=1300,
    autosize=False,
    template='plotly_dark'
    
)


st.write(fig)


