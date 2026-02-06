import pandas as pd
import os
import time

class DataManager:
    def __init__(self, exchange, logger, config):
        self.exchange = exchange
        self.logger = logger
        self.data_dir = config['system'].get('data_dir', 'data')
        self.symbol = config['exchange']['symbol']
        self.timeframe = config['exchange']['timeframe']
        
        # Ensure data directory exists
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def get_historical_data(self, limit=500):
        """
        Fetches historical data from exchange or loads from CSV if recent enough (caching logic can be added here).
        For now, we fetch fresh data to ensure latest candles.
        """
        self.logger.info(f"Fetching {limit} candles for {self.symbol} {self.timeframe}...")
        df = self.exchange.fetch_ohlcv(limit=limit)
        
        if not df.empty:
            self.save_data(df)
        
        return df

    def save_data(self, df):
        """Saves data to CSV for backtesting analysis"""
        sanitized_symbol = self.symbol.replace('/', '_')
        filename = f"{sanitized_symbol}_{self.timeframe}.csv"
        path = os.path.join(self.data_dir, filename)
        df.to_csv(path, index=False)
        # self.logger.debug(f"Saved data to {path}")

    def update_data(self, existing_df):
        """
        Fetches the latest candle and appends it to the dataframe.
        """
        # In a real scenario, this would be more complex (handling overlaps, etc.)
        # For simplicity, we just fetch the last 2 candles to ensure we get the closed one
        new_data = self.exchange.fetch_ohlcv(limit=2)
        if new_data.empty:
            return existing_df
            
        # Concatenate and drop duplicates based on timestamp
        updated_df = pd.concat([existing_df, new_data]).drop_duplicates(subset='timestamp', keep='last').reset_index(drop=True)
        return updated_df
