import pandas as pd
import numpy as np
from strategy_base import BaseStrategy
from config import NASDAQ_100
from stock_selector import DynamicStockSelector
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta

class EarningsMomentumStrategy(BaseStrategy):
    def __init__(self, api, demo_mode=False):
        super().__init__(
            name="Earnings Momentum",
            allocation_percent=0.20,
            api=api
        )
        
        # Add dynamic stock selection
        self.stock_selector = DynamicStockSelector()
        self.target_stocks = self.stock_selector.get_optimized_stock_list(self.name, 10)
        self.last_optimization = datetime.now()
        
        self.demo_mode = demo_mode
        
        if demo_mode:
            from demo_data import demo_provider
            self.demo_provider = demo_provider
        
        print(f"{self.name} initialized with {len(self.target_stocks)} optimized stocks: {self.target_stocks[:5]}...")
    
    def optimize_stock_list(self):
        """Periodically optimize stock list based on performance"""
        if (datetime.now() - self.last_optimization).days < 1:
            return
        
        old_list = self.target_stocks.copy()
        self.target_stocks = self.stock_selector.update_strategy_targets(self, self.target_stocks)
        self.last_optimization = datetime.now()
        
        if old_list != self.target_stocks:
            print(f"{self.name} stock list updated!")
    
    def scan_for_signals(self):
        """Look for earnings momentum opportunities"""
        
        # Optimize stock list periodically
        self.optimize_stock_list()
        
        if self.demo_mode:
            print(f"  Using demo data for {len(self.target_stocks)} optimized stocks...")
            signals = []
            import random
            
            for symbol in self.target_stocks[:5]:  # Check 5 optimized stocks
                # Simulate earnings in 2-4 days
                momentum_strength = random.uniform(0.02, 0.06)
                
                if random.random() < 0.3:  # 30% chance of signal
                    price_data = self.demo_provider.prices.get(symbol, {})
                    price = price_data.get('current_price', 100.0)
                    
                    signal = {
                        'symbol': symbol,
                        'current_price': price,
                        'momentum_strength': momentum_strength,
                        'direction': 'long',
                        'strength': momentum_strength,
                        'days_to_earnings': random.randint(2, 4),
                        'strategy': self.name
                    }
                    signals.append(signal)
                    print(f"    {symbol}: Price=${price:.2f}, Momentum={momentum_strength:.1%}")
                    print(f"    DEMO SIGNAL: {signal['direction']} {symbol} (earnings momentum)")
            
            return signals
            
        return []
    
    def calculate_position_size(self, account_value, signal_strength=1.0):
        """Calculate position size for swing trades"""
        base_size = account_value * self.allocation_percent * 0.4
        adjusted_size = base_size * signal_strength
        return min(adjusted_size, account_value * 0.08)

if __name__ == "__main__":
    from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL
    
    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
    strategy = EarningsMomentumStrategy(api, demo_mode=True)
    
    print("Testing optimized Earnings Momentum strategy...")
    signals = strategy.scan_for_signals()
    print(f"\nFound {len(signals)} earnings momentum signals")