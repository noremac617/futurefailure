import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from config import *

class DataHandler:
    def __init__(self):
        """Initialize Alpaca API connection"""
        self.api = tradeapi.REST(
            ALPACA_API_KEY,
            ALPACA_SECRET_KEY,
            ALPACA_BASE_URL,
            api_version='v2'
        )
        
    def get_account_info(self):
        """Get current account information"""
        try:
            account = self.api.get_account()
            return {
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'positions': len(self.api.list_positions())
            }
        except Exception as e:
            print(f"Error getting account info: {e}")
            return None
    
    def get_current_price(self, symbol):
        """Get current price for a symbol"""
        try:
            latest_trade = self.api.get_latest_trade(symbol)
            return latest_trade.price
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol, timeframe='1Day', limit=100):
        """Get historical price data"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=limit)
            
            bars = self.api.get_bars(
                symbol,
                timeframe,
                start=start_time.isoformat(),
                end=end_time.isoformat()
            ).df
            
            return bars
        except Exception as e:
            print(f"Error getting historical data for {symbol}: {e}")
            return None
    
    def calculate_rsi(self, prices, window=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_vwap(self, bars):
        """Calculate VWAP (Volume Weighted Average Price)"""
        typical_price = (bars['high'] + bars['low'] + bars['close']) / 3
        vwap = (typical_price * bars['volume']).cumsum() / bars['volume'].cumsum()
        return vwap

# Test the connection
if __name__ == "__main__":
    data = DataHandler()
    account = data.get_account_info()
    print("Account Info:", account)
    
    # Test getting price for AAPL
    price = data.get_current_price('AAPL')
    print(f"AAPL current price: ${price}")