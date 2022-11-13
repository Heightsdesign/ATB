from live import live_data_processing as ldp
from strategies import Strategy


def main():
    """
    strategy parameters in order :

    ticker, period, interval,
    rsi_length, rsi_high, rsi_low,
    macd_fast, macd_slow,
    ema_offset,
    trend_line_window(number of candles to consider),
    trend_lever(Change accordingly to average ticker shift)

    """
    strategy = Strategy("EURUSD=X", "5d", "5m",
                        14, 65, 35,
                        9, 26,
                        200,
                        200, 100)

    ldp(strategy.create_strategy_df())

if __name__ == "__main__":
    main()
