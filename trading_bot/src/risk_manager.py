class RiskManager:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.risk_per_trade_pct = config['risk']['risk_per_trade_pct'] / 100.0
        self.max_drawdown_pct = config['risk']['max_drawdown_pct'] / 100.0
        self.stop_loss_pct = config['risk']['stop_loss_pct'] / 100.0
        self.take_profit_pct = config['risk']['take_profit_pct'] / 100.0
        
        self.initial_account_balance = None # To be set on startup

    def set_account_balance(self, balance):
        if self.initial_account_balance is None:
            self.initial_account_balance = balance

    def check_system_health(self, current_balance):
        if self.initial_account_balance:
            drawdown = (self.initial_account_balance - current_balance) / self.initial_account_balance
            if drawdown >= self.max_drawdown_pct:
                self.logger.critical(f"MAX DRAWDOWN BREACHED: {drawdown*100:.2f}% >= {self.max_drawdown_pct*100:.2f}%. STOPPING TRADING.")
                return False
        return True

    def calculate_position_size(self, account_balance, entry_price):
        """
        Calculate position size based on risk amount.
        Risk Amount = Account Balance * Risk%
        Stop Loss Distance = Entry Price * StopLoss%
        Position Size = Risk Amount / Stop Loss Distance
        """
        risk_amount = account_balance * self.risk_per_trade_pct
        stop_loss_dist = entry_price * self.stop_loss_pct
        
        if stop_loss_dist == 0:
            return 0
            
        position_size = risk_amount / stop_loss_dist
        
        # Sanity check: cap position size at 95% of balance (no leverage assumed here for safety)
        max_position_value = account_balance * 0.95
        if (position_size * entry_price) > max_position_value:
             position_size = max_position_value / entry_price
             
        return position_size

    def get_stop_loss_price(self, entry_price, side):
        if side == 'buy':
            return entry_price * (1 - self.stop_loss_pct)
        else:
            return entry_price * (1 + self.stop_loss_pct)

    def get_take_profit_price(self, entry_price, side):
        if side == 'buy':
            return entry_price * (1 + self.take_profit_pct)
        else:
            return entry_price * (1 - self.take_profit_pct)
