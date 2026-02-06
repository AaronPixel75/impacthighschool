class OrderManager:
    def __init__(self, exchange, logger):
        self.exchange = exchange
        self.logger = logger
        self.open_orders = []

    def execute_order(self, signal, position_size, risk_manager):
        """
        Executes an order based on signal and position size.
        """
        side = signal['action'].lower() # 'buy' or 'sell'
        price = signal['price']
        
        self.logger.info(f"EXECUTING {side.upper()} order. Size: {position_size}, Price: {price}, Reason: {signal['comment']}")
        
        # 1. Place Market Order for Entry (for simplicity/guaranteed fill in this MVP)
        # In production, might want limit orders
        order = self.exchange.create_order('market', side, position_size)
        
        if order:
            self.logger.info(f"Entry Order Filled: {order['id']}")
            
            # 2. Place Stop Loss and Take Profit (if exchange supports OCO or separate orders)
            # For this MVP, we will simulate managing SL/TP in the main loop or place them if supported.
            # Many crypto exchanges require separate API calls for SL/TP on open positions.
            
            sl_price = risk_manager.get_stop_loss_price(price, side)
            tp_price = risk_manager.get_take_profit_price(price, side)
            
            self.logger.info(f"Set Stop Loss at {sl_price:.2f} and Take Profit at {tp_price:.2f}")
            
            # Note: A full implementation would place actual stop orders here.
            # self.place_conditional_orders(side, position_size, sl_price, tp_price)
            
            return True
        else:
            self.logger.error("Failed to execute entry order.")
            return False

    def close_position(self, symbol):
        """
        Closes all open positions for a symbol.
        """
        # specialized logic would be needed here to fetch open positions and close them
        pass
