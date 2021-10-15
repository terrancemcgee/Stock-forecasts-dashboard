from mimetypes import init
from os import terminal_size
from numpy.core.fromnumeric import std
import pandas as pd 
import streamlit as st 
from prophet import Prophet, forecaster
import datetime
from prophet.plot import plot_components, plot_plotly
from plotly import graph_objects as go
import plotly.express as px 
from streamlit.type_util import data_frame_to_bytes
import yfinance as yf
import numpy as np

st.set_page_config(layout='wide',initial_sidebar_state='expanded')

TODAY=datetime.date.today()
window_selection_c=st.sidebar.container()
sub_columns=window_selection_c.columns(2)
START=sub_columns[0].date_input('From',value=TODAY-datetime.timedelta(days=7),max_value=TODAY-datetime.timedelta(days=1))
END=sub_columns[1].date_input('To',value=TODAY,max_value=TODAY)



STOCKS=np.array(['AAPL','GOOG','MSFT','GME'])

selected_stocks=window_selection_c.multiselect('Select stocks ',STOCKS,default='GOOG')
    
def load_data(ticker,start,end):
    data=yf.download(ticker,start,end)
    data.reset_index(inplace=True)
    data.rename(columns={'Date':'datetime'},inplace=True)
    data['date']=data.apply(lambda raw: raw['datetime'].date(),axis=1)
    return data

def delta(data,start,end,column='Close'):
    epsilon=1e-6
    s=data.query('date==@start')[column].values[0]
    print(f'starting value is {s}')
    e=data.query('date==@end')[column].values[0]
    print(f'ending value is {e}')
    difference=round(e-s,2)
    change=round(difference/(s+epsilon)*100,2)
    e=round(e,2)
    return (difference, change, e)

selected_stock=selected_stocks[0]
data=load_data(selected_stock,START,END+datetime.timedelta(days=1))

columns=st.columns(2)
def plot_raw_data(context):
    fig=px.line(data,x='date',y='Close')
    fig.update_layout(
                autosize=False,
                width=1100,
                height=300)
    context.plotly_chart(fig)



plot_raw_data(st)

change_c=st.sidebar.container()
diff,change,e=delta(data,START,END)


show_percent=True
if not show_percent:
    change_c.metric(label=selected_stock[0],value=e,delta=diff)
else:
    change_c.metric(label=selected_stocks[0],value=e,delta=f'{change}%')


