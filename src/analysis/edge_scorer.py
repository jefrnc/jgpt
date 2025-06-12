from typing import Dict, Optional, List
from datetime import datetime
from src.utils.logger import setup_logger


class EdgeScorer:
    """
    Advanced edge scoring system that combines statistical data with AI analysis
    to maximize trading edge and probability of success
    """
    
    def __init__(self):
        self.logger = setup_logger('edge_scorer')
        
        # Edge scoring weights (total = 100%)
        self.weights = {
            'flash_research_edge': 0.40,  # Historical statistics (highest weight)
            'gap_characteristics': 0.25,  # Gap size, direction, timing
            'float_dynamics': 0.20,       # Float size and turnover
            'ai_pattern_recognition': 0.10, # AI-identified patterns
            'news_catalyst': 0.05          # News timing and strength
        }
    
    def calculate_edge_score(self, gap_data: Dict, flash_analysis: Dict, 
                           float_analysis: Dict, news_analysis: Dict, 
                           ai_analysis: Optional[Dict] = None) -> Dict:
        """
        Calculate comprehensive edge score based on all available data
        Returns score (0-100) with breakdown and confidence level
        """
        try:
            symbol = gap_data.get('symbol', 'Unknown')
            self.logger.info(f"Calculating edge score for {symbol}")
            
            # Calculate individual component scores
            flash_score = self._score_flash_research_edge(flash_analysis)
            gap_score = self._score_gap_characteristics(gap_data)
            float_score = self._score_float_dynamics(float_analysis, gap_data)
            ai_score = self._score_ai_pattern_recognition(ai_analysis)
            news_score = self._score_news_catalyst(news_analysis)
            
            # Calculate weighted total score
            total_score = (
                flash_score * self.weights['flash_research_edge'] +
                gap_score * self.weights['gap_characteristics'] +
                float_score * self.weights['float_dynamics'] +
                ai_score * self.weights['ai_pattern_recognition'] +
                news_score * self.weights['news_catalyst']
            )
            
            # Calculate confidence level based on data availability
            confidence = self._calculate_confidence(
                flash_analysis, float_analysis, news_analysis, ai_analysis
            )
            
            # Generate edge classification
            edge_class = self._classify_edge(total_score, confidence)
            
            # Generate trading recommendations
            recommendations = self._generate_edge_recommendations(
                total_score, confidence, flash_analysis, gap_data
            )
            
            edge_result = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'total_edge_score': round(total_score, 1),
                'confidence_level': confidence,
                'edge_classification': edge_class,
                'component_scores': {
                    'flash_research': round(flash_score, 1),
                    'gap_characteristics': round(gap_score, 1),
                    'float_dynamics': round(float_score, 1),
                    'ai_pattern': round(ai_score, 1),
                    'news_catalyst': round(news_score, 1)
                },
                'score_weights': self.weights,
                'trading_recommendations': recommendations,
                'edge_summary': self._generate_edge_summary(total_score, confidence, flash_analysis)
            }
            
            self.logger.info(f"Edge score calculated for {symbol}: {total_score:.1f} ({edge_class})")
            return edge_result
            
        except Exception as e:
            self.logger.error(f"Error calculating edge score: {str(e)}")
            return self._create_fallback_edge_score(gap_data)
    
    def _score_flash_research_edge(self, flash_analysis: Dict) -> float:
        """Score based on Flash Research historical statistics (0-100)"""
        if not flash_analysis.get('has_flash_data', False):
            return 50.0  # Neutral score when no data
        
        score = 50.0  # Base score
        
        # Historical gap edge score (primary factor)
        gap_edge_score = flash_analysis.get('gap_edge_score', 50)
        score = gap_edge_score  # Direct use of Flash Research calculated edge
        
        # Continuation rate boost
        continuation_rate = flash_analysis.get('gap_continuation_rate', 50)
        if continuation_rate > 80:
            score += 15
        elif continuation_rate > 70:
            score += 10
        elif continuation_rate > 60:
            score += 5
        
        # Gap fill rate adjustment (lower is better for momentum)
        gap_fill_rate = flash_analysis.get('gap_fill_rate', 50)
        if gap_fill_rate < 20:
            score += 10
        elif gap_fill_rate < 30:
            score += 5
        elif gap_fill_rate > 80:
            score -= 10
        
        # Volume factor during gaps
        volume_factor = flash_analysis.get('volume_factor', 1.0)
        if volume_factor > 4.0:
            score += 8
        elif volume_factor > 2.5:
            score += 5
        elif volume_factor > 1.5:
            score += 2
        
        # Historical performance
        overall_edge = flash_analysis.get('overall_edge_score', 50)
        if overall_edge > 75:
            score += 5
        elif overall_edge > 65:
            score += 3
        
        return min(100.0, max(0.0, score))
    
    def _score_gap_characteristics(self, gap_data: Dict) -> float:
        """Score based on gap size, direction, and timing (0-100)"""
        score = 50.0
        
        gap_percent = abs(gap_data.get('gap_percent', 0))
        gap_direction = gap_data.get('gap_direction', 'UP')
        volume = gap_data.get('volume', 0)
        
        # Gap size scoring
        if gap_percent >= 30:
            score += 25  # Mega gap
        elif gap_percent >= 20:
            score += 20  # Large gap
        elif gap_percent >= 15:
            score += 15  # Significant gap
        elif gap_percent >= 10:
            score += 10  # Good gap
        elif gap_percent >= 7:
            score += 5   # Moderate gap
        elif gap_percent >= 5:
            score += 2   # Small gap
        else:
            score -= 10  # Too small
        
        # Direction bias (slight preference for gaps up in bull market)
        if gap_direction == 'UP':
            score += 2
        
        # Volume confirmation
        if volume > 1_000_000:
            score += 15
        elif volume > 500_000:
            score += 10
        elif volume > 200_000:
            score += 5
        elif volume > 100_000:
            score += 2
        elif volume < 10_000:
            score -= 5
        
        return min(100.0, max(0.0, score))
    
    def _score_float_dynamics(self, float_analysis: Dict, gap_data: Dict) -> float:
        """Score based on float characteristics and dynamics (0-100)"""
        score = 50.0
        
        if not float_analysis:
            return score
        
        # Float size impact
        if float_analysis.get('is_nanofloat', False):
            score += 30  # Nano float has highest impact
        elif float_analysis.get('is_microfloat', False):
            score += 20  # Micro float significant impact
        
        # Squeeze potential
        squeeze_potential = float_analysis.get('squeeze_potential', 0)
        if squeeze_potential > 90:
            score += 15
        elif squeeze_potential > 80:
            score += 10
        elif squeeze_potential > 70:
            score += 5
        
        # Float turnover vs volume
        float_shares = float_analysis.get('float_shares', 0)
        volume = gap_data.get('volume', 0)
        
        if float_shares > 0:
            turnover_ratio = volume / float_shares
            if turnover_ratio > 0.5:  # 50%+ of float traded
                score += 15
            elif turnover_ratio > 0.3:  # 30%+ turnover
                score += 10
            elif turnover_ratio > 0.1:  # 10%+ turnover
                score += 5
        
        return min(100.0, max(0.0, score))
    
    def _score_ai_pattern_recognition(self, ai_analysis: Optional[Dict]) -> float:
        """Score based on AI pattern recognition confidence (0-100)"""
        if not ai_analysis:
            return 50.0
        
        # Use AI setup quality as base score
        setup_quality = ai_analysis.get('setup_quality', 50)
        confidence = ai_analysis.get('confidence', 50)
        
        # Weight by AI confidence
        ai_score = (setup_quality * 0.7) + (confidence * 0.3)
        
        # Pattern type bonuses
        pattern_type = ai_analysis.get('pattern_type', '')
        if pattern_type in ['Float Squeeze', 'Statistical Edge']:
            ai_score += 10
        elif pattern_type in ['News Catalyst', 'Mega Gap']:
            ai_score += 5
        
        return min(100.0, max(0.0, ai_score))
    
    def _score_news_catalyst(self, news_analysis: Dict) -> float:
        """Score based on news catalyst strength and timing (0-100)"""
        score = 50.0
        
        if not news_analysis.get('has_catalyst', False):
            return score
        
        catalyst_strength = news_analysis.get('catalyst_strength', 0)
        catalyst_type = news_analysis.get('catalyst_type', 'Unknown')
        
        # Base catalyst score
        score = catalyst_strength
        
        # Catalyst type bonuses
        if catalyst_type == 'Strong':
            score += 10
        elif catalyst_type == 'Moderate':
            score += 5
        
        return min(100.0, max(0.0, score))
    
    def _calculate_confidence(self, flash_analysis: Dict, float_analysis: Dict, 
                            news_analysis: Dict, ai_analysis: Optional[Dict]) -> str:
        """Calculate confidence level based on data availability and quality"""
        confidence_score = 0
        
        # Flash Research data (highest impact on confidence)
        if flash_analysis.get('has_flash_data', False):
            total_gaps = flash_analysis.get('total_gaps_analyzed', 0)
            if total_gaps > 50:
                confidence_score += 40
            elif total_gaps > 20:
                confidence_score += 30
            elif total_gaps > 10:
                confidence_score += 20
            else:
                confidence_score += 10
        
        # Float data availability
        if float_analysis and float_analysis.get('float_shares', 0) > 0:
            confidence_score += 20
        
        # AI analysis availability
        if ai_analysis and ai_analysis.get('confidence', 0) > 60:
            confidence_score += 20
        elif ai_analysis:
            confidence_score += 10
        
        # News data
        if news_analysis.get('has_catalyst', False):
            confidence_score += 10
        
        # Volume data quality
        confidence_score += 10  # Always have volume data from gap
        
        if confidence_score >= 80:
            return "Very High"
        elif confidence_score >= 60:
            return "High"
        elif confidence_score >= 40:
            return "Medium"
        else:
            return "Low"
    
    def _classify_edge(self, score: float, confidence: str) -> str:
        """Classify the overall edge level"""
        
        # Adjust score based on confidence
        adjusted_score = score
        if confidence == "Very High":
            adjusted_score *= 1.0
        elif confidence == "High":
            adjusted_score *= 0.95
        elif confidence == "Medium":
            adjusted_score *= 0.85
        else:  # Low confidence
            adjusted_score *= 0.7
        
        if adjusted_score >= 85:
            return "Exceptional Edge"
        elif adjusted_score >= 75:
            return "Strong Edge"
        elif adjusted_score >= 65:
            return "Good Edge"
        elif adjusted_score >= 55:
            return "Modest Edge"
        elif adjusted_score >= 45:
            return "Neutral"
        else:
            return "Negative Edge"
    
    def _generate_edge_recommendations(self, score: float, confidence: str, 
                                     flash_analysis: Dict, gap_data: Dict) -> List[str]:
        """Generate specific trading recommendations based on edge analysis"""
        recommendations = []
        
        # Score-based recommendations
        if score >= 80:
            recommendations.append("High probability setup - consider larger position size")
            recommendations.append("Strong statistical backing supports aggressive entry")
        elif score >= 70:
            recommendations.append("Good edge detected - standard position sizing appropriate")
        elif score >= 60:
            recommendations.append("Modest edge - use conservative position sizing")
        else:
            recommendations.append("Limited edge - consider passing or very small position")
        
        # Flash Research specific recommendations
        if flash_analysis.get('has_flash_data', False):
            continuation_rate = flash_analysis.get('gap_continuation_rate', 50)
            gap_fill_rate = flash_analysis.get('gap_fill_rate', 50)
            
            if continuation_rate > 75:
                recommendations.append(f"Strong {continuation_rate:.0f}% historical continuation rate")
            
            if gap_fill_rate < 30:
                recommendations.append("Low gap fill tendency supports momentum plays")
            elif gap_fill_rate > 80:
                recommendations.append("High gap fill risk - watch for reversal")
        
        # Confidence-based recommendations
        if confidence in ["Very High", "High"]:
            recommendations.append("High confidence in analysis - reliable data backing")
        elif confidence == "Medium":
            recommendations.append("Moderate confidence - monitor carefully")
        else:
            recommendations.append("Low confidence - trade with extreme caution")
        
        return recommendations
    
    def _generate_edge_summary(self, score: float, confidence: str, flash_analysis: Dict) -> str:
        """Generate concise edge summary for alerts"""
        edge_class = self._classify_edge(score, confidence)
        
        if flash_analysis.get('has_flash_data', False):
            flash_score = flash_analysis.get('gap_edge_score', 50)
            continuation_rate = flash_analysis.get('gap_continuation_rate', 50)
            
            summary = f"{edge_class} (Score: {score:.0f}/100, Flash: {flash_score}/100, Cont: {continuation_rate:.0f}%)"
        else:
            summary = f"{edge_class} (Score: {score:.0f}/100, Confidence: {confidence})"
        
        return summary
    
    def _create_fallback_edge_score(self, gap_data: Dict) -> Dict:
        """Create fallback edge score when calculation fails"""
        return {
            'symbol': gap_data.get('symbol', 'Unknown'),
            'timestamp': datetime.now().isoformat(),
            'total_edge_score': 50.0,
            'confidence_level': 'Low',
            'edge_classification': 'Analysis Error',
            'component_scores': {
                'flash_research': 50.0,
                'gap_characteristics': 50.0,
                'float_dynamics': 50.0,
                'ai_pattern': 50.0,
                'news_catalyst': 50.0
            },
            'trading_recommendations': ['Analysis error - use standard risk management'],
            'edge_summary': 'Edge analysis unavailable'
        }