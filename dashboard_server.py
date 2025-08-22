# dashboard_server.py
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import json
import threading
import time
from datetime import datetime, timedelta
import pandas as pd
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradingMetrics:
    """Real-time trading metrics data structure"""
    portfolio_value: float
    daily_pnl: float
    monthly_return: float
    win_rate: float
    daily_strikes: int
    max_drawdown: float
    vix_level: float
    open_positions: int
    signals_today: int
    trades_executed: int
    api_latency: float
    system_uptime: float
    data_quality: float
    sharpe_ratio: float
    timestamp: str

@dataclass
class StrategyPerformance:
    """Strategy performance data"""
    name: str
    allocation: float
    daily_return: float
    trades_count: int
    tier: int

@dataclass
class Trade:
    """Individual trade data"""
    symbol: str
    strategy: str
    action: str  # BUY/SELL
    shares: int
    price: float
    pnl: float
    timestamp: str

class DashboardDataManager:
    """Manages all dashboard data and real-time updates"""
    
    def __init__(self):
        self.metrics = self._initialize_metrics()
        self.strategies = self._initialize_strategies()
        self.recent_trades = []
        self.portfolio_history = []
        self.risk_events = []
        
    def _initialize_metrics(self) -> TradingMetrics:
        """Initialize with default/starting values"""
        return TradingMetrics(
            portfolio_value=25000.0,
            daily_pnl=0.0,
            monthly_return=0.0,
            win_rate=0.0,
            daily_strikes=0,
            max_drawdown=0.0,
            vix_level=20.0,
            open_positions=0,
            signals_today=0,
            trades_executed=0,
            api_latency=0.0,
            system_uptime=100.0,
            data_quality=100.0,
            sharpe_ratio=0.0,
            timestamp=datetime.now().isoformat()
        )
    
    def _initialize_strategies(self) -> List[StrategyPerformance]:
        """Initialize strategy performance data"""
        strategies = [
            # Tier 1 (50% allocation)
            StrategyPerformance("Earnings Momentum", 20.0, 0.0, 0, 1),
            StrategyPerformance("VWAP Mean Reversion", 15.0, 0.0, 0, 1),
            StrategyPerformance("Technical Breakout", 15.0, 0.0, 0, 1),
            
            # Tier 2 (25% allocation)
            StrategyPerformance("Gap Fade", 10.0, 0.0, 0, 2),
            StrategyPerformance("Sector Rotation", 10.0, 0.0, 0, 2),
            StrategyPerformance("Statistical Pairs", 8.0, 0.0, 0, 2),
            StrategyPerformance("RSI Mean Reversion", 7.0, 0.0, 0, 2),
            
            # Tier 3 (15% allocation)
            StrategyPerformance("Volume Spike Reversal", 5.0, 0.0, 0, 3),
            StrategyPerformance("End-of-Day Momentum", 5.0, 0.0, 0, 3),
            StrategyPerformance("Time-Based Patterns", 3.0, 0.0, 0, 3),
            StrategyPerformance("News-Driven Momentum", 2.0, 0.0, 0, 3),
        ]
        return strategies
    
    def update_metrics(self, new_metrics: Dict):
        """Update trading metrics from external source"""
        for key, value in new_metrics.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, value)
        
        self.metrics.timestamp = datetime.now().isoformat()
        
        # Add to portfolio history for charting
        self.portfolio_history.append({
            'timestamp': self.metrics.timestamp,
            'value': self.metrics.portfolio_value
        })
        
        # Keep only last 100 data points
        if len(self.portfolio_history) > 100:
            self.portfolio_history = self.portfolio_history[-100:]
    
    def add_trade(self, trade: Trade):
        """Add new trade to recent trades list"""
        self.recent_trades.insert(0, trade)
        
        # Keep only last 20 trades
        if len(self.recent_trades) > 20:
            self.recent_trades = self.recent_trades[:20]
        
        # Update strategy trade count
        for strategy in self.strategies:
            if strategy.name.lower() in trade.strategy.lower():
                strategy.trades_count += 1
                break
    
    def update_strategy_performance(self, strategy_name: str, daily_return: float):
        """Update individual strategy performance"""
        for strategy in self.strategies:
            if strategy.name == strategy_name:
                strategy.daily_return = daily_return
                break
    
    def get_dashboard_data(self) -> Dict:
        """Get all data formatted for dashboard"""
        return {
            'metrics': asdict(self.metrics),
            'strategies': [asdict(s) for s in self.strategies],
            'recent_trades': [asdict(t) for t in self.recent_trades[:10]],
            'portfolio_history': self.portfolio_history[-50:],  # Last 50 points for chart
            'risk_events': self.risk_events[-10:]  # Last 10 risk events
        }

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Debug template path
import os
print(f"Current working directory: {os.getcwd()}")
print(f"Flask template folder: {app.template_folder}")
print(f"Templates folder exists: {os.path.exists('templates')}")
if os.path.exists('templates'):
    print(f"Templates folder contents: {os.listdir('templates')}")

# Global data manager
data_manager = DashboardDataManager()

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    try:
        return render_template('dashboard.html')
    except Exception as e:
        print(f"Error rendering template: {e}")
        return f"<h1>Template Error</h1><p>{e}</p><p>Current directory: {os.getcwd()}</p>"

@app.route('/api/data')
def get_data():
    """API endpoint to get all dashboard data"""
    return jsonify(data_manager.get_dashboard_data())

@app.route('/api/metrics')
def get_metrics():
    """API endpoint to get just metrics"""
    return jsonify(asdict(data_manager.metrics))

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected to dashboard')
    emit('initial_data', data_manager.get_dashboard_data())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected from dashboard')

class TradingEngineConnector:
    """Connects trading engine to dashboard"""
    
    def __init__(self, data_manager: DashboardDataManager):
        self.data_manager = data_manager
        self.running = False
        
    def start_monitoring(self):
        """Start monitoring thread"""
        self.running = True
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        logger.info("Trading engine monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        logger.info("Trading engine monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Read data from your trading engine
                # This could be from files, database, or direct function calls
                trading_data = self._read_trading_engine_data()
                
                if trading_data:
                    # Update metrics
                    self.data_manager.update_metrics(trading_data['metrics'])
                    
                    # Add any new trades
                    for trade_data in trading_data.get('new_trades', []):
                        trade = Trade(**trade_data)
                        self.data_manager.add_trade(trade)
                    
                    # Update strategy performance
                    for strategy_data in trading_data.get('strategy_updates', []):
                        self.data_manager.update_strategy_performance(
                            strategy_data['name'], 
                            strategy_data['daily_return']
                        )
                    
                    # Broadcast update to all connected clients
                    socketio.emit('data_update', self.data_manager.get_dashboard_data())
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Wait longer on error
    
    def _read_trading_engine_data(self) -> Optional[Dict]:
        """Read data from trading engine - CUSTOMIZE THIS"""
        try:
            # Option 1: Read from JSON file that your trading engine updates
            try:
                with open('trading_data.json', 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                pass
            
            # Option 2: Direct integration with your trading engine
            # You would import your trading engine modules here
            # from fully_optimized_engine import get_current_metrics
            # return get_current_metrics()
            
            # Option 3: Database connection
            # return self._read_from_database()
            
            return None
            
        except Exception as e:
            logger.error(f"Error reading trading engine data: {e}")
            return None

# API endpoints for trading engine to push data
@app.route('/api/update_metrics', methods=['POST'])
def update_metrics():
    """Endpoint for trading engine to push metrics updates"""
    try:
        from flask import request
        metrics_data = request.get_json()
        data_manager.update_metrics(metrics_data)
        
        # Broadcast to all connected clients
        socketio.emit('data_update', data_manager.get_dashboard_data())
        
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error updating metrics: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/add_trade', methods=['POST'])
def add_trade():
    """Endpoint for trading engine to report new trades"""
    try:
        from flask import request
        trade_data = request.get_json()
        trade = Trade(**trade_data)
        data_manager.add_trade(trade)
        
        # Broadcast to all connected clients
        socketio.emit('new_trade', asdict(trade))
        
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error adding trade: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def simulate_trading_data():
    """Simulate trading data for testing - REMOVE IN PRODUCTION"""
    import random
    
    # Simulate portfolio value changes
    current_value = data_manager.metrics.portfolio_value
    change = random.uniform(-50, 100)
    new_value = max(20000, current_value + change)
    
    metrics_update = {
        'portfolio_value': new_value,
        'daily_pnl': new_value - 25000,
        'monthly_return': ((new_value / 25000) - 1) * 100,
        'win_rate': random.uniform(55, 75),
        'signals_today': data_manager.metrics.signals_today + random.randint(0, 2),
        'trades_executed': data_manager.metrics.trades_executed + random.randint(0, 1),
        'api_latency': random.uniform(100, 200),
        'vix_level': random.uniform(15, 25)
    }
    
    data_manager.update_metrics(metrics_update)
    
    # Occasionally add a random trade
    if random.random() < 0.3:
        symbols = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'GOOGL', 'AMZN', 'META']
        strategies = ['VWAP Mean Reversion', 'Technical Breakout', 'Gap Fade', 'Earnings Momentum']
        
        trade = Trade(
            symbol=random.choice(symbols),
            strategy=random.choice(strategies),
            action=random.choice(['BUY', 'SELL']),
            shares=random.randint(1, 50),
            price=random.uniform(100, 500),
            pnl=random.uniform(-50, 100),
            timestamp=datetime.now().isoformat()
        )
        data_manager.add_trade(trade)
    
    # Broadcast updates
    socketio.emit('data_update', data_manager.get_dashboard_data())

if __name__ == '__main__':
    # Initialize connector
    connector = TradingEngineConnector(data_manager)
    
    # Start background monitoring
    connector.start_monitoring()
    
    # SIMULATION DISABLED - Will use real data from trading engine
    print("📊 Dashboard server starting - waiting for real trading data...")
    print("🚫 Simulation mode disabled")
    
    # Start the Flask-SocketIO server
    logger.info("Starting dashboard server on http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)