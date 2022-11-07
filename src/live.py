import time
from res_sup_finder import ResSupFinder as rsf


def live_data_processing(strategy, strategy_df, launch=True):

    start_time = time.time()
    buy_signal = False
    sell_signal = False
    macd_conc = f"{strategy.macd_fast}_{strategy.macd_slow}_{strategy.macd_fast}"

    while launch:

        df = strategy_df
        last_row = df.iloc[-1]
        last_close = last_row['Close']
        last_rsi_hi = last_row['RSI_14_A_' + str(strategy.xa)]
        last_rsi_lo = last_row['RSI_14_B_' + str(strategy.xb)]
        last_rsi = last_row['RSI_' + str(strategy.rsi_length)]
        last_macd = last_row['MACD_' + macd_conc]
        last_macdh = last_row['MACDh_' + macd_conc]
        last_macds = last_row['MACDs_' + macd_conc]
        last_ema = last_row['EMA_' + str(strategy.ema_length)]

        if last_rsi_lo == 1 and df.iloc[-2]['RSI_14_B_' + str(strategy.xb)] == 0:
            if last_macds < last_macd < 0:
                if last_ema > last_close and strategy.get_trend_line_angle() > 20:
                    buy_signal = True
                    sl = rsf(df, 4, 3, 0).find_closest(last_close)
                    tp = last_close + (last_close - sl) * 2
                    print(f"Buying conditions met : {last_row}")

        elif last_rsi_hi == 1 and df.iloc[-2]['RSI_14_A_' + str(strategy.xa)] == 0:
            if last_macds > last_macd > 0:
                if last_ema < last_close and strategy.get_trend_line_angle() < -20:
                    sell_signal = True
                    sl = rsf(df, 4, 3, 1).find_closest(last_close)
                    tp = last_close - (last_close - sl) * 2
                    print(f"Selling conditions met : {last_row}")

        else:
            print(f"No conditions met : \n {last_row}")

        time.sleep(60.0 - ((time.time() - start_time) % 60.0))
