import logging
from datetime import timedelta

import ta
from lumibot.strategies.strategy import Strategy


class STATES:
    UPPER = "UPPER"
    LOWER = "LOWER"
    MIDDLE = "MIDDLE"


class BollingerRSI(Strategy):
    

    def initialize(self, 
                    buy_symbol="SPY",
                    lower_threshold=30,
                    upper_threshold=70,
                    higher_bollinger = 2,
                    lower_bollinger = 3,
    ):
        # There is only one trading operation per day
        # No need to sleep between iterations
        self.sleeptime = 1
        self.buy_symbol = buy_symbol
        self.current_state = None
        self.higher_bollinger = higher_bollinger 
        self.lower_bollinger = lower_bollinger
        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold

    def on_trading_iteration(self):
        symbol = self.buy_symbol
        current_rsi = self.get_rsi(symbol)
        current_bolliner = self.get_bollinger(symbol)
        hbb = current_bolliner[0]
        lbb = current_bolliner[1]
        abb = current_bolliner[2]
        current_position = self.get_tracked_position(symbol)
        current_price = self.get_last_price(self.buy_symbol)

        ## Write your code here
        if current_rsi < self.lower_threshold and self.current_state != STATES.LOWER and lbb > current_price:
  
            quantity = self.portfolio_value // current_price
            order = self.create_order(self.buy_symbol, quantity, "buy")
            self.submit_order(order)
            

        elif current_rsi > self.upper_threshold and self.current_state != STATES.UPPER and hbb < current_price:
            my_trail_percent = 5.0 # set trainling stop loss
            selling_order = self.create_order(symbol, quantity, side, trail_percent=my_trail_percent)
            self.submit_order(selling_order)
            

        # Buy a mix of main and other symbol in the proportion determined
        # by self.middle_main_symbol_percentage
        # elif self.current_state != STATES.MIDDLE:
        # self.sell_all()
        
        # Wait untill the end of the day
        self.await_market_to_close()

    def on_abrupt_closing(self):
        # Sell all positions when you hit ctrl + C
        self.sell_all()

    def trace_stats(self, context, snapshot_before):
        row = {
            "quantity": context.get("quantity", 0),
            "price": context.get("current_price", 0),
            "current_rsi": context.get("current_rsi"),
            "current_state": self.current_state,
        }

        return row

    def get_rsi(self, symbol, period=20):
        # code execution for 10 years takes around 37.23s
        bars_set = self.get_symbol_bars(symbol, period, "day")
        rsi = ta.momentum.rsi(bars_set.df["close"])[-1]
        return rsi

    def get_bollinger(self,symbol,period = 20):
        bars_set = self.get_symbol_bars(symbol, period, "day")
        hbb=ta.volatility.BollingerBands(bars_set.df["close"],window = period, window_dev=self.higher_bollinger).bollinger_hband().round(2)[-1]
        lbb=ta.volatility.BollingerBands(bars_set.df["close"],window = period, window_dev=self.lower_bollinger).bollinger_lband().round(2)[-1]
        abb=ta.volatility.BollingerBands(bars_set.df["close"],window = period).bollinger_mavg().round(2)[-1]
        return hbb,lbb,abb


    