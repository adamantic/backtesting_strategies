import pandas as pd
import yfinance as yf
import pickle

def download_ticker_data(tickers, start_years_ago, end_years_ago):
    # Download historical data for tickers
    start = pd.Timestamp.today() - pd.DateOffset(years=start_years_ago)
    end = pd.Timestamp.today() - pd.DateOffset(years=end_years_ago)
    ohlc_data = {}

    try:
        # Try to download data from internet
        for ticker in tickers:
            ohlc_data[ticker] = yf.download(ticker, start, end)
            print('Data downloaded from yfinance for ticker: ',ticker)
        with open('ohlc_data.pickle', 'wb') as f:
            pickle.dump(ohlc_data, f)
            print('pickle dump succeeded')
    except Exception as e:
        print("Failed to download data from internet: {}".format(str(e)))
        # Try to load data from pickle file
        try:
            with open('ohlc_data.pickle', 'rb') as f:
                ohlc_data = pickle.load(f)
        except Exception as e:
            print("Failed to load data from pickle file: {}".format(str(e)))

    return ohlc_data