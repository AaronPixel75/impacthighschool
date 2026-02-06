import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.risk_manager import RiskManager

class MockLogger:
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass
    def critical(self, msg): pass

class TestRiskManager(unittest.TestCase):
    def setUp(self):
        self.config = {
            'risk': {
                'risk_per_trade_pct': 1.0,
                'max_drawdown_pct': 10.0,
                'stop_loss_pct': 2.0,
                'take_profit_pct': 4.0
            }
        }
        self.logger = MockLogger()
        self.risk_manager = RiskManager(self.config, self.logger)
        self.risk_manager.set_account_balance(10000)

    def test_calculate_position_size(self):
        # Account: 10000, Risk: 1% ($100)
        # Entry: 50000
        # Stop Loss: 2% (Distance = 1000)
        # Position Size = 100 / 1000 = 0.1 BTC
        
        entry_price = 50000
        size = self.risk_manager.calculate_position_size(10000, entry_price)
        self.assertAlmostEqual(size, 0.1)

    def test_check_system_health(self):
        # Drawdown limit 10% (Balance < 9000)
        self.assertTrue(self.risk_manager.check_system_health(9500))
        self.assertFalse(self.risk_manager.check_system_health(8900))

    def test_stop_loss_price(self):
        entry = 100
        sl_buy = self.risk_manager.get_stop_loss_price(entry, 'buy')
        self.assertEqual(sl_buy, 98.0)
        
        sl_sell = self.risk_manager.get_stop_loss_price(entry, 'sell')
        self.assertEqual(sl_sell, 102.0)

if __name__ == '__main__':
    unittest.main()
