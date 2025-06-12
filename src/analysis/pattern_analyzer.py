from typing import Dict, List, Optional, Tuple
from datetime import datetime
import asyncio
from src.api.openai_client import OpenAIClient
from src.api.flash_research_client import FlashResearchClient
from src.scanners.news_scanner import NewsScanner
from src.utils.logger import setup_logger


class PatternAnalyzer:
    """
    AI-powered pattern analyzer for small-cap trading setups
    """
    
    def __init__(self):
        self.logger = setup_logger('pattern_analyzer')
        self.openai_client = OpenAIClient()
        self.news_scanner = NewsScanner()
        self.flash_research = FlashResearchClient()
        
        # Pattern thresholds
        self.microfloat_threshold = 5_000_000  # 5M shares
        self.nanofloat_threshold = 1_000_000   # 1M shares
        self.high_gap_threshold = 15.0         # 15%
        self.mega_gap_threshold = 30.0         # 30%
    
    def analyze_gap_setup(self, gap_data: Dict, float_data: Optional[Dict] = None) -> Dict:
        """
        Comprehensive analysis of a gap trading setup
        """
        try:
            # Get symbol info
            symbol = gap_data['symbol']
            gap_percent = abs(gap_data['gap_percent'])
            
            # Get news data
            news_data = self.news_scanner.scan_symbol_news(symbol, hours_back=48)
            
            # Get Flash Research enhanced statistics
            flash_data = None
            try:
                flash_data = self.flash_research.get_enhanced_analysis(symbol)
                if flash_data and 'error' not in flash_data:
                    self.logger.info(f"Flash Research data obtained for {symbol}")
                else:
                    flash_data = None
                    self.logger.warning(f"Flash Research data unavailable for {symbol}")
            except Exception as e:
                self.logger.warning(f"Flash Research error for {symbol}: {str(e)}")
                flash_data = None
            
            # Classify pattern type first (local analysis)
            pattern_classification = self._classify_pattern_local(gap_data, float_data, news_data, flash_data)
            
            # Get AI analysis if enabled
            ai_analysis = None
            if self.openai_client.enabled:
                ai_analysis = self.openai_client.analyze_trading_pattern(
                    gap_data, float_data, news_data
                )
            
            # Combine local, AI, and Flash Research analysis
            combined_analysis = self._combine_analysis(
                pattern_classification, ai_analysis, gap_data, flash_data
            )
            
            self.logger.info(f"Pattern analysis completed for {symbol}: {combined_analysis['pattern_type']}")
            return combined_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing pattern for {gap_data.get('symbol', 'Unknown')}: {str(e)}")
            return self._create_fallback_analysis(gap_data)
    
    def _classify_pattern_local(self, gap_data: Dict, float_data: Optional[Dict], 
                              news_data: Optional[Dict], flash_data: Optional[Dict]) -> Dict:
        """
        Local pattern classification without AI
        """
        symbol = gap_data['symbol']
        gap_percent = abs(gap_data['gap_percent'])
        gap_direction = gap_data['gap_direction']
        volume = gap_data.get('volume', 0)
        
        # Analyze float characteristics
        float_analysis = self._analyze_float_characteristics(float_data)
        
        # Analyze news catalyst
        news_analysis = self._analyze_news_catalyst(news_data)
        
        # Analyze Flash Research statistics
        flash_analysis = self._analyze_flash_statistics(flash_data)
        
        # Determine primary pattern type
        pattern_type = self._determine_pattern_type(
            gap_percent, gap_direction, float_analysis, news_analysis, volume, flash_analysis
        )
        
        # Calculate setup quality score with Flash Research enhancement
        setup_quality = self._calculate_setup_quality(
            gap_percent, float_analysis, news_analysis, volume, flash_analysis
        )
        
        # Generate local playbook with Flash Research insights
        playbook = self._generate_local_playbook(
            pattern_type, gap_percent, gap_direction, float_analysis, news_analysis, flash_analysis
        )
        
        return {
            'pattern_type': pattern_type,
            'setup_quality': setup_quality,
            'playbook': playbook,
            'float_analysis': float_analysis,
            'news_analysis': news_analysis,
            'flash_analysis': flash_analysis,
            'confidence': min(setup_quality + 10, 100),  # Local confidence estimate
            'key_factors': self._extract_key_factors(gap_percent, float_analysis, news_analysis, flash_analysis),
            'risk_level': self._assess_risk_level(gap_percent, float_analysis, news_analysis, flash_analysis)
        }
    
    def _analyze_float_characteristics(self, float_data: Optional[Dict]) -> Dict:
        """Analyze float characteristics for pattern detection"""
        if not float_data:
            return {
                'category': 'Unknown',
                'is_microfloat': False,
                'is_nanofloat': False,
                'squeeze_potential': 0,
                'float_shares': 0
            }
        
        float_shares = float_data.get('float_shares', 0)
        
        is_nanofloat = float_shares < self.nanofloat_threshold
        is_microfloat = float_shares < self.microfloat_threshold
        
        # Calculate squeeze potential (0-100)
        if is_nanofloat:
            squeeze_potential = 95
        elif is_microfloat:
            squeeze_potential = 80
        elif float_shares < 10_000_000:  # 10M
            squeeze_potential = 60
        elif float_shares < 25_000_000:  # 25M
            squeeze_potential = 40
        else:
            squeeze_potential = 20
        
        return {
            'category': float_data.get('float_category', 'Unknown'),
            'is_microfloat': is_microfloat,
            'is_nanofloat': is_nanofloat,
            'squeeze_potential': squeeze_potential,
            'float_shares': float_shares
        }
    
    def _analyze_news_catalyst(self, news_data: Optional[Dict]) -> Dict:
        """Analyze news catalyst strength"""
        if not news_data or not news_data.get('has_catalyst'):
            return {
                'has_catalyst': False,
                'catalyst_strength': 0,
                'catalyst_type': 'None',
                'headline_count': 0
            }
        
        catalyst_score = news_data.get('catalyst_score', 0)
        headlines = news_data.get('key_headlines', [])
        
        # Determine catalyst strength
        if catalyst_score >= 50:
            catalyst_strength = 90
            catalyst_type = 'Strong'
        elif catalyst_score >= 30:
            catalyst_strength = 70
            catalyst_type = 'Moderate'
        elif catalyst_score >= 20:
            catalyst_strength = 50
            catalyst_type = 'Weak'
        else:
            catalyst_strength = 20
            catalyst_type = 'Minimal'
        
        return {
            'has_catalyst': True,
            'catalyst_strength': catalyst_strength,
            'catalyst_type': catalyst_type,
            'headline_count': len(headlines),
            'catalyst_score': catalyst_score
        }
    
    def _analyze_flash_statistics(self, flash_data: Optional[Dict]) -> Dict:
        """Analyze Flash Research historical statistics"""
        if not flash_data or 'error' in flash_data:
            return {
                'has_flash_data': False,
                'gap_edge_score': 50,
                'historical_performance': 'Unknown',
                'gap_continuation_rate': 50,
                'gap_fill_rate': 50,
                'volume_factor': 1.0,
                'statistical_edge': 'Insufficient data'
            }
        
        gap_stats = flash_data.get('gap_statistics', {})
        performance_metrics = flash_data.get('performance_metrics', {})
        overall_edge_score = flash_data.get('overall_edge_score', 50)
        
        # Determine historical performance category
        win_rate = performance_metrics.get('win_rate_percent', 50)
        if win_rate >= 70:
            historical_performance = 'Excellent'
        elif win_rate >= 60:
            historical_performance = 'Good'
        elif win_rate >= 50:
            historical_performance = 'Average'
        else:
            historical_performance = 'Poor'
        
        # Determine statistical edge
        continuation_rate = gap_stats.get('continuation_rate', 50)
        gap_fill_rate = gap_stats.get('gap_fill_rate', 50)
        
        if continuation_rate > 70 and gap_fill_rate < 40:
            statistical_edge = 'Strong bullish momentum'
        elif continuation_rate > 60 and gap_fill_rate < 50:
            statistical_edge = 'Moderate momentum bias'
        elif gap_fill_rate > 80:
            statistical_edge = 'Gap fill tendency'
        else:
            statistical_edge = 'Neutral statistical profile'
        
        return {
            'has_flash_data': True,
            'gap_edge_score': gap_stats.get('gap_edge_score', 50),
            'historical_performance': historical_performance,
            'gap_continuation_rate': continuation_rate,
            'gap_fill_rate': gap_fill_rate,
            'volume_factor': gap_stats.get('volume_factor', 1.0),
            'statistical_edge': statistical_edge,
            'total_gaps_analyzed': gap_stats.get('total_gaps', 0),
            'avg_gap_size': gap_stats.get('avg_gap_size', 0),
            'overall_edge_score': overall_edge_score,
            'trading_recommendations': flash_data.get('trading_recommendations', [])
        }
    
    def _determine_pattern_type(self, gap_percent: float, gap_direction: str, 
                              float_analysis: Dict, news_analysis: Dict, volume: int, flash_analysis: Dict) -> str:
        """Determine the primary pattern type"""
        
        # Priority 1: Float Squeeze (nano/micro float + significant gap)
        if (float_analysis['is_nanofloat'] and gap_percent >= 10) or \
           (float_analysis['is_microfloat'] and gap_percent >= 15):
            return "Float Squeeze"
        
        # Priority 2: News Catalyst (strong news + gap)
        if news_analysis['has_catalyst'] and news_analysis['catalyst_strength'] >= 70 and gap_percent >= 8:
            return "News Catalyst"
        
        # Priority 3: Mega Gap (30%+ gap regardless of other factors)
        if gap_percent >= self.mega_gap_threshold:
            return "Mega Gap"
        
        # Priority 4: Statistical Edge Pattern (Flash Research shows strong edge)
        if flash_analysis['has_flash_data'] and flash_analysis['gap_edge_score'] >= 75:
            if gap_percent >= 8:
                return "Statistical Edge"
        
        # Priority 5: Classic Gap & Go (good gap with decent volume)
        if gap_percent >= 10 and volume > 50000:
            return "Gap & Go"
        
        # Priority 6: Micro Float Play (small float but smaller gap)
        if float_analysis['is_microfloat'] and gap_percent >= 5:
            return "Micro Float"
        
        # Default: Standard Gap
        return "Standard Gap"
    
    def _calculate_setup_quality(self, gap_percent: float, float_analysis: Dict, 
                               news_analysis: Dict, volume: int, flash_analysis: Dict) -> int:
        """Calculate overall setup quality score (0-100)"""
        score = 0
        
        # Gap percentage contribution (0-40 points)
        if gap_percent >= 30:
            score += 40
        elif gap_percent >= 20:
            score += 35
        elif gap_percent >= 15:
            score += 30
        elif gap_percent >= 10:
            score += 25
        elif gap_percent >= 7:
            score += 20
        elif gap_percent >= 5:
            score += 15
        else:
            score += 10
        
        # Float contribution (0-30 points)
        squeeze_potential = float_analysis.get('squeeze_potential', 0)
        score += int(squeeze_potential * 0.3)
        
        # News catalyst contribution (0-20 points)
        if news_analysis['has_catalyst']:
            catalyst_strength = news_analysis.get('catalyst_strength', 0)
            score += int(catalyst_strength * 0.2)
        
        # Volume contribution (0-10 points)
        if volume > 500000:
            score += 10
        elif volume > 200000:
            score += 7
        elif volume > 100000:
            score += 5
        elif volume > 50000:
            score += 3
        
        # Flash Research statistical edge contribution (0-15 points)
        if flash_analysis['has_flash_data']:
            flash_edge_score = flash_analysis.get('gap_edge_score', 50)
            continuation_rate = flash_analysis.get('gap_continuation_rate', 50)
            
            # High edge score adds points
            if flash_edge_score >= 80:
                score += 15
            elif flash_edge_score >= 70:
                score += 12
            elif flash_edge_score >= 60:
                score += 8
            elif flash_edge_score >= 55:
                score += 5
            
            # High continuation rate adds bonus
            if continuation_rate > 75:
                score += 3
            elif continuation_rate > 65:
                score += 2
        
        return min(score, 100)
    
    def _generate_local_playbook(self, pattern_type: str, gap_percent: float, 
                               gap_direction: str, float_analysis: Dict, 
                               news_analysis: Dict, flash_analysis: Dict) -> str:
        """Generate educational playbook description"""
        
        playbooks = {
            "Float Squeeze": f"Small float ({float_analysis['float_shares']/1_000_000:.1f}M) with {gap_percent:.1f}% gap. "
                           f"Limited supply can amplify moves. Watch for volume confirmation and momentum continuation.",
            
            "News Catalyst": f"News-driven {gap_percent:.1f}% gap with {news_analysis['catalyst_type'].lower()} catalyst. "
                           f"Event-based momentum often creates follow-through opportunities in first hour.",
            
            "Mega Gap": f"Exceptional {gap_percent:.1f}% gap suggests significant development. "
                      f"Large gaps often see initial profit-taking followed by potential resumption.",
            
            "Gap & Go": f"Classic {gap_percent:.1f}% {gap_direction.lower()} gap setup. "
                      f"Look for volume confirmation and clean breakout above/below gap levels.",
            
            "Micro Float": f"Micro float ({float_analysis['float_shares']/1_000_000:.1f}M shares) with {gap_percent:.1f}% move. "
                         f"Small supply can create volatile price action on modest volume.",
            
            "Statistical Edge": f"{gap_percent:.1f}% gap with strong historical edge (Score: {flash_analysis.get('gap_edge_score', 50)}/100). "
                           f"Statistics show {flash_analysis.get('statistical_edge', 'favorable profile')}.",
            
            "Standard Gap": f"{gap_percent:.1f}% gap - monitor for volume and momentum confirmation. "
                          f"Standard gap setups require technical confirmation for continuation."
        }
        
        base_playbook = playbooks.get(pattern_type, f"{gap_percent:.1f}% gap setup requiring analysis.")
        
        # Add context based on characteristics
        if float_analysis['is_nanofloat']:
            base_playbook += " Nano float (<1M) increases volatility potential."
        
        if news_analysis['has_catalyst'] and pattern_type != "News Catalyst":
            base_playbook += f" News catalyst adds momentum factor."
        
        # Add Flash Research statistical insights
        if flash_analysis['has_flash_data']:
            continuation_rate = flash_analysis.get('gap_continuation_rate', 50)
            gap_fill_rate = flash_analysis.get('gap_fill_rate', 50)
            
            if continuation_rate > 70:
                base_playbook += f" Historically shows {continuation_rate:.0f}% continuation rate."
            if gap_fill_rate < 40:
                base_playbook += f" Only {gap_fill_rate:.0f}% of gaps typically fill."
        
        return base_playbook
    
    def _extract_key_factors(self, gap_percent: float, float_analysis: Dict, 
                           news_analysis: Dict, flash_analysis: Dict) -> List[str]:
        """Extract key factors driving the setup"""
        factors = []
        
        if gap_percent >= 20:
            factors.append("Large gap")
        elif gap_percent >= 10:
            factors.append("Significant gap")
        else:
            factors.append("Moderate gap")
        
        if float_analysis['is_nanofloat']:
            factors.append("Nano float")
        elif float_analysis['is_microfloat']:
            factors.append("Micro float")
        
        if news_analysis['has_catalyst']:
            factors.append(f"{news_analysis['catalyst_type']} catalyst")
        
        # Add Flash Research statistical factors (these are the EDGE factors)
        if flash_analysis['has_flash_data']:
            edge_score = flash_analysis.get('gap_edge_score', 50)
            continuation_rate = flash_analysis.get('gap_continuation_rate', 50)
            gap_fill_rate = flash_analysis.get('gap_fill_rate', 50)
            
            if edge_score >= 75:
                factors.append("High statistical edge")
            if continuation_rate > 70:
                factors.append(f"{continuation_rate:.0f}% continuation rate")
            if gap_fill_rate < 40:
                factors.append("Low gap fill tendency")
            if flash_analysis.get('volume_factor', 1) > 2.5:
                factors.append("High volume multiplier")
        
        return factors
    
    def _assess_risk_level(self, gap_percent: float, float_analysis: Dict, 
                         news_analysis: Dict, flash_analysis: Dict) -> str:
        """Assess overall risk level"""
        risk_score = 0
        
        # Gap size increases risk
        if gap_percent >= 30:
            risk_score += 3
        elif gap_percent >= 20:
            risk_score += 2
        elif gap_percent >= 10:
            risk_score += 1
        
        # Small float increases volatility risk
        if float_analysis['is_nanofloat']:
            risk_score += 2
        elif float_analysis['is_microfloat']:
            risk_score += 1
        
        # News catalyst can add uncertainty
        if news_analysis['has_catalyst']:
            risk_score += 1
        
        # Flash Research can REDUCE risk with statistical backing
        if flash_analysis['has_flash_data']:
            edge_score = flash_analysis.get('gap_edge_score', 50)
            continuation_rate = flash_analysis.get('gap_continuation_rate', 50)
            
            # High statistical edge reduces risk
            if edge_score >= 80 and continuation_rate > 75:
                risk_score -= 2  # Strong statistical backing reduces risk
            elif edge_score >= 70:
                risk_score -= 1
        
        if risk_score >= 4:
            return "High"
        elif risk_score >= 2:
            return "Medium"
        else:
            return "Low"
    
    def _combine_analysis(self, local_analysis: Dict, ai_analysis: Optional[Dict], 
                        gap_data: Dict, flash_data: Optional[Dict]) -> Dict:
        """Combine local and AI analysis"""
        if not ai_analysis:
            # Use local analysis only
            combined = local_analysis.copy()
            combined['analysis_source'] = 'local'
            combined['symbol'] = gap_data['symbol']
            combined['timestamp'] = datetime.now().isoformat()
            return combined
        
        # Combine both analyses
        combined = {
            'symbol': gap_data['symbol'],
            'timestamp': datetime.now().isoformat(),
            'analysis_source': 'ai_enhanced',
            
            # Prefer AI for these fields
            'pattern_type': ai_analysis.get('pattern_type', local_analysis['pattern_type']),
            'playbook': ai_analysis.get('playbook', local_analysis['playbook']),
            'confidence': ai_analysis.get('confidence', local_analysis['confidence']),
            'risk_level': ai_analysis.get('risk_level', local_analysis['risk_level']),
            'similar_setups': ai_analysis.get('similar_setups', 'N/A'),
            
            # Average setup quality
            'setup_quality': int((
                ai_analysis.get('setup_quality', 0) + local_analysis['setup_quality']
            ) / 2),
            
            # Combine key factors
            'key_factors': list(set(
                ai_analysis.get('key_factors', []) + local_analysis['key_factors']
            )),
            
            # Keep local detailed analysis
            'float_analysis': local_analysis['float_analysis'],
            'news_analysis': local_analysis['news_analysis'],
            
            # Keep AI raw response
            'ai_raw': ai_analysis
        }
        
        return combined
    
    def _create_fallback_analysis(self, gap_data: Dict) -> Dict:
        """Create fallback analysis when main analysis fails"""
        return {
            'symbol': gap_data['symbol'],
            'timestamp': datetime.now().isoformat(),
            'analysis_source': 'fallback',
            'pattern_type': 'Analysis Error',
            'setup_quality': 50,
            'confidence': 25,
            'playbook': f"{abs(gap_data['gap_percent']):.1f}% gap detected. Analysis temporarily unavailable.",
            'key_factors': ['gap_detected'],
            'risk_level': 'Medium',
            'similar_setups': 'N/A'
        }