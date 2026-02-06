import ccxt
import pandas as pd
import time
from datetime import datetime

class ExchangeInterface:
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config
        exchange_id = config['exchange']['name']
        self.symbol = config['exchange']['symbol']
        self.timeframe = config['exchange']['timeframe']
        self.sandbox = config['exchange'].get('sandbox', False)
        
        # Initialize CCXT exchange
        if not hasattr(ccxt, exchange_id):
            raise ValueError(f"Exchange {exchange_id} not supported by CCXT")
            
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
            'options': config['exchange'].get('options', {})
        })
        
        if self.sandbox:
            self.exchange.set_sandbox_mode(True)
            self.logger.warning("Running in SANDBOX mode (Testnet)")

    def authenticate(self, api_key, secret, password=None):
        if api_key and secret:
            self.exchange.apiKey = api_key
            self.exchange.secret = secret
            if password:
                self.exchange.password = password
            self.logger.info(f"Authenticated with {self.exchange.id}")
        else:
            self.logger.warning("No API keys provided. Running in public mode (Data only).")

    def fetch_ohlcv(self, limit=100):
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            self.logger.error(f"Error fetching OHLCV: {e}")
            return pd.DataFrame()

    def get_balance(self):
        try:
            balance = self.exchange.fetch_balance()
            return balance
        except Exception as e:
            self.logger.error(f"Error fetching balance: {e}")
            return None

    def create_order(self, type, side, amount, price=None):
        try:
            # Check for dry run logic in main loop, but here we execute real orders
            if type == 'limit':
                order = self.exchange.create_order(self.symbol, type, side, amount, price)
            else:
                order = self.exchange.create_order(self.symbol, type, side, amount)
            self.logger.info(f"Order created: {order['id']} - {side} {amount} @ {price if price else 'Market'}")
            return order
        except Exception as e:
            self.logger.error(f"Error creating order: {e}")
            return None
