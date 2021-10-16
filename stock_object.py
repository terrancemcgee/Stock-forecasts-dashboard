import yfinance as yf
import datetime
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
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

        cols[0].markdown(f"""<p style="font-size: 100%;margin-left:10px">{self.symbol} {e}</p>""",unsafe_allow_html=True)
        cols[1].markdown(f"""<p style="color:{color};font-size:100%;margin-right:10px">{marker} {difference} {marker} {change}</p>""",unsafe_allow_html=True)
    

    
