import pandas as pd
import numpy as np
import yaml
import sys
import os
import argparse
import matplotlib.pyplot as plt # Optional, but good for reporting

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logger import setup_logging
from src.strategy import SmaRsiStrategy
from src.risk_manager import RiskManager

class Backtester:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.strategy = SmaRsiStrategy(config, logger)
        self.risk_manager = RiskManager(config, logger)
        
        self.initial_balance = 10000
        self.balance = self.initial_balance
        self.positions = [] # list of dicts
        self.trades = [] # list of completed trades
        self.equity_curve = []

    def run(self, data_file):
        self.logger.info(f"Starting Backtest on {data_file}")
        try:
            df = pd.read_csv(data_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        except Exception as e:
            self.logger.error(f"Could not read data file: {e}")
            return

        # Prepare Strategy Indicators (vectorized for speed if possible, but stepping for realism)
        # We will loop to simulate real-time decision making
        
        # Pre-calc indicators to save time in loop if strategy supports it
        # But for 'simulation' accuracy we iterate.
        # To speed up, we can calculate indicators on the whole DF first if the strategy is stateless.
        # Our strategy IS stateless (depends only on window), so we can pre-calc.
        
        # NOTE: For this implementation, I will just iterate loosely or use the strategy's generate_signal
        # on a rolling window. To be fast, let's pre-calculate indicators inside the strategy if optimized.
        # But our strategy takes a DF slice.
        
        total_candles = len(df)
        window_size = self.strategy.sma_long_period + 5
        
        for i in range(window_size, total_candles):
            current_slice = df.iloc[i-window_size:i+1] # Pass window
            current_candle = df.iloc[i]
            timestamp = current_candle['timestamp']
            price = current_candle['close']
            
            # Record Equity
            total_equity = self.balance + self.get_open_position_value(price)
            self.equity_curve.append({'timestamp': timestamp, 'equity': total_equity})
            
            # Check Stops on Open Positions
            self.check_exit_conditions(price, timestamp)
            
            # Generate Signal
            signal = self.strategy.generate_signal(current_slice)
            
            if signal and signal['action'] == 'BUY':
                # Entry Logic
                if len(self.positions) == 0: # Simple 1 position at a time
                    pos_size = self.risk_manager.calculate_position_size(self.balance, price)
                    if pos_size > 0:
                        self.open_position(price, pos_size, timestamp, signal['comment'])
            
            elif signal and signal['action'] == 'SELL':
                # Exit Logic if we have a LONG position
                self.close_all_positions(price, timestamp, signal['comment'])

        self.generate_report()

    def get_open_position_value(self, current_price):
        value = 0
        for pos in self.positions:
            value += pos['size'] * current_price
        return value

    def open_position(self, price, size, timestamp, comment):
        cost = price * size
        if cost > self.balance:
            return # Insufficient funds
            
        self.balance -= cost
        sl = self.risk_manager.get_stop_loss_price(price, 'buy')
        tp = self.risk_manager.get_take_profit_price(price, 'buy')
        
        self.positions.append({
            'entry_price': price,
            'size': size,
            'entry_time': timestamp,
            'sl': sl,
            'tp': tp,
            'comment': comment
        })
        # self.logger.info(f"BUY at {price} ({timestamp})")

    def check_exit_conditions(self, current_price, timestamp):
        # Check SL/TP
        for pos in list(self.positions): # Copy to modify
            if current_price <= pos['sl']:
                self.close_position(pos, current_price, timestamp, "Stop Loss")
            elif current_price >= pos['tp']:
                self.close_position(pos, current_price, timestamp, "Take Profit")

    def close_all_positions(self, price, timestamp, comment):
        for pos in list(self.positions):
            self.close_position(pos, price, timestamp, comment)

    def close_position(self, pos, price, timestamp, reason):
        # Execute Sell
        proceeds = pos['size'] * price
        self.balance += proceeds
        
        # Calculate PnL
        cost = pos['size'] * pos['entry_price']
        pnl = proceeds - cost
        pnl_pct = (pnl / cost) * 100
        
        self.trades.append({
            'entry_time': pos['entry_time'],
            'exit_time': timestamp,
            'entry_price': pos['entry_price'],
            'exit_price': price,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'reason': reason
        })
        
        self.positions.remove(pos)
        # self.logger.info(f"SELL at {price} ({reason}) PnL: {pnl:.2f}")

    def generate_report(self):
        self.logger.info("--------------------------------")
        self.logger.info("BACKTEST RESULTS")
        self.logger.info("--------------------------------")
        
        total_trades = len(self.trades)
        if total_trades == 0:
            self.logger.info("No trades executed.")
            return

        wins = [t for t in self.trades if t['pnl'] > 0]
        losses = [t for t in self.trades if t['pnl'] <= 0]
        win_rate = (len(wins) / total_trades) * 100
        
        total_pnl = sum(t['pnl'] for t in self.trades)
        final_equity = self.equity_curve[-1]['equity']
        roi = ((final_equity - self.initial_balance) / self.initial_balance) * 100
        
        self.logger.info(f"Total Trades: {total_trades}")
        self.logger.info(f"Win Rate: {win_rate:.2f}%")
        self.logger.info(f"Total PnL: ${total_pnl:.2f}")
        self.logger.info(f"Final Equity: ${final_equity:.2f}")
        self.logger.info(f"ROI: {roi:.2f}%")
        self.logger.info("--------------------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True, help='Path to CSV data file')
    parser.add_argument('--config', default='config/config.yaml')
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    logger = setup_logging(config)
    backtester = Backtester(config, logger)
    backtester.run(args.data)
