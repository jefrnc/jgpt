import os
from datetime import datetime, time
from typing import Dict, Tuple, Optional
import pytz
import requests
from dotenv import load_dotenv
from src.utils.logger import setup_logger

load_dotenv()


class MarketHoursManager:
    def __init__(self):
        self.logger = setup_logger('market_hours')
        self.eastern = pytz.timezone('US/Eastern')
        
        # Load schedule from .env
        self.premarket_start = self._parse_time(os.getenv('PREMARKET_START', '04:00'))
        self.premarket_end = self._parse_time(os.getenv('PREMARKET_END', '09:30'))
        self.market_open = self._parse_time(os.getenv('MARKET_OPEN', '09:30'))
        self.market_close = self._parse_time(os.getenv('MARKET_CLOSE', '16:00'))
        self.afterhours_end = self._parse_time(os.getenv('AFTERHOURS_END', '20:00'))
        
        self.enable_premarket = os.getenv('ENABLE_PREMARKET', 'true').lower() == 'true'
        self.enable_afterhours = os.getenv('ENABLE_AFTERHOURS', 'false').lower() == 'true'
        self.weekend_pause = os.getenv('WEEKEND_PAUSE', 'true').lower() == 'true'
        
    def _parse_time(self, time_str: str) -> time:
        """Parse time string in HH:MM format"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return time(hour, minute)
        except:
            self.logger.error(f"Invalid time format: {time_str}")
            return time(9, 30)  # Default to market open
    
    def get_current_time_est(self) -> datetime:
        """Get current time in Eastern timezone"""
        return datetime.now(self.eastern)
    
    def is_trading_session(self) -> Tuple[bool, str]:
        """Check if we're in a trading session that should scan"""
        now = self.get_current_time_est()
        current_time = now.time()
        
        # Check if weekend
        if self.weekend_pause and now.weekday() >= 5:  # Saturday=5, Sunday=6
            return False, "weekend"
        
        # Check different sessions
        if self.enable_premarket and self.premarket_start <= current_time < self.premarket_end:
            return True, "premarket"
        
        if self.market_open <= current_time <= self.market_close:
            return True, "market_hours"
        
        if self.enable_afterhours and self.market_close < current_time <= self.afterhours_end:
            return True, "afterhours"
        
        return False, "closed"
    
    def get_next_session_start(self) -> datetime:
        """Get when the next trading session starts"""
        now = self.get_current_time_est()
        current_time = now.time()
        
        # If weekend, return Monday premarket
        if now.weekday() >= 5:  # Saturday=5, Sunday=6
            days_until_monday = 7 - now.weekday()
            if now.weekday() == 6:  # Sunday
                days_until_monday = 1
            
            next_monday = now.replace(hour=self.premarket_start.hour, 
                                    minute=self.premarket_start.minute, 
                                    second=0, microsecond=0)
            
            # Add days to get to Monday
            import datetime as dt
            next_monday = next_monday + dt.timedelta(days=days_until_monday)
            return next_monday
        
        # Check what's next today
        if current_time < self.premarket_start:
            return now.replace(hour=self.premarket_start.hour, 
                             minute=self.premarket_start.minute, 
                             second=0, microsecond=0)
        elif current_time < self.market_open:
            return now.replace(hour=self.market_open.hour, 
                             minute=self.market_open.minute, 
                             second=0, microsecond=0)
        elif current_time < self.market_close:
            return now.replace(hour=self.market_close.hour, 
                             minute=self.market_close.minute, 
                             second=0, microsecond=0)
        else:
            # Next day premarket
            import datetime as dt
            tomorrow = now + dt.timedelta(days=1)
            return tomorrow.replace(hour=self.premarket_start.hour, 
                                  minute=self.premarket_start.minute, 
                                  second=0, microsecond=0)
    
    def time_until_next_session(self) -> int:
        """Get seconds until next trading session"""
        next_start = self.get_next_session_start()
        now = self.get_current_time_est()
        return int((next_start - now).total_seconds())
    
    def get_session_info(self) -> Dict:
        """Get complete session information"""
        is_active, session_type = self.is_trading_session()
        
        info = {
            'is_active': is_active,
            'session_type': session_type,
            'current_time': self.get_current_time_est().strftime('%H:%M:%S ET'),
            'current_date': self.get_current_time_est().strftime('%Y-%m-%d'),
            'day_of_week': self.get_current_time_est().strftime('%A'),
            'premarket_enabled': self.enable_premarket,
            'afterhours_enabled': self.enable_afterhours,
        }
        
        if not is_active:
            info['next_session'] = self.get_next_session_start().strftime('%Y-%m-%d %H:%M:%S ET')
            info['wait_time_minutes'] = self.time_until_next_session() // 60
        
        return info
    
    def should_scan_now(self) -> bool:
        """Main function to check if scanner should run"""
        is_active, session_type = self.is_trading_session()
        
        if is_active:
            self.logger.info(f"✅ Trading session active: {session_type}")
            return True
        else:
            next_session_minutes = self.time_until_next_session() // 60
            self.logger.info(f"💤 Market closed ({session_type}) - Next session in {next_session_minutes} minutes")
            return False
    
    def get_optimal_scan_interval(self) -> int:
        """Get optimal scan interval based on session"""
        is_active, session_type = self.is_trading_session()
        
        if not is_active:
            # When market closed, check every hour instead of every 5 min
            return 3600
        
        # Normal interval during trading sessions
        base_interval = int(os.getenv('SCANNER_INTERVAL', 300))
        
        if session_type == "premarket":
            return base_interval  # Most important for gaps
        elif session_type == "market_hours":
            return base_interval * 2  # Less frequent during market hours
        elif session_type == "afterhours":
            return base_interval * 3  # Even less frequent after hours
        
        return base_interval