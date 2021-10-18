import optuna 
import pandas 
import prophet

import plotly.express as px 
import plotly.graph_objects as go 

from stock_object import Stock

if __name__ == '__main__':
    stock=Stock('TSLA')
    stock.load_data()
    