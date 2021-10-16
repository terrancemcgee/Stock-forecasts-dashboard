from mimetypes import init
from numpy.core.fromnumeric import std
import pandas as pd 
import streamlit as st 
from prophet import Prophet, forecaster
import datetime
from prophet.plot import plot, plot_components, plot_plotly
from plotly import graph_objects as go
from streamlit.type_util import data_frame_to_bytes
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from stock_object import Stock

st.set_page_config(layout='wide',initial_sidebar_state='expanded')
st.markdown('# Train forecasting models for stock prices')
#------ layout setting---------------------------
window_selection_c=st.sidebar.container()
window_selection_c.markdown('## Watch list')

sub_columns=window_selection_c.columns(2)
change_c=st.sidebar.container()

#----------Time window selection-----------------
TODAY= Stock.nearest_business_day(datetime.date.today())
DEFAULT_START=Stock.nearest_business_day(TODAY-datetime.timedelta(days=700))



START=sub_columns[0].date_input('From',value=DEFAULT_START,max_value=TODAY-datetime.timedelta(days=1))
START=Stock.nearest_business_day(START)
END=sub_columns[1].date_input('To',value=TODAY,max_value=TODAY,min_value=START)
END=Stock.nearest_business_day(END)


#---------------stock selection------------------
STOCKS=np.array(['AAPL','GOOG','MSFT','GME','FB']) #TODO : include all stocks
selected_stocks=window_selection_c.multiselect('',STOCKS,default='GOOG')

chart_width=st.expander(label='chart width').slider('',1000,2800,1400)


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
    width=chart_width,
    autosize=False,
    template='plotly_dark'
    
)


st.write(fig)




#------------------------------------------Training configurations-------------------------------------
st.sidebar.markdown("## Forecasts")
form=st.sidebar.form(key='train_dataset')
SYMB=form.selectbox('select stock',STOCKS)
form.markdown('## Select interval lengths')
HORIZON=form.number_input('Inference horizon',value=7,min_value=7,max_value=200)
TEST_INTERVAL_LENGTH=form.number_input('number of days to test on and visualize',value=30,min_value=20)
TRAIN_INTERVAL_LENGTH=form.number_input('number of  day to use for training',value=300,min_value=100)
form.form_submit_button(label='Load and train',on_click=Stock.train_forecast_report(chart_width,SYMB,TRAIN_INTERVAL_LENGTH,TEST_INTERVAL_LENGTH))



