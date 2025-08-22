import pandas as pd
import numpy as np
from strategy_base import BaseStrategy
from config import TOP_LIQUID_STOCKS
from stock_selector import DynamicStockSelector
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta

class StatisticalPairsStrategy(BaseStrategy):
    def __init__(self, api, demo_mode=False):
        super().__init__(
            name="Statistical Pairs",
            allocation_percent=0.08,
            api=api
        )
        
        # Add dynamic stock selection
        self.stock_selector = DynamicStockSelector()
        self.target_stocks = self.stock_selector.get_optimized_stock_list(self.name, 12)
        self.last_optimization = datetime.now()
        
        # Define pairs from optimized stocks
        self.pairs = [
            ('AAPL', 'MSFT'),
            ('GOOGL', 'META'),
            ('NVDA', 'AMD'),
            ('PEP', 'COST')
        ]
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
            # Update pairs based on optimized stocks
            self._update_pairs_from_optimized_stocks()
    
    def _update_pairs_from_optimized_stocks(self):
        """Update trading pairs based on optimized stock list"""
        # Create pairs from optimized stocks
        optimized_pairs = []
        
        # Add traditional pairs if both stocks are in optimized list
        traditional_pairs = [('AAPL', 'MSFT'), ('GOOGL', 'META'), ('NVDA', 'AMD'), ('PEP', 'COST')]
        for pair in traditional_pairs:
            if pair[0] in self.target_stocks and pair[1] in self.target_stocks:
                optimized_pairs.append(pair)
        
        # Add additional pairs from top optimized stocks
        top_stocks = self.target_stocks[:8]
        for i in range(0, len(top_stocks)-1, 2):
            if i+1 < len(top_stocks):
                new_pair = (top_stocks[i], top_stocks[i+1])
                if new_pair not in optimized_pairs:
                    optimized_pairs.append(new_pair)
        
        self.pairs = optimized_pairs[:4]  # Keep top 4 pairs
        print(f"    Updated pairs: {self.pairs}")
    
    def scan_for_signals(self):
        """Look for pairs trading opportunities"""
        
        # Optimize stock list periodically
        self.optimize_stock_list()
        
        if self.demo_mode:
            print(f"  Using demo data for {len(self.pairs)} optimized pairs...")
            signals = []
            import random
            
            for stock_a, stock_b in self.pairs[:3]:  # Check first 3 pairs
                if random.random() < 0.3:  # 30% chance of divergence
                    price_a = self.demo_provider.prices.get(stock_a, {}).get('current_price', 100.0)
                    price_b = self.demo_provider.prices.get(stock_b, {}).get('current_price', 100.0)
                    
                    # Simulate correlation breakdown
                    normal_ratio = random.uniform(0.4, 0.6)
                    current_ratio = price_a / price_b
                    divergence = abs(current_ratio - normal_ratio) / normal_ratio
                    
                    if divergence > 0.05:  # 5% divergence threshold
                        # Determine which stock is underperforming
                        if current_ratio > normal_ratio:
                            long_stock, short_stock = stock_b, stock_a
                            long_price, short_price = price_b, price_a
                        else:
                            long_stock, short_stock = stock_a, stock_b
                            long_price, short_price = price_a, price_b
                        
                        signal = {
                            'pair': f"{stock_a}/{stock_b}",
                            'long_symbol': long_stock,
                            'short_symbol': short_stock,
                            'long_price': long_price,
                            'short_price': short_price,
                            'divergence': divergence,
                            'direction': 'pairs_trade',
                            'strength': divergence,
                            'strategy': self.name
                        }
                        signals.append(signal)
                        print(f"    Pair: {stock_a}/{stock_b}")
                        print(f"    Divergence: {divergence:.1%}")
                        print(f"    DEMO SIGNAL: Long {long_stock}, Short {short_stock}")
            
            return signals
            
        return []
    
    def calculate_position_size(self, account_value, signal_strength=1.0):
        """Calculate position size for pairs trades"""
        base_size = account_value * self.allocation_percent * 0.8
        adjusted_size = base_size * signal_strength
        return min(adjusted_size, account_value * 0.04)

if __name__ == "__main__":
    from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL
    
    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
    strategy = StatisticalPairsStrategy(api, demo_mode=True)
    
    print("Testing optimized Statistical Pairs strategy...")
    signals = strategy.scan_for_signals()
    print(f"\nFound {len(signals)} pairs signals")