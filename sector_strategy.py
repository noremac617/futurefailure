import pandas as pd
import numpy as np
from strategy_base import BaseStrategy
from config import NASDAQ_100
from stock_selector import DynamicStockSelector
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta

class SectorRotationStrategy(BaseStrategy):
    def __init__(self, api, demo_mode=False):
        super().__init__(
            name="Sector Rotation",
            allocation_percent=0.10,
            api=api
        )
        
        # Add dynamic stock selection
        self.stock_selector = DynamicStockSelector()
        self.target_stocks = self.stock_selector.get_optimized_stock_list(self.name, 16)
        self.last_optimization = datetime.now()
        
        # Group stocks by sector
        self.sectors = {
            'Big Tech': ['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
            'Semiconductors': ['NVDA', 'AMD', 'INTC', 'QCOM'],
            'Social Media': ['META', 'NFLX'],
            'Cloud/Software': ['ADBE', 'CRM', 'ORCL']
        }
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
        """Look for sector rotation opportunities"""
        
        # Optimize stock list periodically
        self.optimize_stock_list()
        
        if self.demo_mode:
            print(f"  Using demo data for {len(self.target_stocks)} optimized stocks...")
            signals = []
            import random
            
            # Simulate one hot sector
            hot_sector = random.choice(list(self.sectors.keys()))
            print(f"    Hot Sector: {hot_sector}")
            
            # Only check stocks that are both in hot sector AND in our optimized list
            sector_stocks = self.sectors[hot_sector]
            optimized_sector_stocks = [s for s in sector_stocks if s in self.target_stocks]
            
            for symbol in optimized_sector_stocks[:2]:  # Top 2 in hot sector from optimized list
                if random.random() < 0.4:  # 40% chance per stock
                    price_data = self.demo_provider.prices.get(symbol, {})
                    current_price = price_data.get('current_price', 100.0)
                    
                    # Simulate sector momentum
                    sector_momentum = random.uniform(0.03, 0.08)
                    
                    signal = {
                        'symbol': symbol,
                        'current_price': current_price,
                        'sector': hot_sector,
                        'sector_momentum': sector_momentum,
                        'direction': 'long',
                        'strength': sector_momentum,
                        'hold_days': random.randint(3, 14),
                        'strategy': self.name
                    }
                    signals.append(signal)
                    print(f"    {symbol}: Price=${current_price:.2f}, Sector momentum={sector_momentum:.1%}")
                    print(f"    DEMO SIGNAL: {signal['direction']} {symbol} (sector rotation)")
            
            return signals
            
        return []
    
    def calculate_position_size(self, account_value, signal_strength=1.0):
        """Calculate position size for sector trades"""
        base_size = account_value * self.allocation_percent * 0.6
        adjusted_size = base_size * signal_strength
        return min(adjusted_size, account_value * 0.06)

if __name__ == "__main__":
    from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL
    
    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
    strategy = SectorRotationStrategy(api, demo_mode=True)
    
    print("Testing optimized Sector Rotation strategy...")
    signals = strategy.scan_for_signals()
    print(f"\nFound {len(signals)} sector rotation signals")