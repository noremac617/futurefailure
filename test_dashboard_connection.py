# test_dashboard_connection.py
import requests
import json
from datetime import datetime

def test_dashboard_connection():
    """Test if dashboard is receiving data"""
    
    print("🧪 Testing dashboard connection...")
    
    # Test metrics update
    test_metrics = {
        'portfolio_value': 26543.21,
        'daily_pnl': 1543.21,
        'monthly_return': 6.17,
        'win_rate': 68.5,
        'daily_strikes': 0,
        'max_drawdown': -2.1,
        'vix_level': 19.2,
        'open_positions': 5,
        'signals_today': 15,  # Should show 15 instead of 23
        'trades_executed': 8,
        'api_latency': 142.0,
        'system_uptime': 99.9,
        'data_quality': 100.0,
        'sharpe_ratio': 2.1,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/update_metrics',
            json=test_metrics,
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Dashboard metrics update successful!")
            print("📊 Check dashboard - signals should show 15")
        else:
            print(f"❌ Dashboard update failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("🔧 Make sure dashboard_server.py is running")
    
    # Test trade reporting
    test_trade = {
        'symbol': 'TEST',
        'strategy': 'Test Strategy',
        'action': 'BUY',
        'shares': 10,
        'price': 150.00,
        'pnl': 0.0,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/add_trade',
            json=test_trade,
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Dashboard trade reporting successful!")
            print("📈 Check dashboard - should see TEST trade")
        else:
            print(f"❌ Trade reporting failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Trade reporting error: {e}")

if __name__ == "__main__":
    test_dashboard_connection()