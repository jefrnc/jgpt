import os
import time
import requests
import yfinance as yf
from typing import Dict, Optional, List
from datetime import datetime
from dotenv import load_dotenv
from src.utils.logger import setup_logger

load_dotenv()


class FinnhubClient:
    def __init__(self):
        self.logger = setup_logger('finnhub_client')
        self.api_key = os.getenv('FINNHUB_API_KEY')
        self.base_url = 'https://finnhub.io/api/v1'
        
        if not self.api_key or self.api_key == 'your_finnhub_api_key_here':
            self.logger.warning("FINNHUB_API_KEY not configured - float data disabled")
            self.enabled = False
            return
        
        self.enabled = True
        self.session = requests.Session()
        self.session.headers.update({'X-Finnhub-Token': self.api_key})
        
        # Rate limiting (60 calls/min free tier)
        self.calls_per_minute = 60
        self.call_timestamps = []
        
    def _rate_limit_check(self):
        """Check and enforce rate limits"""
        if not self.enabled:
            return False
            
        now = time.time()
        # Remove calls older than 1 minute
        self.call_timestamps = [ts for ts in self.call_timestamps if now - ts < 60]
        
        if len(self.call_timestamps) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.call_timestamps[0])
            if sleep_time > 0:
                self.logger.warning(f"Rate limit reached, sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)
                return self._rate_limit_check()
        
        self.call_timestamps.append(now)
        return True
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting"""
        if not self._rate_limit_check():
            return None
            
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 429:
                self.logger.warning("Rate limit hit, backing off...")
                time.sleep(60)
                return self._make_request(endpoint, params)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Finnhub API error: {str(e)}")
            return None
    
    def get_company_metrics(self, symbol: str) -> Optional[Dict]:
        """Get company metrics with fallback to yfinance"""
        # Try Finnhub first
        finnhub_data = self._get_finnhub_metrics(symbol)
        
        # If float data not available, use yfinance fallback
        if not finnhub_data or not finnhub_data.get('shares_outstanding'):
            self.logger.debug(f"Using yfinance fallback for {symbol}")
            yf_data = self._get_yfinance_metrics(symbol)
            if yf_data:
                # Merge data (prefer Finnhub for technical metrics, yfinance for float)
                if finnhub_data:
                    finnhub_data.update(yf_data)
                    return finnhub_data
                else:
                    return yf_data
        
        return finnhub_data
    
    def _get_finnhub_metrics(self, symbol: str) -> Optional[Dict]:
        """Get metrics from Finnhub API"""
        params = {
            'symbol': symbol,
            'metric': 'all'
        }
        
        data = self._make_request('stock/metric', params)
        if not data or 'metric' not in data:
            return None
            
        metrics = data['metric']
        
        # Extract key float metrics
        result = {
            'symbol': symbol,
            'shares_outstanding': metrics.get('sharesOutstanding'),
            'float_shares': metrics.get('floatShares'),
            'market_cap': metrics.get('marketCapitalization'),
            'enterprise_value': metrics.get('enterpriseValue'),
            'shares_short': metrics.get('sharesShort'),
            'short_ratio': metrics.get('shortRatio'),
            'beta': metrics.get('beta'),
            'pe_ratio': metrics.get('peBasicExclExtraTTM'),
            'data_source': 'finnhub',
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def _get_yfinance_metrics(self, symbol: str) -> Optional[Dict]:
        """Get float metrics from Yahoo Finance as fallback"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return None
            
            result = {
                'symbol': symbol,
                'shares_outstanding': info.get('sharesOutstanding'),
                'float_shares': info.get('floatShares'),
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'shares_short': info.get('sharesShort'),
                'short_ratio': info.get('shortRatio'),
                'beta': info.get('beta'),
                'pe_ratio': info.get('trailingPE'),
                'data_source': 'yfinance',
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"yfinance error for {symbol}: {str(e)}")
            return None
    
    def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """Get company profile data"""
        params = {'symbol': symbol}
        
        data = self._make_request('stock/profile2', params)
        if not data:
            return None
            
        return {
            'symbol': symbol,
            'name': data.get('name'),
            'industry': data.get('finnhubIndustry'),
            'sector': data.get('ggroup'),
            'country': data.get('country'),
            'exchange': data.get('exchange'),
            'ipo_date': data.get('ipo'),
            'market_cap': data.get('marketCapitalization'),
            'outstanding_shares': data.get('shareOutstanding'),
            'website': data.get('weburl'),
            'logo': data.get('logo'),
            'phone': data.get('phone')
        }
    
    def get_basic_financials(self, symbol: str) -> Optional[Dict]:
        """Get basic financial metrics"""
        params = {
            'symbol': symbol,
            'metric': 'all'
        }
        
        data = self._make_request('stock/metric', params)
        if not data:
            return None
            
        return data
    
    def calculate_float_metrics(self, symbol: str) -> Optional[Dict]:
        """Calculate advanced float metrics for squeeze analysis"""
        metrics = self.get_company_metrics(symbol)
        if not metrics:
            return None
            
        shares_out = metrics.get('shares_outstanding')
        float_shares = metrics.get('float_shares')
        shares_short = metrics.get('shares_short')
        short_ratio = metrics.get('short_ratio')
        
        if not all([shares_out, float_shares]):
            return None
            
        # Calculate key ratios
        insider_ownership = max(0, (shares_out - float_shares) / shares_out) if shares_out > 0 else 0
        float_percentage = float_shares / shares_out if shares_out > 0 else 0
        short_interest = shares_short / float_shares if shares_short and float_shares > 0 else 0
        
        # Categorize float size
        float_category = self._categorize_float(float_shares)
        squeeze_potential = self._calculate_squeeze_potential(short_interest, short_ratio)
        
        result = {
            'symbol': symbol,
            'shares_outstanding': shares_out,
            'float_shares': float_shares,
            'insider_ownership_pct': round(insider_ownership * 100, 2),
            'float_percentage': round(float_percentage * 100, 2),
            'short_interest_pct': round(short_interest * 100, 2) if short_interest else None,
            'short_ratio': short_ratio,
            'float_category': float_category,
            'squeeze_potential': squeeze_potential,
            'is_microfloat': float_shares < 10_000_000 if float_shares else False,
            'is_low_float': float_shares < 50_000_000 if float_shares else False,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def _categorize_float(self, float_shares: Optional[float]) -> str:
        """Categorize float size"""
        if not float_shares:
            return 'unknown'
        
        if float_shares < 5_000_000:
            return 'nano_float'
        elif float_shares < 10_000_000:
            return 'micro_float'
        elif float_shares < 50_000_000:
            return 'low_float'
        elif float_shares < 200_000_000:
            return 'medium_float'
        else:
            return 'high_float'
    
    def _calculate_squeeze_potential(self, short_interest: Optional[float], 
                                   short_ratio: Optional[float]) -> str:
        """Calculate squeeze potential based on metrics"""
        if not short_interest:
            return 'unknown'
        
        if short_interest > 0.4:  # >40% short interest
            return 'extreme'
        elif short_interest > 0.25:  # >25% short interest
            return 'high'
        elif short_interest > 0.15:  # >15% short interest
            return 'moderate'
        elif short_interest > 0.05:  # >5% short interest
            return 'low'
        else:
            return 'minimal'
    
    def scan_multiple_symbols(self, symbols: List[str]) -> List[Dict]:
        """Scan multiple symbols for float data"""
        results = []
        
        self.logger.info(f"Scanning {len(symbols)} symbols for float data...")
        
        for i, symbol in enumerate(symbols):
            self.logger.debug(f"Scanning {symbol} ({i+1}/{len(symbols)})")
            
            float_data = self.calculate_float_metrics(symbol)
            if float_data:
                results.append(float_data)
            
            # Small delay to be respectful to API
            time.sleep(0.1)
        
        self.logger.info(f"Successfully scanned {len(results)} symbols")
        return results
    
    def get_float_leaders(self, symbols: List[str], 
                         category: str = 'micro_float') -> List[Dict]:
        """Get symbols matching specific float category"""
        all_data = self.scan_multiple_symbols(symbols)
        
        filtered = [
            data for data in all_data 
            if data.get('float_category') == category
        ]
        
        # Sort by float size (smallest first)
        filtered.sort(key=lambda x: x.get('float_shares', float('inf')))
        
        return filtered