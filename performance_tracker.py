import json
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import os

class PerformanceTracker:
    def __init__(self, data_file='performance_data.json'):
        self.data_file = data_file
        self.performance_data = self.load_data()
        
    def load_data(self):
        """Load historical performance data"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    # Convert defaultdict back to regular dict for JSON compatibility
                    if 'strategy_stats' in data:
                        return data
        except:
            pass
        
        # Initialize empty structure
        return {
            'trades': [],
            'strategy_stats': {}  # Regular dict instead of defaultdict
        }
    
    def save_data(self):
        """Save performance data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.performance_data, f, indent=2)
        except Exception as e:
            print(f"Error saving performance data: {e}")
    
    def record_trade(self, strategy_name, symbol, entry_price, exit_price, entry_time, exit_time, direction='long', signal_strength=1.0):
        """Record a completed trade"""
        
        # Calculate P&L
        if direction == 'long':
            pnl_percent = (exit_price - entry_price) / entry_price
        else:
            pnl_percent = (entry_price - exit_price) / entry_price
        
        # Calculate hold time in hours
        if isinstance(entry_time, str):
            entry_time = datetime.fromisoformat(entry_time)
        if isinstance(exit_time, str):
            exit_time = datetime.fromisoformat(exit_time)
        
        hold_time_hours = (exit_time - entry_time).total_seconds() / 3600
        
        # Record trade
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            'strategy': strategy_name,
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'entry_time': entry_time.isoformat(),
            'exit_time': exit_time.isoformat(),
            'pnl_percent': pnl_percent,
            'hold_time_hours': hold_time_hours,
            'signal_strength': signal_strength,
            'win': pnl_percent > 0
        }
        
        self.performance_data['trades'].append(trade_record)
        
        # Update strategy stats - FIX THE NESTED DICTIONARY ISSUE
        if strategy_name not in self.performance_data['strategy_stats']:
            self.performance_data['strategy_stats'][strategy_name] = {}
        
        if symbol not in self.performance_data['strategy_stats'][strategy_name]:
            self.performance_data['strategy_stats'][strategy_name][symbol] = {
                'total_trades': 0,
                'winning_trades': 0,
                'total_pnl': 0.0,
                'avg_hold_time': 0.0
            }
        
        stats = self.performance_data['strategy_stats'][strategy_name][symbol]
        stats['total_trades'] += 1
        if pnl_percent > 0:
            stats['winning_trades'] += 1
        stats['total_pnl'] += pnl_percent
        stats['avg_hold_time'] = (stats['avg_hold_time'] * (stats['total_trades'] - 1) + hold_time_hours) / stats['total_trades']
        
        self.save_data()
        print(f"📊 Recorded trade: {strategy_name} {direction} {symbol} PnL: {pnl_percent:.2%}")
    
    def get_strategy_performance(self, strategy_name, min_trades=5):
        """Get performance stats for a strategy"""
        if strategy_name not in self.performance_data['strategy_stats']:
            return {}
        
        strategy_data = self.performance_data['strategy_stats'][strategy_name]
        results = {}
        
        for symbol, stats in strategy_data.items():
            if stats['total_trades'] >= min_trades:
                win_rate = stats['winning_trades'] / stats['total_trades']
                avg_pnl = stats['total_pnl'] / stats['total_trades']
                
                # Calculate performance score (win rate * avg profit)
                performance_score = win_rate * max(avg_pnl, 0.001)
                
                results[symbol] = {
                    'total_trades': stats['total_trades'],
                    'win_rate': win_rate,
                    'avg_pnl_percent': avg_pnl,
                    'total_pnl_percent': stats['total_pnl'],
                    'avg_hold_time': stats['avg_hold_time'],
                    'performance_score': performance_score
                }
        
        return results
    
    def get_top_performers(self, strategy_name, count=10, min_trades=3):
        """Get top performing stocks for a strategy"""
        performance = self.get_strategy_performance(strategy_name, min_trades)
        
        if not performance:
            return []
        
        # Sort by performance score (win rate * avg profit)
        sorted_stocks = sorted(
            performance.items(), 
            key=lambda x: x[1]['performance_score'], 
            reverse=True
        )
        
        return [stock for stock, stats in sorted_stocks[:count]]
    
    def get_strategy_summary(self, strategy_name):
        """Get overall summary for a strategy"""
        trades = [t for t in self.performance_data['trades'] if t['strategy'] == strategy_name]
        
        if not trades:
            return None
        
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t['win'])
        total_pnl = sum(t['pnl_percent'] for t in trades)
        
        return {
            'total_trades': total_trades,
            'win_rate': winning_trades / total_trades,
            'avg_pnl_percent': total_pnl / total_trades,
            'total_pnl_percent': total_pnl,
            'best_stock': self.get_top_performers(strategy_name, 1),
            'active_stocks': len(set(t['symbol'] for t in trades))
        }

# Test the tracker
if __name__ == "__main__":
    tracker = PerformanceTracker()
    
    # Simulate some trades
    tracker.record_trade(
        "VWAP Mean Reversion", "AAPL", 225.0, 227.0, 
        datetime.now() - timedelta(hours=2), datetime.now()
    )
    
    tracker.record_trade(
        "VWAP Mean Reversion", "MSFT", 420.0, 415.0, 
        datetime.now() - timedelta(hours=1), datetime.now()
    )
    
    # Check performance
    performance = tracker.get_strategy_performance("VWAP Mean Reversion")
    print("Strategy Performance:", performance)
    
    top_performers = tracker.get_top_performers("VWAP Mean Reversion")
    print("Top Performers:", top_performers)