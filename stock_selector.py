import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import NASDAQ_100, TOP_LIQUID_STOCKS
from performance_tracker import PerformanceTracker

class DynamicStockSelector:
    def __init__(self, performance_tracker=None):
        self.tracker = performance_tracker or PerformanceTracker()
        
        # Define strategy-specific base lists
        self.strategy_base_lists = {
            'VWAP Mean Reversion': TOP_LIQUID_STOCKS[:8],
            'Gap Fade': NASDAQ_100[:25],
            'Technical Breakout': NASDAQ_100[:20],
            'Earnings Momentum': NASDAQ_100[:15],
            'Sector Rotation': NASDAQ_100[:30],
            'Statistical Pairs': TOP_LIQUID_STOCKS[:12],
            'RSI Mean Reversion': NASDAQ_100[:20],
            'Volume Spike Reversal': NASDAQ_100[:15],
            'End-of-Day Momentum': TOP_LIQUID_STOCKS[:8],
            'Time-Based Patterns': TOP_LIQUID_STOCKS[:6],
            'News-Driven Momentum': NASDAQ_100[:25]
        }
        
        # Quality requirements by strategy
        self.quality_requirements = {
            'VWAP Mean Reversion': {'min_volume': 2000000, 'max_spread': 0.02},
            'Gap Fade': {'min_volume': 1000000, 'max_spread': 0.03},
            'Technical Breakout': {'min_volume': 1500000, 'max_spread': 0.025},
            'Earnings Momentum': {'min_volume': 1000000, 'max_spread': 0.03},
            'Statistical Pairs': {'min_volume': 2500000, 'max_spread': 0.015},
            'End-of-Day Momentum': {'min_volume': 3000000, 'max_spread': 0.01}
        }
    
    def get_optimized_stock_list(self, strategy_name, target_count=None):
        """Get optimized stock list for a strategy"""
        
        # Get base list for strategy
        base_list = self.strategy_base_lists.get(strategy_name, NASDAQ_100[:15])
        
        if target_count is None:
            target_count = min(len(base_list), 10)  # Default to 10 or less
        
        # Get performance-based recommendations
        top_performers = self.tracker.get_top_performers(strategy_name, target_count * 2)
        
        if len(top_performers) >= target_count // 2:
            # We have enough historical data - use performance-based selection
            optimized_list = self._performance_based_selection(
                strategy_name, base_list, top_performers, target_count
            )
        else:
            # Not enough historical data - use quality-based selection
            optimized_list = self._quality_based_selection(
                strategy_name, base_list, target_count
            )
        
        return optimized_list
    
    def _performance_based_selection(self, strategy_name, base_list, top_performers, target_count):
        """Select stocks based on historical performance"""
        
        # Start with proven performers
        proven_count = min(len(top_performers), target_count // 2)
        selected = top_performers[:proven_count]
        
        # Fill remaining slots with quality picks from base list
        remaining_count = target_count - len(selected)
        candidates = [stock for stock in base_list if stock not in selected]
        
        # Score remaining candidates by quality
        quality_scores = []
        for stock in candidates:
            score = self._calculate_quality_score(stock, strategy_name)
            quality_scores.append((stock, score))
        
        # Sort by quality and take top remaining
        quality_scores.sort(key=lambda x: x[1], reverse=True)
        selected.extend([stock for stock, score in quality_scores[:remaining_count]])
        
        return selected[:target_count]
    
    def _quality_based_selection(self, strategy_name, base_list, target_count):
        """Select stocks based on quality metrics when no performance data"""
        
        quality_scores = []
        for stock in base_list:
            score = self._calculate_quality_score(stock, strategy_name)
            quality_scores.append((stock, score))
        
        # Sort by quality score and return top performers
        quality_scores.sort(key=lambda x: x[1], reverse=True)
        return [stock for stock, score in quality_scores[:target_count]]
    
    def _calculate_quality_score(self, symbol, strategy_name):
        """Calculate quality score for a stock/strategy combination"""
        score = 0
        
        # Base score from liquidity (simulate with symbol characteristics)
        if symbol in TOP_LIQUID_STOCKS:
            score += 10
        elif symbol in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']:
            score += 15
        
        # Strategy-specific scoring
        if strategy_name == 'VWAP Mean Reversion':
            # Prefer stable, high-volume stocks
            if symbol in ['AAPL', 'MSFT', 'GOOGL']:
                score += 5
                
        elif strategy_name == 'Gap Fade':
            # Prefer stocks that gap frequently but predictably
            if symbol in ['TSLA', 'NVDA', 'AMD']:
                score += 5
                
        elif strategy_name == 'Technical Breakout':
            # Prefer momentum stocks
            if symbol in ['NVDA', 'TSLA', 'AMD', 'CRM']:
                score += 5
                
        elif strategy_name == 'Sector Rotation':
            # Prefer sector leaders
            if symbol in ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'META']:
                score += 5
        
        # Add randomness to simulate real market conditions
        import random
        score += random.uniform(0, 3)
        
        return score
    
    def update_strategy_targets(self, strategy, current_list):
        """Update stock targets for a strategy based on performance"""
        
        performance = self.tracker.get_strategy_performance(strategy.name)
        
        if not performance:
            return current_list  # No data yet
        
        # Get optimized list
        optimized_list = self.get_optimized_stock_list(strategy.name, len(current_list))
        
        # Only change if we have significant performance data
        total_trades = sum(stats['total_trades'] for stats in performance.values())
        
        if total_trades >= 20:  # Minimum 20 trades before optimizing
            print(f"🔄 Optimizing {strategy.name} stock list based on {total_trades} trades")
            print(f"   Old: {current_list[:5]}...")
            print(f"   New: {optimized_list[:5]}...")
            return optimized_list
        
        return current_list
    
    def get_strategy_recommendations(self, strategy_name):
        """Get detailed recommendations for a strategy"""
        performance = self.tracker.get_strategy_performance(strategy_name)
        summary = self.tracker.get_strategy_summary(strategy_name)
        optimized_list = self.get_optimized_stock_list(strategy_name)
        
        return {
            'strategy': strategy_name,
            'recommended_stocks': optimized_list,
            'performance_data': performance,
            'summary': summary,
            'data_quality': 'high' if summary and summary['total_trades'] > 50 else 'low'
        }

# Test the selector
if __name__ == "__main__":
    selector = DynamicStockSelector()
    
    # Test optimization for VWAP strategy
    recommendations = selector.get_strategy_recommendations('VWAP Mean Reversion')
    print("VWAP Recommendations:", recommendations['recommended_stocks'])
    
    # Test for all strategies
    for strategy_name in selector.strategy_base_lists.keys():
        optimized = selector.get_optimized_stock_list(strategy_name, 8)
        print(f"{strategy_name}: {optimized}")