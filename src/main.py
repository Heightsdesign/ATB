from live import live_data_processing as ldp
from strategies import Strategy


def main():

    strategy = Strategy("EURUSD=X", "5d", "5m")
    ldp(strategy.create_strategy_df())

if __name__ == "__main__":
    main()
