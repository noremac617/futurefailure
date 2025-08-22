import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Alpaca API Configuration
ALPACA_API_KEY = "PK7AJE09BRFOI5J3AUPF"
ALPACA_SECRET_KEY = "qGgmYN9vfKc4dKeVIMQALhTjp92OQAil8Ai5c8VE"
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"  # Paper trading URL

# Trading Configuration
STARTING_CAPITAL = 25000
MAX_POSITION_SIZE = 0.05  # 5% max per trade
MAX_STRATEGY_ALLOCATION = 0.20  # 20% max per strategy
DAILY_LOSS_LIMIT = 3  # Stop after 3 losses

# NASDAQ 100 Top Liquid Stocks for specific strategies
TOP_LIQUID_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 
    'TSLA', 'META', 'AVGO', 'PEP', 'COST'
]

# All NASDAQ 100 stocks (abbreviated list for now)
NASDAQ_100 = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'AVGO',
    'PEP', 'COST', 'ADBE', 'CMCSA', 'NFLX', 'INTC', 'QCOM', 'TXN',
    'INTU', 'AMAT', 'AMD', 'ISRG', 'BKNG', 'HON', 'AMGN', 'VRTX',
    'GILD', 'MU', 'ADP', 'LRCX', 'SBUX', 'MDLZ'
    # We'll add the full list later
]