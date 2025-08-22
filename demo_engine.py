from trading_engine import TradingEngine
from vwap_strategy import VWAPMeanReversionStrategy
from earnings_strategy import EarningsMomentumStrategy
from breakout_strategy import TechnicalBreakoutStrategy
from sector_strategy import SectorRotationStrategy
from pairs_strategy import StatisticalPairsStrategy
from gap_fade_strategy import GapFadeStrategy
from rsi_strategy import RSIMeanReversionStrategy
from volume_spike_strategy import VolumeSpikeReversalStrategy
from eod_momentum_strategy import EndOfDayMomentumStrategy
from time_pattern_strategy import TimeBasedPatternStrategy
from news_momentum_strategy import NewsDrivenMomentumStrategy

class CompleteTradingEngine(TradingEngine):
    def __init__(self):
        """Initialize complete 11-strategy trading engine"""
        super().__init__(testing_mode=True)
        
    def init_strategies(self):
        """Initialize all 11 strategies in demo mode"""
        self.strategies = [
            # Tier 1: High-Priority Strategies (50% total allocation)
            EarningsMomentumStrategy(self.api, demo_mode=True),        # 20%
            VWAPMeanReversionStrategy(self.api, demo_mode=True),       # 15%
            TechnicalBreakoutStrategy(self.api, demo_mode=True),       # 15%
            
            # Tier 2: Medium-Priority Strategies (25% total allocation)
            GapFadeStrategy(self.api, demo_mode=True),                 # 10%
            SectorRotationStrategy(self.api, demo_mode=True),          # 10%
            StatisticalPairsStrategy(self.api, demo_mode=True),        # 8%
            RSIMeanReversionStrategy(self.api, demo_mode=True),        # 7%
            
            # Tier 3: Opportunistic Strategies (15% total allocation)
            VolumeSpikeReversalStrategy(self.api, demo_mode=True),     # 5%
            EndOfDayMomentumStrategy(self.api, demo_mode=True),        # 5%
            TimeBasedPatternStrategy(self.api, demo_mode=True),        # 3%
            NewsDrivenMomentumStrategy(self.api, demo_mode=True),      # 2%
        ]
        
        print(f"🚀 Initialized {len(self.strategies)} strategies")
        print("\n📊 Strategy Allocations:")
        
        tier1_total = tier2_total = tier3_total = 0
        
        print("  Tier 1 (High-Priority):")
        for strategy in self.strategies[:3]:
            allocation = strategy.allocation_percent * 100
            tier1_total += allocation
            print(f"    {strategy.name}: {allocation:.0f}%")
            
        print("  Tier 2 (Medium-Priority):")
        for strategy in self.strategies[3:7]:
            allocation = strategy.allocation_percent * 100
            tier2_total += allocation
            print(f"    {strategy.name}: {allocation:.0f}%")
            
        print("  Tier 3 (Opportunistic):")
        for strategy in self.strategies[7:]:
            allocation = strategy.allocation_percent * 100
            tier3_total += allocation
            print(f"    {strategy.name}: {allocation:.0f}%")
            
        print(f"\n📈 Total Allocations:")
        print(f"  Tier 1: {tier1_total:.0f}%")
        print(f"  Tier 2: {tier2_total:.0f}%") 
        print(f"  Tier 3: {tier3_total:.0f}%")
        print(f"  TOTAL: {tier1_total + tier2_total + tier3_total:.0f}%")

# Test the complete system
if __name__ == "__main__":
    engine = CompleteTradingEngine()
    print("\n🎯 COMPLETE TRADING SYSTEM - ALL 11 STRATEGIES")
    print("=" * 60)
    engine.run_once()