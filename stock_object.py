from prophet.forecaster import Prophet
import yfinance as yf
import datetime
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from typing import Optional, Any, Dict, Tuple
from sklearn.metrics import mean_absolute_percentage_error
class Stock:
    """
    This class enables data loading, plotting and statistical analysis of a given stock
    """
    def __init__(self,symbol='GOOG',column='Close'):
        """
        create a stock object , initialize time window and loads data.
        """
        self.end=datetime.datetime.today()
        self.start=self.end-datetime.timedelta(days=4)
        self.column=column
        self.symbol=symbol
        self.data=self.load_data(self.start,self.end,column)

    @st.cache
    def load_data(self,start,end,inplace=False):
        """
        takes a start and end dates, download data do some processing and returns dataframe
        """

        data=yf.download(self.symbol,start,end+datetime.timedelta(days=1))
        try:
            assert(len(data)>0)
        except AssertionError:
            print('Cannot fetch data, check spelling or time window')
        data.reset_index(inplace=True)
        data.rename(columns={'Date':'datetime'},inplace=True)
        data['date']=data.apply(lambda raw: raw['datetime'].date(),axis=1)
        
        data=data[['date',self.column]]
        if inplace:
            self.data=data 
            self.start=start
            self.end=end
            return True
        return data   


    def plot_raw_data(self,fig):
        fig=fig.add_trace(
        go.Scatter(
        x=self.data.date,
        y=self.data[self.column],
        mode="lines",
        name=self.symbol
            )
        )
        return fig

    def show_delta(self):
        epsilon=1e-6
        i=self.start
        j=self.end
        s=self.data.query('date==@i')[self.column].values[0]
        e=self.data.query('date==@j')[self.column].values[0]
        difference=round(e-s,2)
        change=round(difference/(s+epsilon)*100,2)
        e=round(e,2)
        cols=st.columns(2)
        (color,marker)=('green','+') if difference>=0 else ('red','-')

        cols[0].markdown(f"""<p style="font-size: 100%;margin-left:10px">{self.symbol} \t {e}</p>""",unsafe_allow_html=True)
        cols[1].markdown(f"""<p style="color:{color};font-size:100%;margin-right:10px">{marker} \t {difference} {marker} {change}</p>""",unsafe_allow_html=True)
    
    @staticmethod    
    def nearest_business_day(DATE:datetime.date):
        """
        Takes a date and transform it to the nearest business day
        """
        if DATE.weekday() ==5:
            DATE=DATE-datetime.timedelta(days=1)

        if DATE.weekday()==6:
            DATE=DATE+datetime.timedelta(days=1)
        return DATE


    

    @staticmethod
    def for_prophet(df:pd.DataFrame,date_column='date',y_column='Close')-> pd.DataFrame:
        return df.rename(columns={date_column:'ds',y_column:'y'})

    @st.cache
    def load_train_test_data(self,TEST_INTERVAL_LENGTH,TRAIN_INTERVAL_LENGTH):
        """Returns two dataframes for testing and training"""
        TODAY= Stock.nearest_business_day(datetime.date.today())
        TEST_END=Stock.nearest_business_day(TODAY)
        TEST_START=Stock.nearest_business_day(TEST_END-datetime.timedelta(days=TEST_INTERVAL_LENGTH))

        TRAIN_END=Stock.nearest_business_day(TEST_START-datetime.timedelta(days=1))
        TRAIN_START=Stock.nearest_business_day(TRAIN_END-datetime.timedelta(days=TRAIN_INTERVAL_LENGTH))

        train_data=self.load_data(TRAIN_START,TRAIN_END)
        test_data=self.load_data(TEST_START,TEST_END)

        train_data=Stock.for_prophet(train_data)
        test_data=Stock.for_prophet(test_data)
        self.train_data=train_data 
        self.test_data=test_data

    @st.cache(suppress_st_warning=True)
    def train_prophet(self,kwargs={}):
        m=Prophet(**kwargs)
        m.fit(self.train_data)
        self.model=m
        forecasts=m.predict(self.test_data)
        self.test_data=self.test_data.join(forecasts[['yhat_lower','yhat','yhat_upper']])
        self.test_mape=mean_absolute_percentage_error(self.test_data['y'],self.test_data['yhat'])

    def plot_test(self,chart_width):
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=self.test_data['ds'],
                y=self.test_data['y'], 
                mode='lines',
                name='True Closing price'
            )
        )

        fig.add_trace(
            go.Scatter(
                x=self.test_data['ds'], 
                y=self.test_data['yhat'], 
                mode='lines', 
                name='Predicted CLosing price'
            )
        )

        fig.add_trace(
            go.Scatter(
                x=self.test_data['ds'], 
                y=self.test_data['yhat_upper'], 
                fill=None,
                mode='lines', 
                name='CI+', 
                line_color='orange'
            )
        )

        fig.add_trace(
            go.Scatter(
                x=self.test_data['ds'], 
                y=self.test_data['yhat_lower'], 
                fill='tonexty',
                mode='lines', 
                line_color='orange',
                name='CI-'
            )
        )
        fig.update_layout(width=chart_width,
                        margin=dict(l=0, r=0, t=0, b=0,pad=0),
                        legend=dict(
                                x=0,
                                y=0.99,
                                traceorder='normal',
                                font=dict(
                                    size=12),
                            ),
                        autosize=False,
                        template='plotly_dark')
        
        return fig

    @staticmethod 
    def train_forecast_report(chart_width,symb,TRAIN_INTERVAL_LENGTH,TEST_INTERVAL_LENGTH):
        stock=Stock(symb)
        stock.load_train_test_data(TEST_INTERVAL_LENGTH,TRAIN_INTERVAL_LENGTH)
        stock.train_prophet()
        fig=stock.plot_test(chart_width)
        st.markdown(f'## {symb} stock forecasts on testing set, Testing error {round(stock.test_mape*100,2)}%')
        st.plotly_chart(fig)
        


