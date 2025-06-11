import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz
from dotenv import load_dotenv
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockTradesRequest, StockSnapshotRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

load_dotenv()


class AlpacaClient:
    def __init__(self):
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        self.data_client = StockHistoricalDataClient(self.api_key, self.secret_key)
        self.trading_client = TradingClient(self.api_key, self.secret_key, paper=True)
        
        self.eastern = pytz.timezone('US/Eastern')
    
    def get_account(self) -> Dict:
        """Get account information"""
        return self.trading_client.get_account()
    
    def get_positions(self) -> List[Dict]:
        """Get all open positions"""
        return self.trading_client.get_all_positions()
    
    def get_snapshot(self, symbol: str) -> Dict:
        """Get latest snapshot for a symbol"""
        request_params = StockSnapshotRequest(symbol_or_symbols=symbol)
        snapshot = self.data_client.get_stock_snapshot(request_params)
        return snapshot[symbol]
    
    def get_bars(self, symbol: str, timeframe: TimeFrame = TimeFrame.Minute, 
                 start: Optional[datetime] = None, end: Optional[datetime] = None) -> Dict:
        """Get historical bars for a symbol"""
        if not start:
            start = datetime.now() - timedelta(days=1)
        
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=timeframe,
            start=start,
            end=end
        )
        
        bars = self.data_client.get_stock_bars(request_params)
        return bars[symbol]
    
    def get_premarket_movers(self, min_gap_percent: float = 5.0) -> List[Dict]:
        """Get premarket movers based on gap percentage"""
        # This is a placeholder - Alpaca doesn't have a direct endpoint for this
        # In production, we'd need to scan multiple symbols or use a screener
        movers = []
        
        # For now, return empty list
        # TODO: Implement proper scanning logic
        return movers
    
    def place_order(self, symbol: str, qty: int, side: OrderSide, 
                   time_in_force: TimeInForce = TimeInForce.DAY) -> Dict:
        """Place a market order"""
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=time_in_force
        )
        
        order = self.trading_client.submit_order(order_data=market_order_data)
        return order
    
    def get_market_hours(self, date: Optional[datetime] = None) -> Dict:
        """Get market hours for a specific date"""
        if not date:
            date = datetime.now()
        
        # Basic market hours - would need to check calendar API for holidays
        market_open = date.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = date.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'open': market_open.isoformat(),
            'close': market_close.isoformat(),
            'is_open': self.trading_client.get_clock().is_open
        }
    
    def is_tradeable(self, symbol: str) -> bool:
        """Check if a symbol is tradeable"""
        try:
            asset = self.trading_client.get_asset(symbol)
            return asset.tradable
        except:
            return False