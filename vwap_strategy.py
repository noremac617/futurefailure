import pandas as pd
import numpy as np
from strategy_base import BaseStrategy
from config import TOP_LIQUID_STOCKS
from stock_selector import DynamicStockSelector
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta

class VWAPMeanReversionStrategy(BaseStrategy):
    def __init__(self, api, demo_mode=False):
        super().__init__(
            name="VWAP Mean Reversion",
            allocation_percent=0.15,
            api=api
        )
        
        # Initialize dynamic stock selection
        self.stock_selector = DynamicStockSelector()
        self.target_stocks = self.stock_selector.get_optimized_stock_list(self.name, 8)
        self.last_optimization = datetime.now()
        
        self.min_deviation = 0.005
        self.demo_mode = demo_mode
        
        if demo_mode:
            from demo_data import demo_provider
            self.demo_provider = demo_provider
        
        print(f"🎯 {self.name} initialized with {len(self.target_stocks)} optimized stocks: {self.target_stocks}")
    
    def optimize_stock_list(self):
        """Periodically optimize stock list based on performance"""
        
        # Only optimize once per day
        if (datetime.now() - self.last_optimization).days < 1:
            return
        
        old_list = self.target_stocks.copy()
        self.target_stocks = self.stock_selector.update_strategy_targets(self, self.target_stocks)
        self.last_optimization = datetime.now()
        
        if old_list != self.target_stocks:
            print(f"🔄 {self.name} stock list updated!")
    
    def scan_for_signals(self):
        """Look for VWAP mean reversion opportunities"""
        
        # Optimize stock list periodically
        self.optimize_stock_list()
        
        if self.demo_mode:
            print(f"  🎭 Using demo data for {len(self.target_stocks)} optimized stocks...")
            signals = self.demo_provider.get_demo_signals(self.name)
            
            # Filter signals to only include our optimized stocks
            filtered_signals = [s for s in signals if s['symbol'] in self.target_stocks]
            
            for signal in filtered_signals:
                print(f"    {signal['symbol']}: Price=${signal['current_price']:.2f}, VWAP=${signal['vwap']:.2f}, Dev={signal['deviation']:.2%}")
                print(f"    ✅ DEMO SIGNAL: {signal['direction']} {signal['symbol']}")
            
            return filtered_signals
            
        # Real logic for live data (unchanged)
        signals = []
        print(f"Scanning {len(self.target_stocks)} optimized stocks: {self.target_stocks}")
        
            
        # Original logic for live data (will work when you upgrade Alpaca)
        signals = []
        print(f"Scanning {len(self.target_stocks)} stocks: {self.target_stocks}")
        
        for symbol in self.target_stocks:
            try:
                print(f"  Checking {symbol}...")
                
                # This will work when you have the $99 Alpaca plan
                today = datetime.now().date()
                bars = self.api.get_bars(
                    symbol,
                    '1Min',
                    start=today.isoformat(),
                    end=(today + timedelta(days=1)).isoformat()
                ).df
                
                if len(bars) < 10:
                    print(f"    Not enough data for {symbol}")
                    continue
                    
                # Calculate VWAP and current price
                vwap = self.calculate_vwap(bars)
                current_vwap = vwap.iloc[-1]
                current_price = bars['close'].iloc[-1]
                current_volume = bars['volume'].iloc[-1]
                
                # Calculate deviation
                deviation = (current_price - current_vwap) / current_vwap
                
                print(f"    {symbol}: Price=${current_price:.2f}, VWAP=${current_vwap:.2f}, Dev={deviation:.2%}")
                
                if abs(deviation) > self.min_deviation:
                    # Check volume
                    if len(bars) > 20:
                        avg_volume = bars['volume'].rolling(20).mean().iloc[-1]
                        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                    else:
                        volume_ratio = 1.0
                    
                    signal = {
                        'symbol': symbol,
                        'current_price': current_price,
                        'vwap': current_vwap,
                        'deviation': deviation,
                        'direction': 'short' if deviation > 0 else 'long',
                        'strength': abs(deviation),
                        'volume_ratio': volume_ratio,
                        'strategy': self.name
                    }
                    signals.append(signal)
                    print(f"    ✅ SIGNAL: {signal['direction']} {symbol}")
                        
            except Exception as e:
                print(f"    Error scanning {symbol}: {e}")
                continue
                
        return signals
    
    def calculate_position_size(self, account_value, signal_strength=1.0):
        """Calculate position size"""
        base_size = account_value * self.allocation_percent * 0.5
        adjusted_size = base_size * signal_strength
        return min(adjusted_size, account_value * 0.05)

# Test the strategy
if __name__ == "__main__":
    from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL
    
    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
    
    print("Testing VWAP strategy in demo mode...")
    strategy = VWAPMeanReversionStrategy(api, demo_mode=True)
    signals = strategy.scan_for_signals()
    print(f"\nFound {len(signals)} demo signals")