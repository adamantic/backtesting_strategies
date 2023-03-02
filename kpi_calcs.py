import pandas as pd
import numpy as np
from hedge_functions import CAGR, total_return_multiple, volatility, sharpe, max_dd
from flask_table import Table, Col

class KPIs(Table):
    kpi = Col('KPI')
    long_only = Col('Long only with signal')
    long_only_no_signal = Col('Long only (no signal)')

def calculate_kpis(strat_returns):
    """
    Calculates the key performance indicators (KPIs) for a given set of strategy returns.

    Parameters:
    strat_returns (pandas DataFrame): DataFrame containing strategy returns.

    Returns:
    data (list): List of KPI data.
    """
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

    # Calculate KPI data
    data = [
        {'kpi': 'CAGR', 'long_only': '{:.1%}'.format(CAGR(strategy_df)),
         'long_only_no_signal': '{:.1%}'.format(CAGR(strategy_df_2))},
        {'kpi': 'Sharpe ratio', 'long_only': '{:.2f}'.format(sharpe(strategy_df, 0.025)),
         'long_only_no_signal': '{:.2f}'.format(sharpe(strategy_df_2, 0.025))},
        {'kpi': 'Max Drawdown', 'long_only': '{:.0%}'.format(max_dd(strategy_df)),
         'long_only_no_signal': '{:.0%}'.format(max_dd(strategy_df_2))},
        {'kpi': 'Total return multiple', 'long_only': "{:.1f}x".format(total_return_multiple(strategy_df)),
         'long_only_no_signal': "{:.1f}x".format(total_return_multiple(strategy_df_2))}
    ]

    return data
