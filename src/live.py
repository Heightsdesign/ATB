import time


def live_data_processing(strategy_df, launch=True):

    start_time = time.time()
    buy_signal = False
    sell_signal = False


    while launch:

        df = strategy_df
        last_row = df.iloc[-1]
        last_close = last_row['Close']
        last_rsi_hi = last_row['RSI_14_A_65']
        last_rsi_lo = last_row['RSI_14_B_35']
        last_rsi = last_row['RSI_14']
        last_macd = last_row['MACD_9_26_9']
        last_macdh = last_row['MACDh_9_26_9']
        last_macds = last_row['MACDs_9_26_9']
        last_ema = last_row['EMA_200']

        if last_rsi_lo == 1 and df.iloc[-2]['RSI_14_B_35'] == 0:
            if last_macd > last_macds and last_macd < 0:
                if last_ema > last_close:
                    buy_signal == True
                    print(f"Buying conditions met : {last_row}")

        elif last_rsi_hi == 1 and df.iloc[-2]['RSI_14_A_65'] == 0:
            if last_macd < last_macds and last_macd > 0:
                if last_ema < last_close:
                    sell_signal == True
                    print(f"Selling conditions met : {last_row}")

        else:
            print(f"No conditions met : \n {last_row}")

        time.sleep(60.0 - ((time.time() - start_time) % 60.0))
