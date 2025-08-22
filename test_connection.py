import alpaca_trade_api as tradeapi
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL

print("Testing Alpaca connection...")

api = tradeapi.REST(
    ALPACA_API_KEY,
    ALPACA_SECRET_KEY, 
    ALPACA_BASE_URL,
    api_version='v2'
)

try:
    account = api.get_account()
    print(f"✅ Connection successful!")
    print(f"Account Status: {account.status}")
    print(f"Buying Power: ${float(account.buying_power):,.2f}")
    print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
except Exception as e:
    print(f"❌ Connection failed: {e}")