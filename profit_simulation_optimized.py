import random
import pandas as pd
from datetime import datetime, timedelta
from fully_optimized_engine import FullyOptimizedEngine

class ProfitSimulator:
    def __init__(self, starting_capital=25000):
        self.starting_capital = starting_capital
        self.current_capital = starting_capital
        self.trades = []
        self.daily_balances = []
        
    def simulate_month(self, target_return=0.03):
        """Simulate a month of optimized trading"""
        
        print(f"Simulating month with ${self.starting_capital:,} starting capital")
        print(f"Target: {target_return:.1%} ({target_return * self.starting_capital:,.0f})")
        print("=" * 60)
        
        self.current_capital = self.starting_capital
        self.trades = []
        self.daily_balances = [self.current_capital]
        
        # Strategy performance based on optimization levels
        strategy_performance = {
            'Earnings Momentum': {'win_rate': 0.72, 'avg_win': 0.045, 'avg_loss': -0.018, 'allocation': 0.20},
            'VWAP Mean Reversion': {'win_rate': 0.78, 'avg_win': 0.012, 'avg_loss': -0.008, 'allocation': 0.15},
            'Technical Breakout': {'win_rate': 0.65, 'avg_win': 0.035, 'avg_loss': -0.015, 'allocation': 0.15},
            'Gap Fade': {'win_rate': 0.68, 'avg_win': 0.018, 'avg_loss': -0.012, 'allocation': 0.10},
            'Sector Rotation': {'win_rate': 0.70, 'avg_win': 0.028, 'avg_loss': -0.016, 'allocation': 0.10},
            'Statistical Pairs': {'win_rate': 0.75, 'avg_win': 0.014, 'avg_loss': -0.009, 'allocation': 0.08},
            'RSI Mean Reversion': {'win_rate': 0.73, 'avg_win': 0.016, 'avg_loss': -0.010, 'allocation': 0.07},
            'Volume Spike Reversal': {'win_rate': 0.66, 'avg_win': 0.022, 'avg_loss': -0.014, 'allocation': 0.05},
            'End-of-Day Momentum': {'win_rate': 0.69, 'avg_win': 0.019, 'avg_loss': -0.011, 'allocation': 0.05},
            'Time-Based Patterns': {'win_rate': 0.64, 'avg_win': 0.008, 'avg_loss': -0.006, 'allocation': 0.03},
            'News-Driven Momentum': {'win_rate': 0.67, 'avg_win': 0.038, 'avg_loss': -0.022, 'allocation': 0.02}
        }
        
        # Simulate 22 trading days
        for day in range(1, 23):
            daily_trades = 0
            daily_pnl = 0
            
            # Each strategy might generate 0-2 trades per day
            for strategy, params in strategy_performance.items():
                trade_probability = 0.3  # 30% chance per strategy per day
                
                if random.random() < trade_probability:
                    # Generate trade
                    position_size = self.current_capital * params['allocation'] * random.uniform(0.3, 0.8)
                    
                    # Determine win/loss
                    is_win = random.random() < params['win_rate']
                    
                    if is_win:
                        pnl_percent = random.uniform(params['avg_win'] * 0.5, params['avg_win'] * 1.5)
                    else:
                        pnl_percent = random.uniform(params['avg_loss'] * 1.5, params['avg_loss'] * 0.5)
                    
                    pnl_dollars = position_size * pnl_percent
                    daily_pnl += pnl_dollars
                    daily_trades += 1
                    
                    # Record trade
                    self.trades.append({
                        'day': day,
                        'strategy': strategy,
                        'position_size': position_size,
                        'pnl_percent': pnl_percent,
                        'pnl_dollars': pnl_dollars,
                        'win': is_win
                    })
            
            # Update capital
            self.current_capital += daily_pnl
            self.daily_balances.append(self.current_capital)
            
            # Calculate current return
            current_return = (self.current_capital - self.starting_capital) / self.starting_capital
            
            print(f"Day {day:2d}: {daily_trades} trades, P&L: ${daily_pnl:+7.0f}, "
                  f"Balance: ${self.current_capital:8,.0f} ({current_return:+5.1%})")
            
            # Check if target reached
            if current_return >= target_return:
                print(f"\n*** TARGET REACHED on Day {day}! ***")
                print(f"Final return: {current_return:.2%}")
                break
        
        return self.analyze_results()
    
    def analyze_results(self):
        """Analyze simulation results"""
        total_return = (self.current_capital - self.starting_capital) / self.starting_capital
        total_trades = len(self.trades)
        winning_trades = sum(1 for trade in self.trades if trade['win'])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        total_pnl = sum(trade['pnl_dollars'] for trade in self.trades)
        avg_win = sum(trade['pnl_dollars'] for trade in self.trades if trade['win']) / winning_trades if winning_trades > 0 else 0
        losing_trades = total_trades - winning_trades
        avg_loss = sum(trade['pnl_dollars'] for trade in self.trades if not trade['win']) / losing_trades if losing_trades > 0 else 0
        
        print(f"\n" + "=" * 60)
        print("SIMULATION RESULTS")
        print("=" * 60)
        print(f"Starting Capital:    ${self.starting_capital:,}")
        print(f"Ending Capital:      ${self.current_capital:,}")
        print(f"Total Return:        {total_return:.2%}")
        print(f"Profit/Loss:         ${total_pnl:+,.0f}")
        print(f"Total Trades:        {total_trades}")
        print(f"Win Rate:            {win_rate:.1%}")
        print(f"Average Win:         ${avg_win:.0f}")
        print(f"Average Loss:        ${avg_loss:.0f}")
        
        # Strategy breakdown
        print(f"\nStrategy Performance:")
        strategy_stats = {}
        for trade in self.trades:
            strategy = trade['strategy']
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {'trades': 0, 'wins': 0, 'pnl': 0}
            strategy_stats[strategy]['trades'] += 1
            if trade['win']:
                strategy_stats[strategy]['wins'] += 1
            strategy_stats[strategy]['pnl'] += trade['pnl_dollars']
        
        for strategy, stats in sorted(strategy_stats.items(), key=lambda x: x[1]['pnl'], reverse=True):
            win_rate = stats['wins'] / stats['trades'] if stats['trades'] > 0 else 0
            print(f"  {strategy:<25} {stats['trades']:2d} trades, {win_rate:.0%} win rate, ${stats['pnl']:+6.0f}")
        
        return {
            'total_return': total_return,
            'total_pnl': total_pnl,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'target_reached': total_return >= 0.03
        }

def run_multiple_simulations(num_simulations=5):
    """Run multiple month simulations"""
    print("OPTIMIZED SYSTEM PROFIT SIMULATION")
    print("=" * 60)
    
    results = []
    
    for i in range(num_simulations):
        print(f"\nSIMULATION {i+1}/{num_simulations}")
        print("-" * 30)
        
        simulator = ProfitSimulator(25000)
        result = simulator.simulate_month()
        results.append(result)
    
    # Summary statistics
    avg_return = sum(r['total_return'] for r in results) / len(results)
    avg_trades = sum(r['total_trades'] for r in results) / len(results)
    avg_win_rate = sum(r['win_rate'] for r in results) / len(results)
    success_rate = sum(1 for r in results if r['target_reached']) / len(results)
    
    print(f"\n" + "=" * 60)
    print("SUMMARY OF ALL SIMULATIONS")
    print("=" * 60)
    print(f"Number of Simulations:   {num_simulations}")
    print(f"Average Monthly Return:  {avg_return:.2%}")
    print(f"Average Trades/Month:    {avg_trades:.0f}")
    print(f"Average Win Rate:        {avg_win_rate:.1%}")
    print(f"Target Success Rate:     {success_rate:.1%}")
    print(f"Monthly Profit Range:    ${min(r['total_pnl'] for r in results):,.0f} to ${max(r['total_pnl'] for r in results):,.0f}")

if __name__ == "__main__":
    run_multiple_simulations(3)