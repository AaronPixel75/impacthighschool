import pandas as pd
import numpy as np
try:
    import talib
except ImportError:
    print("TA-Lib not found. Please install it or use a different library.")
    talib = None

class Strategy:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.params = config['strategy'].get('params', {})

    def generate_signal(self, df):
        """
        Analyzes the dataframe and returns a signal.
        Returns:
            dict: {'action': 'BUY'/'SELL', 'price': float, 'comment': str} or None
        """
        raise NotImplementedError("Strategy must implement generate_signal method")

class SmaRsiStrategy(Strategy):
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.sma_short_period = self.params.get('sma_short', 50)
        self.sma_long_period = self.params.get('sma_long', 200)
        self.rsi_period = self.params.get('rsi_period', 14)
        self.rsi_buy = self.params.get('rsi_buy_threshold', 30)
        self.rsi_sell = self.params.get('rsi_sell_threshold', 70)

    def generate_signal(self, df):
        if df.empty or len(df) < self.sma_long_period:
            return None

        # Calculate Indicators
        # Using TA-Lib
        if talib:
            close_prices = df['close'].values
            sma_short = talib.SMA(close_prices, timeperiod=self.sma_short_period)
            sma_long = talib.SMA(close_prices, timeperiod=self.sma_long_period)
            rsi = talib.RSI(close_prices, timeperiod=self.rsi_period)
        else:
            # Fallback (simple pandas calculation if talib fails)
            self.logger.warning("TA-Lib missing, using pandas simple calculation")
            close_series = df['close']
            sma_short = close_series.rolling(window=self.sma_short_period).mean().values
            sma_long = close_series.rolling(window=self.sma_long_period).mean().values
            # Simple RSI approx not implemented for brevity in fallback, returning None
            return None

        # Get latest values
        current_price = df['close'].iloc[-1]
        last_sma_short = sma_short[-1]
        last_sma_long = sma_long[-1]
        last_rsi = rsi[-1]
        
        prev_sma_short = sma_short[-2]
        prev_sma_long = sma_long[-2]

        # Logic: Golden Cross (Short crosses above Long) + RSI < Overbought
        # This is a basic trend following entry
        signal = None
        
        # BUY SIGNAL: Golden Cross AND RSI is not overbought (room to grow)
        # OR: Mean Reversion buy (RSI < 30)
        
        # Example Logic: Buy if SMA 50 > SMA 200 AND RSI < 70 (Trend is up, not overextended)
        is_uptrend = last_sma_short > last_sma_long
        
        # Crossover check (did it just happen?)
        crossover_bullish = (prev_sma_short <= prev_sma_long) and (last_sma_short > last_sma_long)
        crossover_bearish = (prev_sma_short >= prev_sma_long) and (last_sma_short < last_sma_long)
        
        if crossover_bullish:
             signal = {'action': 'BUY', 'price': current_price, 'comment': 'Golden Cross'}
        
        elif last_rsi < self.rsi_buy and is_uptrend:
             signal = {'action': 'BUY', 'price': current_price, 'comment': 'RSI Oversold in Uptrend'}

        # SELL SIGNAL: Death Cross OR RSI Overbought
        elif crossover_bearish:
             signal = {'action': 'SELL', 'price': current_price, 'comment': 'Death Cross'}
        
        elif last_rsi > self.rsi_sell:
             signal = {'action': 'SELL', 'price': current_price, 'comment': 'RSI Overbought'}

        return signal
