from typing import Dict, List, Optional
from datetime import datetime
from src.utils.logger import setup_logger


class PlaybookGenerator:
    """
    Generate educational trading playbooks for different pattern types
    """
    
    def __init__(self):
        self.logger = setup_logger('playbook_generator')
        
        # Playbook templates for different patterns
        self.pattern_playbooks = {
            "Float Squeeze": {
                "description": "Low float stock with significant gap creating supply/demand imbalance",
                "typical_behavior": "Initial spike, possible pullback, then momentum continuation if volume sustains",
                "key_levels": "Gap fill level, previous resistance/support",
                "volume_importance": "Critical - low float needs volume to move significantly",
                "timing": "Best in first 30-60 minutes, watch for momentum shifts",
                "risk_factors": ["Extreme volatility", "Low liquidity", "Quick reversals"],
                "educational_notes": "Float squeezes can create explosive moves but require careful timing and risk management"
            },
            
            "News Catalyst": {
                "description": "Gap driven by specific news or catalyst event",
                "typical_behavior": "Initial reaction, consolidation, then follow-through based on news significance",
                "key_levels": "Pre-news levels, gap support/resistance",
                "volume_importance": "High volume confirms news impact and continuation potential",
                "timing": "First hour typically most volatile, watch for institutional response",
                "risk_factors": ["News interpretation", "Market sentiment", "Sector rotation"],
                "educational_notes": "News-driven gaps often see multiple waves as different market participants react"
            },
            
            "Gap & Go": {
                "description": "Classic gap setup with potential for momentum continuation",
                "typical_behavior": "Gap open, possible test of gap level, continuation on volume",
                "key_levels": "Gap fill zone, previous day's high/low, round numbers",
                "volume_importance": "Volume above average confirms strength and continuation potential",
                "timing": "First 15-30 minutes critical for direction, then hourly momentum shifts",
                "risk_factors": ["Gap fill risk", "Momentum failure", "Sector weakness"],
                "educational_notes": "Most reliable when accompanied by above-average volume and clean technical levels"
            },
            
            "Mega Gap": {
                "description": "Exceptional gap (30%+) suggesting major development or event",
                "typical_behavior": "Extreme volatility, multiple waves, profit-taking followed by reassessment",
                "key_levels": "Multiple resistance/support zones due to size of move",
                "volume_importance": "Extremely high volume expected, watch for distribution vs accumulation",
                "timing": "All day event, multiple entry/exit opportunities",
                "risk_factors": ["Extreme volatility", "Halt risk", "Overnight developments"],
                "educational_notes": "Mega gaps often create all-day momentum but require constant risk assessment"
            },
            
            "Micro Float": {
                "description": "Very small float stock with moderate gap showing early momentum",
                "typical_behavior": "Volatile price action, sensitive to small volume changes",
                "key_levels": "Previous highs/lows more important due to limited supply",
                "volume_importance": "Even small volume can create significant moves",
                "timing": "Watch for volume spikes that can accelerate moves quickly",
                "risk_factors": ["Low liquidity", "Wide spreads", "Manipulation risk"],
                "educational_notes": "Micro floats require smaller position sizes but can offer explosive potential"
            },
            
            "Standard Gap": {
                "description": "Moderate gap requiring technical confirmation for continuation",
                "typical_behavior": "Initial move, consolidation, then direction based on market factors",
                "key_levels": "Standard technical levels, moving averages, trend lines",
                "volume_importance": "Above-average volume needed to confirm move sustainability",
                "timing": "Monitor first hour, then look for technical breakouts/breakdowns",
                "risk_factors": ["Lack of catalyst", "Market conditions", "Sector performance"],
                "educational_notes": "Standard gaps rely more on technical analysis and market conditions"
            }
        }
    
    def generate_enhanced_playbook(self, pattern_analysis: Dict) -> Dict:
        """
        Generate comprehensive playbook based on pattern analysis
        """
        try:
            pattern_type = pattern_analysis.get('pattern_type', 'Standard Gap')
            symbol = pattern_analysis.get('symbol', 'Unknown')
            setup_quality = pattern_analysis.get('setup_quality', 50)
            
            # Get base playbook template
            base_playbook = self.pattern_playbooks.get(pattern_type, self.pattern_playbooks['Standard Gap'])
            
            # Generate customized playbook
            customized_playbook = self._customize_playbook(base_playbook, pattern_analysis)
            
            # Add specific observations
            observations = self._generate_observations(pattern_analysis)
            
            # Create trading considerations
            considerations = self._generate_trading_considerations(pattern_analysis)
            
            # Generate risk assessment
            risk_assessment = self._generate_risk_assessment(pattern_analysis)
            
            enhanced_playbook = {
                'symbol': symbol,
                'pattern_type': pattern_type,
                'setup_quality': setup_quality,
                'timestamp': datetime.now().isoformat(),
                
                # Core playbook content
                'description': customized_playbook['description'],
                'expected_behavior': customized_playbook['expected_behavior'],
                'key_levels': customized_playbook['key_levels'],
                'timing_considerations': customized_playbook['timing'],
                
                # Specific analysis
                'current_observations': observations,
                'trading_considerations': considerations,
                'risk_assessment': risk_assessment,
                
                # Educational content
                'educational_notes': base_playbook['educational_notes'],
                'similar_patterns': self._find_similar_patterns(pattern_analysis),
                
                # Summary for alerts
                'alert_summary': self._generate_alert_summary(pattern_analysis)
            }
            
            self.logger.info(f"Enhanced playbook generated for {symbol}: {pattern_type}")
            return enhanced_playbook
            
        except Exception as e:
            self.logger.error(f"Error generating playbook: {str(e)}")
            return self._create_fallback_playbook(pattern_analysis)
    
    def _customize_playbook(self, base_playbook: Dict, pattern_analysis: Dict) -> Dict:
        """Customize base playbook with specific analysis data"""
        
        symbol = pattern_analysis.get('symbol', 'Stock')
        gap_percent = pattern_analysis.get('gap_percent', 0)
        
        # Get analysis details
        float_analysis = pattern_analysis.get('float_analysis', {})
        news_analysis = pattern_analysis.get('news_analysis', {})
        
        customized = base_playbook.copy()
        
        # Customize description
        if float_analysis.get('is_nanofloat'):
            customized['description'] += f" {symbol} has nano float (<1M shares) amplifying move potential."
        elif float_analysis.get('is_microfloat'):
            customized['description'] += f" {symbol} has micro float amplifying volatility."
        
        if news_analysis.get('has_catalyst'):
            customized['description'] += f" News catalyst adds fundamental driver to technical setup."
        
        # Customize expected behavior
        if abs(gap_percent) >= 20:
            customized['expected_behavior'] = "Extreme initial volatility expected, " + customized['typical_behavior']
        else:
            customized['expected_behavior'] = customized['typical_behavior']
        
        return customized
    
    def _generate_observations(self, pattern_analysis: Dict) -> List[str]:
        """Generate specific observations about current setup"""
        observations = []
        
        gap_percent = pattern_analysis.get('gap_percent', 0)
        float_analysis = pattern_analysis.get('float_analysis', {})
        news_analysis = pattern_analysis.get('news_analysis', {})
        setup_quality = pattern_analysis.get('setup_quality', 50)
        
        # Gap observations
        if abs(gap_percent) >= 30:
            observations.append(f"Exceptional {abs(gap_percent):.1f}% gap indicates major development")
        elif abs(gap_percent) >= 15:
            observations.append(f"Significant {abs(gap_percent):.1f}% gap shows strong momentum")
        else:
            observations.append(f"Moderate {abs(gap_percent):.1f}% gap requires confirmation")
        
        # Float observations
        if float_analysis.get('is_nanofloat'):
            float_shares = float_analysis.get('float_shares', 0) / 1000
            observations.append(f"Nano float ({float_shares:.0f}K shares) creates explosive potential")
        elif float_analysis.get('is_microfloat'):
            float_shares = float_analysis.get('float_shares', 0) / 1_000_000
            observations.append(f"Micro float ({float_shares:.1f}M shares) amplifies moves")
        
        # News observations
        if news_analysis.get('has_catalyst'):
            catalyst_type = news_analysis.get('catalyst_type', 'Unknown')
            observations.append(f"{catalyst_type} news catalyst provides fundamental support")
        
        # Quality observation
        if setup_quality >= 80:
            observations.append("High quality setup with multiple confirming factors")
        elif setup_quality >= 60:
            observations.append("Solid setup with good risk/reward characteristics")
        else:
            observations.append("Moderate setup requiring careful risk management")
        
        return observations
    
    def _generate_trading_considerations(self, pattern_analysis: Dict) -> List[str]:
        """Generate specific trading considerations"""
        considerations = []
        
        pattern_type = pattern_analysis.get('pattern_type', 'Standard Gap')
        float_analysis = pattern_analysis.get('float_analysis', {})
        gap_percent = pattern_analysis.get('gap_percent', 0)
        
        # Pattern-specific considerations
        if pattern_type == "Float Squeeze":
            considerations.append("Position size carefully due to low liquidity")
            considerations.append("Monitor Level 2 for thin order book areas")
            
        elif pattern_type == "News Catalyst":
            considerations.append("Watch for additional news developments")
            considerations.append("Monitor sector response to gauge sustainability")
            
        elif pattern_type == "Mega Gap":
            considerations.append("Expect multiple waves of volatility")
            considerations.append("Consider scaling in/out of positions")
            
        # Float-based considerations
        if float_analysis.get('is_nanofloat'):
            considerations.append("Use smaller position sizes due to extreme volatility")
            considerations.append("Expect wide bid/ask spreads")
        
        # Gap-based considerations
        if abs(gap_percent) >= 20:
            considerations.append("High volatility expected - adjust position sizing")
        
        considerations.append("Set alerts for key technical levels")
        considerations.append("Monitor overall market sentiment")
        
        return considerations
    
    def _generate_risk_assessment(self, pattern_analysis: Dict) -> Dict:
        """Generate comprehensive risk assessment"""
        
        risk_level = pattern_analysis.get('risk_level', 'Medium')
        pattern_type = pattern_analysis.get('pattern_type', 'Standard Gap')
        float_analysis = pattern_analysis.get('float_analysis', {})
        
        risk_factors = []
        
        # Pattern-specific risks
        if pattern_type == "Float Squeeze":
            risk_factors.extend(["Low liquidity", "Extreme volatility", "Quick reversals"])
        elif pattern_type == "News Catalyst":
            risk_factors.extend(["News interpretation risk", "Sector sentiment"])
        elif pattern_type == "Mega Gap":
            risk_factors.extend(["Extreme volatility", "Halt risk", "Overnight gaps"])
        
        # Float-specific risks
        if float_analysis.get('is_nanofloat'):
            risk_factors.extend(["Manipulation risk", "Wide spreads"])
        
        # General risks
        risk_factors.extend(["Market conditions", "Gap fill potential"])
        
        return {
            'overall_risk': risk_level,
            'primary_risks': risk_factors[:3],  # Top 3 risks
            'risk_mitigation': [
                "Use appropriate position sizing",
                "Set stop losses before entry",
                "Monitor volume for confirmation",
                "Watch for momentum shifts"
            ]
        }
    
    def _find_similar_patterns(self, pattern_analysis: Dict) -> str:
        """Find similar historical patterns for educational context"""
        
        pattern_type = pattern_analysis.get('pattern_type', 'Standard Gap')
        
        similar_patterns = {
            "Float Squeeze": "Similar to micro-cap momentum plays like IMPP, PROG, ATER during their major runs",
            "News Catalyst": "Comparable to biotech FDA approvals or tech earnings surprises",
            "Gap & Go": "Classic setup seen in quality small-caps during sector rotation",
            "Mega Gap": "Reminiscent of major catalyst plays like DWAC, GME during peak momentum",
            "Micro Float": "Similar to other sub-5M float runners during momentum phases"
        }
        
        return similar_patterns.get(pattern_type, "Standard gap pattern seen regularly in small-cap trading")
    
    def _generate_alert_summary(self, pattern_analysis: Dict) -> str:
        """Generate concise summary for Telegram alerts"""
        
        pattern_type = pattern_analysis.get('pattern_type', 'Gap')
        setup_quality = pattern_analysis.get('setup_quality', 50)
        confidence = pattern_analysis.get('confidence', 50)
        
        # Add quality indicators
        if setup_quality >= 80:
            quality_emoji = "🔥"
        elif setup_quality >= 60:
            quality_emoji = "⚡"
        else:
            quality_emoji = "📊"
        
        summary = f"{quality_emoji} {pattern_type} Setup (Q:{setup_quality}/100)"
        
        # Add key characteristics
        float_analysis = pattern_analysis.get('float_analysis', {})
        if float_analysis.get('is_nanofloat'):
            summary += " • Nano Float"
        elif float_analysis.get('is_microfloat'):
            summary += " • Micro Float"
        
        news_analysis = pattern_analysis.get('news_analysis', {})
        if news_analysis.get('has_catalyst'):
            summary += " • News Catalyst"
        
        return summary
    
    def _create_fallback_playbook(self, pattern_analysis: Dict) -> Dict:
        """Create fallback playbook when generation fails"""
        return {
            'symbol': pattern_analysis.get('symbol', 'Unknown'),
            'pattern_type': 'Analysis Error',
            'setup_quality': 50,
            'description': 'Gap detected but detailed analysis unavailable',
            'expected_behavior': 'Monitor for volume and momentum confirmation',
            'key_levels': 'Gap fill level, previous support/resistance',
            'current_observations': ['Gap detected', 'Analysis temporarily unavailable'],
            'trading_considerations': ['Use standard gap trading rules', 'Monitor volume'],
            'risk_assessment': {
                'overall_risk': 'Medium',
                'primary_risks': ['Analysis incomplete', 'Standard gap risks'],
                'risk_mitigation': ['Conservative position sizing', 'Standard risk management']
            },
            'alert_summary': '📊 Gap Setup (Analysis Limited)'
        }
    
    def get_pattern_statistics(self) -> Dict:
        """Get statistics about pattern types for analysis"""
        return {
            'supported_patterns': list(self.pattern_playbooks.keys()),
            'pattern_count': len(self.pattern_playbooks),
            'last_updated': datetime.now().isoformat()
        }