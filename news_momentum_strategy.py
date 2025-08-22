import pandas as pd
import numpy as np
from strategy_base import BaseStrategy
from config import NASDAQ_100
from stock_selector import DynamicStockSelector
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta

class NewsDrivenMomentumStrategy(BaseStrategy):
    def __init__(self, api, demo_mode=False):
        super().__init__(
            name="News-Driven Momentum",
            allocation_percent=0.02,
            api=api
        )
        
        # Add dynamic stock selection
        self.stock_selector = DynamicStockSelector()
        self.target_stocks = self.stock_selector.get_optimized_stock_list(self.name, 20)
        self.last_optimization = datetime.now()
        
        self.min_momentum = 0.02
        self.max_hold_days = 3
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
        """Look for news-driven momentum opportunities"""
        
        # Optimize stock list periodically
        self.optimize_stock_list()
        
        if self.demo_mode:
            print(f"  Using demo data for {len(self.target_stocks)} optimized stocks...")
            signals = []
            import random
            
            news_types = ['earnings_beat', 'product_launch', 'partnership', 'upgrade']
            
            for symbol in self.target_stocks[:5]:  # Check 5 optimized stocks for news
                if random.random() < 0.15:  # 15% chance of relevant news
                    price_data = self.demo_provider.prices.get(symbol, {})
                    current_price = price_data.get('current_price', 100.0)
                    
                    news_type = random.choice(news_types)
                    momentum_strength = random.uniform(0.02, 0.08)
                    
                    direction = 'long' if random.random() < 0.8 else 'short'
                    follow_through_days = random.randint(1, 3)
                    
                    signal = {
                        'symbol': symbol,
                        'current_price': current_price,
                        'news_type': news_type,
                        'momentum_strength': momentum_strength,
                        'direction': direction,
                        'strength': momentum_strength,
                        'follow_through_days': follow_through_days,
                        'catalyst': f"{news_type.replace('_', ' ').title()}",
                        'strategy': self.name
                    }
                    signals.append(signal)
                    print(f"    {symbol}: {signal['catalyst']} - {momentum_strength:.1%} move")
                    print(f"    Expected follow-through: {follow_through_days} days")
                    print(f"    DEMO SIGNAL: {direction} {symbol} (news momentum)")
            
            return signals
            
        return []
    
    def calculate_position_size(self, account_value, signal_strength=1.0):
        """Calculate position size for news momentum trades"""
        base_size = account_value * self.allocation_percent * 1.0
        adjusted_size = base_size * min(signal_strength * 2.5, 1.8)
        return min(adjusted_size, account_value * 0.015)

if __name__ == "__main__":
    from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL
    
    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
    strategy = NewsDrivenMomentumStrategy(api, demo_mode=True)
    
    print("Testing optimized News-Driven Momentum strategy...")
    signals = strategy.scan_for_signals()
    print(f"\nFound {len(signals)} news momentum signals")