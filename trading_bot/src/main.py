import sys
import os
import time
import argparse
import yaml
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logger import setup_logging
from src.exchange import ExchangeInterface
from src.data_loader import DataManager
from src.strategy import SmaRsiStrategy
from src.risk_manager import RiskManager
from src.order_manager import OrderManager

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_secrets(secrets_path):
    try:
        with open(secrets_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("Secrets file not found. Creating empty one.")
        return {}

def main():
    parser = argparse.ArgumentParser(description='Professional Trading Bot')
    parser.add_argument('--config', default='config/config.yaml', help='Path to config file')
    parser.add_argument('--secrets', default='config/secrets.yaml', help='Path to secrets file')
    args = parser.parse_args()

    # Load Configuration
    config = load_config(args.config)
    secrets = load_secrets(args.secrets)

    # Setup Logging
    logger = setup_logging(config)
    logger.info("Starting Trading Bot...")

    # Initialize Modules
    try:
        exchange = ExchangeInterface(config, logger)
        exchange.authenticate(secrets.get('api_key'), secrets.get('secret'), secrets.get('password'))
        
        data_manager = DataManager(exchange, logger, config)
        strategy = SmaRsiStrategy(config, logger)
        risk_manager = RiskManager(config, logger)
        order_manager = OrderManager(exchange, logger)
        
        # Initial Check
        balance_info = exchange.get_balance()
        if balance_info:
            # Assuming USDT or generic 'total' balance for simplicity
            # Adjust based on exchange response structure
            total_balance = balance_info.get('total', {}).get('USDT', 10000) # Fallback to 10k if can't parse or paper trading
            risk_manager.set_account_balance(total_balance)
            logger.info(f"Initial Account Balance: {total_balance}")
        
        # Main Loop
        logger.info("Entering Main Loop...")
        while True:
            try:
                # 1. Fetch Data
                df = data_manager.get_historical_data(limit=strategy.sma_long_period + 10)
                
                # 2. Analyze Strategy
                signal = strategy.generate_signal(df)
                
                if signal:
                    logger.info(f"Signal Generated: {signal['action']} @ {signal['price']} ({signal['comment']})")
                    
                    # 3. Risk Check
                    current_balance = risk_manager.initial_account_balance # Ideally update this fetch
                    if risk_manager.check_system_health(current_balance):
                        position_size = risk_manager.calculate_position_size(current_balance, signal['price'])
                        
                        if position_size > 0:
                            if config['system'].get('dry_run', True):
                                logger.info(f"[DRY RUN] Would execute: {signal['action']} {position_size} @ {signal['price']}")
                            else:
                                order_manager.execute_order(signal, position_size, risk_manager)
                        else:
                            logger.warning("Calculated position size is 0. Check risk parameters.")
                
                # Sleep for timeframe (simplified)
                # In production, sleep until next candle close
                logger.debug("Waiting for next cycle...")
                time.sleep(60) # check every minute

            except KeyboardInterrupt:
                logger.info("Shutdown signal received.")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(10) # Backoff

    except Exception as e:
        logger.critical(f"Fatal Error during initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
