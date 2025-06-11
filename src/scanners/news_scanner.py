import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
import pytz
from src.utils.logger import setup_logger

load_dotenv()


class NewsScanner:
    """Scanner for detecting news catalysts"""
    
    def __init__(self):
        self.logger = setup_logger('news_scanner')
        self.finnhub_key = os.getenv('FINNHUB_API_KEY')
        self.eastern = pytz.timezone('US/Eastern')
        
        # Keywords that indicate potential catalysts
        self.catalyst_keywords = [
            # Positive catalysts
            'fda approval', 'fda', 'approved', 'breakthrough', 'patent',
            'contract', 'partnership', 'merger', 'acquisition', 'buyout',
            'earnings beat', 'revenue', 'guidance raised', 'upgrade',
            # Biotech specific
            'phase 3', 'phase 2', 'clinical trial', 'results', 'efficacy',
            'designation', 'clearance', 'milestone',
            # Offerings/Dilution
            'offering', 'dilution', 'warrants', 'direct offering',
            # Short squeeze
            'short squeeze', 'short interest', 'squeeze'
        ]
        
        # Negative keywords to filter out
        self.negative_keywords = [
            'bankruptcy', 'delisting', 'investigation', 'lawsuit',
            'downgrade', 'missed', 'lowered guidance'
        ]
    
    def scan_symbol_news(self, symbol: str, hours_back: int = 24) -> Dict:
        """Scan news for a specific symbol"""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=hours_back)
            
            # Finnhub news API
            if self.finnhub_key:
                url = "https://finnhub.io/api/v1/company-news"
                params = {
                    'symbol': symbol,
                    'from': start_date.strftime('%Y-%m-%d'),
                    'to': end_date.strftime('%Y-%m-%d'),
                    'token': self.finnhub_key
                }
                
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    news_items = response.json()
                    
                    if news_items:
                        # Analyze news
                        catalyst_score = 0
                        key_headlines = []
                        
                        for item in news_items[:5]:  # Check last 5 news
                            headline = item.get('headline', '').lower()
                            summary = item.get('summary', '').lower()
                            full_text = f"{headline} {summary}"
                            
                            # Check for catalyst keywords
                            for keyword in self.catalyst_keywords:
                                if keyword in full_text:
                                    catalyst_score += 10
                                    if len(key_headlines) < 3:
                                        key_headlines.append(item['headline'][:100])
                            
                            # Check for negative keywords
                            for keyword in self.negative_keywords:
                                if keyword in full_text:
                                    catalyst_score -= 15
                        
                        return {
                            'symbol': symbol,
                            'news_count': len(news_items),
                            'catalyst_score': catalyst_score,
                            'has_catalyst': catalyst_score >= 20,
                            'key_headlines': key_headlines,
                            'latest_news_time': news_items[0].get('datetime') if news_items else None
                        }
            
            return {
                'symbol': symbol,
                'news_count': 0,
                'catalyst_score': 0,
                'has_catalyst': False,
                'key_headlines': [],
                'latest_news_time': None
            }
            
        except Exception as e:
            self.logger.error(f"Error scanning news for {symbol}: {str(e)}")
            return None
    
    def scan_watchlist_news(self, symbols: List[str]) -> List[Dict]:
        """Scan news for multiple symbols"""
        results = []
        
        for symbol in symbols:
            news_data = self.scan_symbol_news(symbol)
            if news_data and news_data['has_catalyst']:
                results.append(news_data)
        
        # Sort by catalyst score
        results.sort(key=lambda x: x['catalyst_score'], reverse=True)
        return results
    
    def format_news_alert(self, news_data: Dict) -> str:
        """Format news data for alerts"""
        output = f"📰 NEWS CATALYST: {news_data['symbol']}\n"
        output += f"Score: {news_data['catalyst_score']}/100\n"
        output += f"News items: {news_data['news_count']}\n"
        
        if news_data['key_headlines']:
            output += "\nKey Headlines:\n"
            for headline in news_data['key_headlines']:
                output += f"• {headline}\n"
        
        return output