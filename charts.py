import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
matplotlib.use('Agg')
import pandas as pd
import io
import base64
import kpi_calcs



from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from io import BytesIO


def generate_charts(ohlc_dict, ticker_signal, short, long, ind, ticker_strat, strat_returns, buys, sells):
    try:
        # Calculating long-only strategy KPIs with signal
        strategy_df = pd.DataFrame()
        strategy_df["Returns"] = strat_returns["Returns"]
        strategy_df["Returns"] = strategy_df.mean(axis=1)
        strategy_df["cum_return"] = (1 + strategy_df["Returns"]).cumprod()
        strategy_df['Position'] = strat_returns['Position']

        # Calculating long-only strategy KPIs without signal
        strategy_df_2 = pd.DataFrame()
        strategy_df_2["Returns_T"] = strat_returns["All Returns"]
        strategy_df_2["Returns_T"] = strategy_df_2.mean(axis=1)
        strategy_df_2["Position"] = strategy_df["Position"]
        idx = strategy_df_2["Position"].eq(1).idxmax()
        strategy_df_2.loc[idx:, "Position"] = 1
        strategy_df_2["Returns"] = strategy_df_2["Returns_T"] * strategy_df_2["Position"]
        strategy_df_2["cum_return"] = (1 + strategy_df_2["Returns"]).cumprod()

        fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(10, 10))
        ax[0].set_title('Crossover signal: {a} {b}/{c} {d} '.format(a=ticker_signal, b=short, c=long, d=ind))
        ax[1].set_title('Cumulative return')
        ax[0].grid()
        ax[1].grid()

        # Chart 1
        ax[0].plot(ohlc_dict[ticker_signal]['Adj Close'], color='black', label='Adj Close')
        ax[0].plot(ohlc_dict[ticker_signal]['Short {}'.format(ind)], color='black', label='Short {}'.format(ind))
        ax[0].plot(ohlc_dict[ticker_signal]['Long {}'.format(ind)], color='g', label='Long {}'.format(ind))
        ax[0].plot_date(buys, ohlc_dict[ticker_signal]['Short {}'.format(ind)][ohlc_dict[ticker_signal]['Position'] == 1], \
                        '^', markersize=5, color='g', label='buy')
        ax[0].plot_date(sells, ohlc_dict[ticker_signal]['Short {}'.format(ind)][ohlc_dict[ticker_signal]['Position'] == -1], \
                        'v', markersize=5, color='r', label='sell')
        ax[0].legend()

        # Chart 2
        ax[1].plot(strategy_df["cum_return"], color="green", label="Strategy w/ signal")
        ax[1].plot(strategy_df_2["cum_return"], color="blue", label="Strategy w/o signal")
        ax[1].legend()
        ax[1].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png',bbox_inches='tight')
        img_buffer.seek(0)

        # Create a base64 encoded image string
        img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        print("charts.py: created base64 encoded image string")
        # Return the image string
        return img_str


    except Exception as e:
        print("Error generating chart in charts.py")
        return None
