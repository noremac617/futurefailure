import alpaca_trade_api as tradeapi
from datetime import datetime, time
import time as sleep_time
from config import *
from vwap_strategy import VWAPMeanReversionStrategy
from trading_engine_integration import integrate_with_existing_engine

class TradingEngine:
    def __init__(self, testing_mode=False):
        """Initialize the trading engine"""
        self.api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
        self.strategies = []
        self.daily_pnl = 0
        self.is_running = False
        self.testing_mode = testing_mode  # Skip market hours check when testing
        
        # Initialize strategies
        self.init_strategies()
        
    def init_strategies(self):
        """Initialize all trading strategies"""
        self.strategies = [
            VWAPMeanReversionStrategy(self.api),
            # We'll add more strategies here later
        ]
        print(f"Initialized {len(self.strategies)} strategies")
        
    def is_market_open(self):
        """Check if market is currently open"""
        if self.testing_mode:
            return True  # Always "open" in testing mode
            
        try:
            clock = self.api.get_clock()
            return clock.is_open
        except:
            # Fallback: check time manually (Eastern Time)
            now = datetime.now().time()
            market_open = time(9, 30)  # 9:30 AM
            market_close = time(16, 0)  # 4:00 PM
            return market_open <= now <= market_close
            
    def get_account_summary(self):
        """Get current account status"""
        try:
            account = self.api.get_account()
            positions = self.api.list_positions()
            
            # Some paper accounts don't have day_trade_count
            day_trade_count = getattr(account, 'day_trade_count', 0)
            
            return {
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value),
                'cash': float(account.cash),
                'day_trade_count': int(day_trade_count) if day_trade_count else 0,
                'positions_count': len(positions),
                'positions': [{'symbol': p.symbol, 'qty': p.qty, 'unrealized_pnl': p.unrealized_pnl} for p in positions]
            }
        except Exception as e:
            print(f"Error getting account summary: {e}")
            return {
                'buying_power': 25000.0,
                'portfolio_value': 25000.0,
                'cash': 25000.0,
                'day_trade_count': 0,
                'positions_count': 0,
                'positions': []
            }
            
    def scan_all_strategies(self):
        """Run signal detection for all strategies"""
        all_signals = []
        
        print(f"\n{'='*50}")
        print(f"Scanning at {datetime.now().strftime('%H:%M:%S')}")
        if self.testing_mode:
            print("🧪 TESTING MODE - Market hours check disabled")
        print(f"{'='*50}")
        
        for strategy in self.strategies:
            if strategy.can_trade():
                print(f"\n[{strategy.name}] Scanning...")
                try:
                    signals = strategy.scan_for_signals()
                    # Add strategy name to each signal
                    for signal in signals:
                        signal['strategy'] = strategy.name
                    all_signals.extend(signals)
                    print(f"[{strategy.name}] Found {len(signals)} signals")
                except Exception as e:
                    print(f"[{strategy.name}] Error: {e}")
            else:
                print(f"[{strategy.name}] Skipping - strategy limits reached")
                
        return all_signals
    
    def execute_paper_trade(self, signal):
        """Simulate trade execution for paper trading"""
        account = self.get_account_summary()
        if not account:
            return False
            
        strategy = next((s for s in self.strategies if s.name == signal.get('strategy')), None)
        if not strategy:
            print(f"Could not find strategy for signal: {signal}")
            return False
        
        # Handle different signal types
        if signal.get('direction') == 'pairs_trade':
            # Handle pairs trading signals
            long_symbol = signal['long_symbol']
            short_symbol = signal['short_symbol']
            long_price = signal['long_price']
            short_price = signal['short_price']
            
            position_size = strategy.calculate_position_size(
                account['portfolio_value'], 
                signal.get('strength', 1.0)
            )
            
            # Use fractional shares - calculate exact quantities
            long_quantity = round(position_size / long_price, 4)  # 4 decimal places
            short_quantity = round(position_size / short_price, 4)
            
            print(f"PAIRS TRADE: Long {long_quantity} {long_symbol} @ ${long_price:.2f}")
            print(f"             Short {short_quantity} {short_symbol} @ ${short_price:.2f}")
            print(f"   Total position value: ${(long_quantity * long_price + short_quantity * short_price):.2f}")
            print(f"   Strategy: {signal.get('strategy', 'Unknown')}")
            
        else:
            # Handle regular single-stock signals
            current_price = signal.get('current_price')
            if not current_price:
                print(f"No price data for signal: {signal}")
                return False
                
            position_size = strategy.calculate_position_size(
                account['portfolio_value'], 
                signal.get('strength', 1.0)
            )
            
            # Use fractional shares - calculate exact quantity
            quantity = round(position_size / current_price, 4)  # 4 decimal places
            
            # Minimum position size check (e.g., $10 minimum)
            if position_size < 10:
                print(f"Position size too small for {signal['symbol']} (${position_size:.2f} < $10 minimum)")
                return False
                
            print(f"PAPER TRADE: {signal['direction']} {quantity} shares of {signal['symbol']} @ ${current_price:.2f}")
            print(f"   Position value: ${quantity * current_price:.2f}")
            print(f"   Strategy: {signal.get('strategy', 'Unknown')}")
        
        return True
    
    def run_once(self):
        """Run one complete scan cycle"""
        if not self.is_market_open():
            print("🕐 Market is closed")
            return
            
        # Get account summary
        account = self.get_account_summary()
        if account:
            print(f"💰 Portfolio Value: ${account['portfolio_value']:,.2f}")
            print(f"💵 Buying Power: ${account['buying_power']:,.2f}")
            print(f"📊 Active Positions: {account['positions_count']}")
        
        # Scan for signals
        signals = self.scan_all_strategies()
        
        # Execute signals (paper trading for now)
        if signals:
            print(f"\n🎯 Executing {len(signals)} signals:")
            for signal in signals:
                self.execute_paper_trade(signal)
        else:
            print("\n😴 No signals found this cycle")
    
    def run_continuous(self, scan_interval_minutes=5):
        """Run the engine continuously"""
        print(f"🚀 Starting Trading Engine...")
        print(f"📊 Scan interval: {scan_interval_minutes} minutes")
        
        self.is_running = True
        
        try:
            while self.is_running:
                self.run_once()
                print(f"\n⏰ Waiting {scan_interval_minutes} minutes until next scan...")
                sleep_time.sleep(scan_interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping trading engine...")
            self.is_running = False

# Test the engine
if __name__ == "__main__":
    # Test with testing mode enabled
    engine = TradingEngine(testing_mode=True)
    
    print("Testing single scan with testing mode...")
    engine.run_once()
    
    # Uncomment this to run continuously:
    # engine.run_continuous(scan_interval_minutes=5)