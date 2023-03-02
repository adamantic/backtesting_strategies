from flask import Flask, render_template, request, session
from flask_bootstrap import Bootstrap
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import os

import warnings
warnings.filterwarnings("ignore")

# Import the Hedge v5 trading strategy script
from hedge_functions import CAGR, total_return_multiple, volatility, sharpe, max_dd
from charts import generate_charts
from sma_ema import add_sma_ema_signals
from data_download import download_ticker_data
from kpi_calcs import calculate_kpis, KPIs

app = Flask(__name__, template_folder='templates',static_folder='templates')

# generate a secret key
secret_key = os.urandom(24)

# set the secret key in the Flask app
app.secret_key = secret_key

#call boostrap table for bootstrap table
bootstrap = Bootstrap(app)

# default values
default_symbol = 'QQQ'
default_short = 1
default_long = 200
default_ind = 'SMA'
default_start_years_ago = 20
default_end_years_ago = 0

@app.route('/')
def index():
    return render_template('index.html',
        symbol=session.get('symbol', default_symbol),
        short=session.get('short', default_short),
        long=session.get('long', default_long),
        ind=session.get('ind', default_ind),
        start_years_ago=session.get('start_years_ago', default_start_years_ago),
        end_years_ago=session.get('end_years_ago', default_end_years_ago),
        img_str = '',
        table_str = '')

@app.route('/generate_chart', methods=['POST'])
def generate_chart():

    # Get user input
    symbol = request.form.get('symbol', default_symbol)
    short = int(request.form.get('short', default_short))
    long = int(request.form.get('long', default_long))
    ind = request.form.get('ind', default_ind)
    start_years_ago = int(request.form.get('start_years_ago', default_start_years_ago))
    end_years_ago = int(request.form.get('end_years_ago', default_end_years_ago))

    ticker_signal = symbol
    ticker_strat = symbol

    # Define the tickers to download data for
    tickers = [symbol]

    # Download historical data for tickers
    ohlc_data = download_ticker_data(tickers, start_years_ago, end_years_ago)

    # Add SMA/EMA signals and buy/sell signals
    ohlc_dict = add_sma_ema_signals(ohlc_data, symbol, short, long, ind)

    print('Dictionary after SMA and EMA calc and buy/sell signal',ohlc_dict)

    # Calculate returns with long strategy and ticker signal
    df_temp = pd.concat(ohlc_dict, axis=1)
    strat_returns = df_temp.xs('Adj Close', axis=1, level=1)
    strat_returns['Position'] = df_temp.xs('Position', axis=1, level=1)
    strat_returns = strat_returns.copy()
    strat_returns['Signal'] = df_temp.xs('Signal', axis=1, level=1)
    strat_returns['Returns'] = 0

    for i in range(1, len(strat_returns)):
        if strat_returns['Signal'].iloc[i] == 1:
            strat_returns['Returns'].iloc[i] = (
                    (strat_returns[ticker_strat].iloc[i] / strat_returns[ticker_strat].iloc[i - 1]) - 1)
        else:
            strat_returns['Returns'].iloc[i] = 0

    strat_returns['All Returns'] = (strat_returns[ticker_strat].pct_change())

    # Call the calculate_kpis function to get the KPI data
    kpi_data = calculate_kpis(strat_returns)
    table_html = KPIs(kpi_data, classes=['table', 'table-striped']).__html__()

    buys = ohlc_dict[ticker_signal][ohlc_dict[ticker_signal]['Position'] == 1].index
    sells = ohlc_dict[ticker_signal][ohlc_dict[ticker_signal]['Position'] == -1].index

    img_str = generate_charts(ohlc_dict, ticker_signal, short, long, ind, ticker_strat, strat_returns, buys, sells)

    session['symbol'] = symbol
    session['short'] = short
    session['long'] = long
    session['ind'] = ind
    session['start_years_ago'] = start_years_ago
    session['end_years_ago'] = end_years_ago

    return render_template('index.html', table_html=table_html, img_str=img_str, symbol=symbol, short=short, long=long, ind=ind, start_years_ago=start_years_ago, end_years_ago=end_years_ago)


if __name__ == '__main__':
    # Get the port number from the environment variable, or use 5000 as a fallback
    port = int(os.environ.get('PORT', 5000))
    # Run the app on the specified port
    app.run(host='0.0.0.0', port=port)