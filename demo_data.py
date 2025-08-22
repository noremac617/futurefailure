import random
import pandas as pd
from datetime import datetime
from config import NASDAQ_100

class DemoDataProvider:
    """Provides simulated market data for testing"""
    
    def __init__(self):
        self.prices = self.generate_demo_prices()
        
    def generate_demo_prices(self):
        """Generate realistic demo prices for NASDAQ 100 stocks"""
        prices = {}
        base_prices = {
            'AAPL': 225.0, 'MSFT': 420.0, 'GOOGL': 165.0, 'AMZN': 185.0, 'NVDA': 135.0,
            'TSLA': 248.0, 'META': 575.0, 'AVGO': 175.0, 'PEP': 160.0, 'COST': 875.0
        }
        
        for symbol in NASDAQ_100[:10]:  # Use first 10 stocks
            base_price = base_prices.get(symbol, 100.0)
            
            # Add some random variation (-3% to +3%)
            variation = random.uniform(-0.03, 0.03)
            current_price = base_price * (1 + variation)
            
            # Generate VWAP (slightly different from current price)
            vwap_variation = random.uniform(-0.01, 0.01)
            vwap = base_price * (1 + vwap_variation)
            
            # Generate yesterday's close for gap calculation
            gap_variation = random.uniform(-0.02, 0.02)
            yesterday_close = base_price * (1 + gap_variation)
            
            prices[symbol] = {
                'current_price': round(current_price, 2),
                'vwap': round(vwap, 2),
                'yesterday_close': round(yesterday_close, 2),
                'volume': random.randint(1000000, 10000000),
                'avg_volume': random.randint(800000, 8000000)
            }
            
        return prices
    
    def get_demo_signals(self, strategy_name):
        """Generate demo signals for testing"""
        signals = []
        
        for symbol, data in list(self.prices.items())[:5]:  # Check first 5 stocks
            current_price = data['current_price']
            
            if strategy_name == "VWAP Mean Reversion":
                vwap = data['vwap']
                deviation = (current_price - vwap) / vwap
                
                if abs(deviation) > 0.005:  # 0.5% deviation
                    signals.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'vwap': vwap,
                        'deviation': deviation,
                        'direction': 'long' if deviation < 0 else 'short',
                        'strength': abs(deviation),
                        'strategy': strategy_name
                    })
                    
            elif strategy_name == "Gap Fade":
                yesterday_close = data['yesterday_close']
                gap = (current_price - yesterday_close) / yesterday_close
                
                if 0.008 <= abs(gap) <= 0.025:  # 0.8% to 2.5% gap
                    signals.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'yesterday_close': yesterday_close,
                        'gap_percent': gap,
                        'direction': 'short' if gap > 0 else 'long',
                        'strength': abs(gap),
                        'strategy': strategy_name
                    })
        
        return signals

# Global demo provider
demo_provider = DemoDataProvider()