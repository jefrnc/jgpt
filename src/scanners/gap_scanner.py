import os
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Tuple
import pytz
from dotenv import load_dotenv
from alpaca.data.timeframe import TimeFrame
from src.api.alpaca_client import AlpacaClient
from src.utils.logger import setup_logger
import asyncio
import pandas as pd

load_dotenv()


class GapScanner:
    def __init__(self):
        self.client = AlpacaClient()
        self.logger = setup_logger('gap_scanner')
        
        # Trading parameters from .env
        self.min_gap_percent = float(os.getenv('MIN_GAP_PERCENT', 5))
        self.min_price = float(os.getenv('MIN_PRICE', 0.50))
        self.max_price = float(os.getenv('MAX_PRICE', 20.00))
        self.min_volume = 100000  # Minimum average volume
        
        self.eastern = pytz.timezone('US/Eastern')
        
    def calculate_gap_percentage(self, premarket_price: float, previous_close: float) -> float:
        """Calculate gap percentage between premarket and previous close"""
        if previous_close == 0:
            return 0
        return ((premarket_price - previous_close) / previous_close) * 100
    
    def get_previous_close(self, symbol: str) -> Optional[float]:
        """Get previous day's closing price using snapshot data"""
        try:
            # Use snapshot which includes previous daily bar
            snapshot = self.client.get_snapshot(symbol)
            
            if snapshot and snapshot.previous_daily_bar:
                # Use previous_daily_bar for the actual previous trading day
                return float(snapshot.previous_daily_bar.close)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting previous close for {symbol}: {str(e)}")
            return None
    
    def get_premarket_price(self, symbol: str) -> Optional[Tuple[float, int]]:
        """Get current premarket price and volume"""
        try:
            snapshot = self.client.get_snapshot(symbol)
            
            if snapshot and snapshot.latest_trade:
                current_price = float(snapshot.latest_trade.price)
                
                # Get premarket volume
                minute_bar = snapshot.minute_bar
                volume = int(minute_bar.volume) if minute_bar else 0
                
                return current_price, volume
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting premarket price for {symbol}: {str(e)}")
            return None
    
    def scan_symbol(self, symbol: str) -> Optional[Dict]:
        """Scan a single symbol for gap criteria"""
        try:
            # Check if tradeable
            if not self.client.is_tradeable(symbol):
                return None
            
            # Get previous close
            previous_close = self.get_previous_close(symbol)
            if not previous_close:
                return None
            
            # Get current premarket data
            premarket_data = self.get_premarket_price(symbol)
            if not premarket_data:
                return None
            
            current_price, volume = premarket_data
            
            # Check price range
            if current_price < self.min_price or current_price > self.max_price:
                return None
            
            # Calculate gap
            gap_percent = self.calculate_gap_percentage(current_price, previous_close)
            
            # Check gap threshold
            if abs(gap_percent) < self.min_gap_percent:
                return None
            
            # Prepare result
            result = {
                'symbol': symbol,
                'previous_close': previous_close,
                'current_price': current_price,
                'gap_percent': round(gap_percent, 2),
                'volume': volume,
                'gap_direction': 'UP' if gap_percent > 0 else 'DOWN',
                'timestamp': datetime.now(self.eastern).isoformat()
            }
            
            self.logger.info(f"Gap found: {symbol} {result['gap_direction']} {abs(gap_percent):.2f}%")
            return result
            
        except Exception as e:
            self.logger.error(f"Error scanning {symbol}: {str(e)}")
            return None
    
    def scan_watchlist(self, symbols: List[str]) -> List[Dict]:
        """Scan a list of symbols for gaps"""
        self.logger.info(f"Scanning {len(symbols)} symbols for gaps...")
        
        results = []
        for symbol in symbols:
            gap_data = self.scan_symbol(symbol)
            if gap_data:
                results.append(gap_data)
        
        # Sort by gap percentage (highest first)
        results.sort(key=lambda x: abs(x['gap_percent']), reverse=True)
        
        self.logger.info(f"Found {len(results)} symbols with gaps > {self.min_gap_percent}%")
        return results
    
    def get_market_movers(self) -> List[str]:
        """Get list of potential movers to scan"""
        # Mix of volatile small/micro caps and some liquid names
        # TODO: Implement dynamic screener for top % gainers/losers
        watchlist = [
            # Micro/Small caps prone to gaps
            'KLTO', 'KZIA', 'VTAK', 'HSDT', 'CARM', 'OEGD', 'KNW', 'SIR',
            'SXTC', 'IMPP', 'INDO', 'BFRI', 'XELA', 'MULN', 'BBIG', 'PROG',
            'ATER', 'GFAI', 'RDBX', 'NEGG', 'BKKT', 'DWAC', 'PHUN', 'MARK',
            'IZEA', 'NAKD', 'SNDL', 'CLOV', 'WKHS', 'RIDE', 'NKLA', 'GOEV',
            # Some liquid names for comparison
            'AMC', 'GME', 'BBBY', 'SOFI', 'PLTR', 'NIO', 'MARA', 'RIOT'
        ]
        return watchlist
    
    def format_results(self, results: List[Dict]) -> str:
        """Format scan results for display"""
        if not results:
            return "No gaps found matching criteria."
        
        output = f"\n{'='*60}\n"
        output += f"Gap Scanner Results - {datetime.now(self.eastern).strftime('%Y-%m-%d %H:%M:%S ET')}\n"
        output += f"{'='*60}\n\n"
        
        for gap in results:
            output += f"Symbol: {gap['symbol']}\n"
            output += f"Gap: {gap['gap_direction']} {abs(gap['gap_percent'])}%\n"
            output += f"Price: ${gap['previous_close']:.2f} → ${gap['current_price']:.2f}\n"
            output += f"Volume: {gap['volume']:,}\n"
            output += f"{'-'*40}\n"
        
        return output
    
    def is_market_hours(self) -> bool:
        """Check if we're in regular market hours"""
        now = datetime.now(self.eastern)
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        return market_open <= now <= market_close
    
    def is_premarket_hours(self) -> bool:
        """Check if we're in premarket hours"""
        now = datetime.now(self.eastern)
        premarket_start = now.replace(hour=4, minute=0, second=0, microsecond=0)
        premarket_end = now.replace(hour=9, minute=30, second=0, microsecond=0)
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        return premarket_start <= now < premarket_end