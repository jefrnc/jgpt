import os
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from src.api.finnhub_client import FinnhubClient
from src.utils.logger import setup_logger

load_dotenv()


class FloatScreener:
    def __init__(self):
        self.logger = setup_logger('float_screener')
        self.finnhub = FinnhubClient()
        
        # Load float screening parameters from .env
        self.max_microfloat = float(os.getenv('MAX_MICROFLOAT_MILLIONS', 10)) * 1_000_000
        self.max_lowfloat = float(os.getenv('MAX_LOWFLOAT_MILLIONS', 50)) * 1_000_000
        self.min_short_interest = float(os.getenv('MIN_SHORT_INTEREST_PCT', 15)) / 100
        self.min_insider_ownership = float(os.getenv('MIN_INSIDER_OWNERSHIP_PCT', 30)) / 100
        
    def screen_symbol(self, symbol: str) -> Optional[Dict]:
        """Screen a single symbol for float characteristics"""
        if not self.finnhub.enabled:
            return None
            
        try:
            float_data = self.finnhub.calculate_float_metrics(symbol)
            if not float_data:
                return None
            
            # Add screening flags
            float_data['screening_results'] = self._analyze_float_opportunity(float_data)
            
            return float_data
            
        except Exception as e:
            self.logger.error(f"Error screening {symbol}: {str(e)}")
            return None
    
    def _analyze_float_opportunity(self, float_data: Dict) -> Dict:
        """Analyze float data for trading opportunities"""
        float_shares = float_data.get('float_shares', 0)
        short_interest = float_data.get('short_interest_pct', 0) / 100 if float_data.get('short_interest_pct') else 0
        insider_ownership = float_data.get('insider_ownership_pct', 0) / 100
        
        analysis = {
            'is_microfloat': float_shares < self.max_microfloat,
            'is_lowfloat': float_shares < self.max_lowfloat,
            'high_short_interest': short_interest > self.min_short_interest,
            'high_insider_ownership': insider_ownership > self.min_insider_ownership,
            'squeeze_setup': False,
            'float_score': 0,
            'opportunity_type': [],
            'risk_factors': []
        }
        
        # Calculate opportunity score (0-100)
        score = 0
        
        # Float size scoring
        if float_shares < 5_000_000:  # Nano float
            score += 40
            analysis['opportunity_type'].append('nano_float_play')
        elif float_shares < 10_000_000:  # Micro float
            score += 30
            analysis['opportunity_type'].append('micro_float_play')
        elif float_shares < 50_000_000:  # Low float
            score += 15
            analysis['opportunity_type'].append('low_float_play')
        
        # Short interest scoring
        if short_interest > 0.4:  # >40%
            score += 25
            analysis['opportunity_type'].append('short_squeeze_candidate')
        elif short_interest > 0.25:  # >25%
            score += 15
            analysis['opportunity_type'].append('high_short_interest')
        
        # Insider ownership scoring
        if insider_ownership > 0.7:  # >70%
            score += 20
            analysis['opportunity_type'].append('insider_controlled')
        elif insider_ownership > 0.5:  # >50%
            score += 10
        
        # Squeeze setup detection
        if (analysis['is_microfloat'] and 
            analysis['high_short_interest'] and 
            analysis['high_insider_ownership']):
            analysis['squeeze_setup'] = True
            score += 15
            analysis['opportunity_type'].append('perfect_squeeze_setup')
        
        # Risk factors
        if float_shares < 1_000_000:
            analysis['risk_factors'].append('extremely_illiquid')
        if short_interest > 0.5:
            analysis['risk_factors'].append('excessive_short_interest')
        if insider_ownership > 0.9:
            analysis['risk_factors'].append('very_low_public_float')
        
        analysis['float_score'] = min(100, score)
        return analysis
    
    def screen_watchlist(self, symbols: List[str]) -> List[Dict]:
        """Screen a list of symbols for float opportunities"""
        self.logger.info(f"Screening {len(symbols)} symbols for float opportunities...")
        
        results = []
        screened_count = 0
        
        for symbol in symbols:
            float_data = self.screen_symbol(symbol)
            if float_data:
                results.append(float_data)
                screened_count += 1
                
                # Log interesting finds
                screening = float_data.get('screening_results', {})
                if screening.get('float_score', 0) > 50:
                    self.logger.info(f"🎯 High score: {symbol} - Score: {screening['float_score']}")
        
        # Sort by float score (highest first)
        results.sort(key=lambda x: x.get('screening_results', {}).get('float_score', 0), reverse=True)
        
        self.logger.info(f"Screened {screened_count} symbols, found {len(results)} with float data")
        return results
    
    def find_microfloats(self, symbols: List[str]) -> List[Dict]:
        """Find symbols with microfloat characteristics"""
        all_results = self.screen_watchlist(symbols)
        
        microfloats = [
            result for result in all_results
            if result.get('screening_results', {}).get('is_microfloat', False)
        ]
        
        return microfloats
    
    def find_squeeze_candidates(self, symbols: List[str]) -> List[Dict]:
        """Find potential short squeeze candidates"""
        all_results = self.screen_watchlist(symbols)
        
        squeeze_candidates = [
            result for result in all_results
            if result.get('screening_results', {}).get('squeeze_setup', False)
        ]
        
        return squeeze_candidates
    
    def get_float_leaders(self, symbols: List[str], min_score: int = 60) -> List[Dict]:
        """Get top float opportunities by score"""
        all_results = self.screen_watchlist(symbols)
        
        leaders = [
            result for result in all_results
            if result.get('screening_results', {}).get('float_score', 0) >= min_score
        ]
        
        return leaders[:10]  # Top 10
    
    def format_float_analysis(self, float_data: Dict) -> str:
        """Format float analysis for display"""
        symbol = float_data.get('symbol', 'N/A')
        float_shares = float_data.get('float_shares', 0)
        screening = float_data.get('screening_results', {})
        
        # Format float size
        if float_shares:
            if float_shares < 1_000_000:
                float_str = f"{float_shares/1000:.0f}K"
            else:
                float_str = f"{float_shares/1_000_000:.1f}M"
        else:
            float_str = "N/A"
        
        output = f"\n🔍 {symbol} Float Analysis:\n"
        output += f"Float: {float_str} shares\n"
        output += f"Category: {float_data.get('float_category', 'unknown')}\n"
        output += f"Score: {screening.get('float_score', 0)}/100\n"
        
        if float_data.get('short_interest_pct'):
            output += f"Short Interest: {float_data['short_interest_pct']:.1f}%\n"
        
        if float_data.get('insider_ownership_pct'):
            output += f"Insider Ownership: {float_data['insider_ownership_pct']:.1f}%\n"
        
        # Opportunities
        opportunities = screening.get('opportunity_type', [])
        if opportunities:
            output += f"Opportunities: {', '.join(opportunities)}\n"
        
        # Risk factors
        risks = screening.get('risk_factors', [])
        if risks:
            output += f"⚠️  Risks: {', '.join(risks)}\n"
        
        if screening.get('squeeze_setup'):
            output += "🚨 SQUEEZE SETUP DETECTED!\n"
        
        return output
    
    def get_float_summary(self, results: List[Dict]) -> str:
        """Get summary of float screening results"""
        if not results:
            return "No float data available."
        
        total = len(results)
        microfloats = len([r for r in results if r.get('screening_results', {}).get('is_microfloat')])
        squeeze_setups = len([r for r in results if r.get('screening_results', {}).get('squeeze_setup')])
        high_scores = len([r for r in results if r.get('screening_results', {}).get('float_score', 0) > 70])
        
        output = f"\n📊 Float Screening Summary:\n"
        output += f"Total Analyzed: {total}\n"
        output += f"Microfloats (<10M): {microfloats}\n"
        output += f"Squeeze Setups: {squeeze_setups}\n"
        output += f"High Scores (>70): {high_scores}\n"
        
        if results:
            top_symbol = results[0]
            output += f"\n🏆 Top Pick: {top_symbol['symbol']} "
            output += f"(Score: {top_symbol.get('screening_results', {}).get('float_score', 0)})\n"
        
        return output