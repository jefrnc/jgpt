import os
import openai
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from src.utils.logger import setup_logger

load_dotenv()


class OpenAIClient:
    """OpenAI API client for pattern analysis and playbook generation"""
    
    def __init__(self):
        self.logger = setup_logger('openai_client')
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            self.logger.warning("OpenAI API key not found. AI analysis disabled.")
            self.enabled = False
            return
        
        # Initialize OpenAI client (new v1+ API)
        self.client = openai.OpenAI(api_key=self.api_key)
        self.enabled = True
        self.model = "gpt-4o"  # Latest GPT-4 model
        
        self.logger.info("OpenAI client initialized successfully")
    
    def analyze_trading_pattern(self, gap_data: Dict, float_data: Optional[Dict] = None, 
                              news_data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Analyze a trading setup and generate pattern classification with playbook
        """
        if not self.enabled:
            return None
        
        try:
            # Prepare data for AI analysis
            analysis_prompt = self._build_analysis_prompt(gap_data, float_data, news_data)
            
            # Call OpenAI API (new v1+ API)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": analysis_prompt
                    }
                ],
                max_tokens=800,
                temperature=0.3  # Lower temperature for more consistent analysis
            )
            
            # Parse response
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response, gap_data['symbol'])
            
        except Exception as e:
            self.logger.error(f"Error in AI pattern analysis: {str(e)}")
            return None
    
    def _get_system_prompt(self) -> str:
        """System prompt for AI pattern analysis"""
        return """
You are an expert small-cap day trading analyst specializing in premarket gap patterns and float analysis for DAY TRADING strategies.

Your job is to analyze trading setups and classify patterns based on:
- Gap percentage and direction for day trading opportunities
- Float size and characteristics for intraday momentum  
- Volume vs historical average for liquidity
- News catalysts and timing for day trading edge
- Price action context for short-term moves

IMPORTANT: Focus on DAY TRADING setups. Do NOT provide entry/exit signals or price targets. Focus on:
1. Pattern classification for day trading
2. Setup quality assessment for intraday moves
3. Educational playbook description for day traders
4. Historical context for same-day patterns

Respond in this exact JSON format:
{
  "pattern_type": "Gap & Go" | "Float Squeeze" | "News Catalyst" | "Breakout" | "Other",
  "confidence": 0-100,
  "setup_quality": 0-100,
  "playbook": "Brief educational description of the pattern and what typically happens for day traders",
  "key_factors": ["factor1", "factor2", "factor3"],
  "risk_level": "Low" | "Medium" | "High",
  "similar_setups": "Historical reference if applicable for day trading"
}
"""
    
    def _build_analysis_prompt(self, gap_data: Dict, float_data: Optional[Dict], 
                             news_data: Optional[Dict]) -> str:
        """Build analysis prompt with all available data"""
        
        symbol = gap_data['symbol']
        gap_percent = gap_data['gap_percent']
        gap_direction = gap_data['gap_direction']
        current_price = gap_data['current_price']
        previous_close = gap_data['previous_close']
        volume = gap_data['volume']
        
        prompt = f"""
TRADING SETUP ANALYSIS REQUEST

Symbol: {symbol}
Gap: {gap_direction} {abs(gap_percent):.1f}%
Price Movement: ${previous_close:.2f} → ${current_price:.2f}
Current Volume: {volume:,}
"""
        
        # Add float data if available
        if float_data:
            float_shares = float_data.get('float_shares', 0)
            if float_shares:
                float_millions = float_shares / 1_000_000
                prompt += f"""
Float Analysis:
- Float Size: {float_millions:.1f}M shares
- Category: {float_data.get('float_category', 'Unknown')}
- Market Cap: ${float_data.get('market_cap', 0):,.0f}
"""
        
        # Add news data if available
        if news_data and news_data.get('has_catalyst'):
            prompt += f"""
News Catalyst:
- Catalyst Score: {news_data['catalyst_score']}/100
- Recent Headlines: {news_data.get('key_headlines', [])}
- News Count: {news_data['news_count']}
"""
        
        prompt += """

Please analyze this setup and classify the pattern. Focus on educational value and pattern recognition rather than trading signals.
"""
        
        return prompt
    
    def _parse_ai_response(self, ai_response: str, symbol: str) -> Dict:
        """Parse AI response and return structured data"""
        try:
            # Try to extract JSON from response
            import json
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                # Add metadata
                parsed['symbol'] = symbol
                parsed['ai_analysis_timestamp'] = datetime.now().isoformat()
                
                return parsed
            else:
                # Fallback if JSON parsing fails
                return {
                    'symbol': symbol,
                    'pattern_type': 'Analysis Error',
                    'confidence': 0,
                    'setup_quality': 50,
                    'playbook': ai_response[:200] + "..." if len(ai_response) > 200 else ai_response,
                    'key_factors': ['AI parsing error'],
                    'risk_level': 'Medium',
                    'similar_setups': 'N/A'
                }
                
        except Exception as e:
            self.logger.error(f"Error parsing AI response: {str(e)}")
            return {
                'symbol': symbol,
                'pattern_type': 'Parse Error',
                'confidence': 0,
                'setup_quality': 0,
                'playbook': 'Error parsing AI analysis',
                'key_factors': ['parsing_error'],
                'risk_level': 'High',
                'similar_setups': 'N/A'
            }
    
    def get_pattern_summary(self, pattern_data: Dict) -> str:
        """Generate a concise summary for alerts"""
        if not pattern_data:
            return ""
        
        pattern_type = pattern_data.get('pattern_type', 'Unknown')
        confidence = pattern_data.get('confidence', 0)
        setup_quality = pattern_data.get('setup_quality', 0)
        
        summary = f"🧠 AI: {pattern_type} (Q:{setup_quality}/100, C:{confidence}%)"
        
        if setup_quality >= 80:
            summary = f"🔥 {summary}"
        elif setup_quality >= 60:
            summary = f"⚡ {summary}"
        
        return summary
    
    def analyze_gap_with_flash_research(self, gap_data: Dict, our_analysis: Dict, 
                                       flash_research_data: Optional[Dict] = None) -> Dict:
        """
        Comprehensive analysis combining our scoring with Flash Research data
        Returns ready-to-send Telegram message and analysis
        """
        if not self.enabled:
            return self._fallback_telegram_message(gap_data, our_analysis, flash_research_data)
        
        try:
            # Build comprehensive prompt
            prompt = self._build_flash_research_prompt(gap_data, our_analysis, flash_research_data)
            
            # Call OpenAI with comprehensive analysis
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_flash_research_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=1200,
                temperature=0.2  # Low temperature for consistent analysis
            )
            
            # Parse response
            ai_response = response.choices[0].message.content
            return self._parse_flash_research_response(ai_response, gap_data, our_analysis)
            
        except Exception as e:
            self.logger.error(f"Error in Flash Research analysis: {str(e)}")
            return self._fallback_telegram_message(gap_data, our_analysis, flash_research_data)
    
    def _get_flash_research_system_prompt(self) -> str:
        """System prompt for comprehensive Flash Research analysis"""
        return """
You are an expert small-cap day trading analyst. You receive:
1. Gap trading data (symbol, price, volume, etc.)
2. Our calculated scoring and reasoning
3. Complete Flash Research historical data

Your job is to:
1. Validate or challenge our analysis with the Flash Research data
2. Find patterns we might have missed
3. Generate a FINAL Telegram alert message in English

IMPORTANT RULES:
- Focus on DAY TRADING opportunities
- Use Flash Research data to validate/improve our scoring
- Be concise but informative for traders
- NO specific entry/exit prices - focus on edge and context
- Highlight statistical edges from Flash Research
- Explain WHY the movement matters

Respond in this exact JSON format:
{
  "telegram_message": "Complete ready-to-send Telegram message in English with emojis",
  "our_score_assessment": "agree/disagree and why",
  "key_flash_insights": ["insight1", "insight2", "insight3"],
  "recommended_action": "Strong momentum play / Caution advised / Standard gap approach",
  "confidence_level": 0-100,
  "edge_explanation": "Why this setup has statistical edge based on Flash Research data"
}
"""
    
    def _build_flash_research_prompt(self, gap_data: Dict, our_analysis: Dict, 
                                   flash_research_data: Optional[Dict]) -> str:
        """Build comprehensive prompt with all data"""
        
        symbol = gap_data['symbol']
        gap_percent = gap_data.get('gap_percent', 0)
        current_price = gap_data.get('current_price', 0)
        volume = gap_data.get('volume', 0)
        market_cap = gap_data.get('market_cap', 0)
        float_shares = gap_data.get('float_shares', 0)
        
        prompt = f"""
COMPREHENSIVE GAP ANALYSIS REQUEST

=== BASIC DATA ===
Symbol: {symbol}
Gap: {gap_percent:+.1f}%
Current Price: ${current_price:.2f}
Volume: {volume:,}
Market Cap: ${market_cap:,.0f}
Float: {float_shares:,.0f} shares ({float_shares/1_000_000:.1f}M)

=== OUR ANALYSIS & SCORING ===
Total Score: {our_analysis.get('total_score', 0)}/100
- Gap Score: {our_analysis.get('gap_score', 0)}/25
- Volume Score: {our_analysis.get('volume_score', 0)}/20  
- Float Score: {our_analysis.get('float_score', 0)}/15
- Flash Research Score: {our_analysis.get('flash_score', 0)}/40
- AI Score: {our_analysis.get('ai_score', 0)}/10

Our Reasoning:
{our_analysis.get('reasoning', 'No reasoning provided')}

=== FLASH RESEARCH DATA ==="""
        
        if flash_research_data and flash_research_data.get('has_flash_data'):
            prompt += f"""
✅ REAL FLASH RESEARCH DATA AVAILABLE:

Historical Gap Statistics:
- Edge Score: {flash_research_data.get('gap_edge_score', 0)}/100
- Continuation Rate: {flash_research_data.get('gap_continuation_rate', 0):.1f}%
- Gap Fill Rate: {flash_research_data.get('gap_fill_rate', 0):.1f}%
- Total Gaps Analyzed: {flash_research_data.get('total_gaps_analyzed', 0)}
- Average Gap Size: {flash_research_data.get('avg_gap_size', 0):.1f}%
- Statistical Edge: {flash_research_data.get('statistical_edge', 'Unknown')}
- Historical Performance: {flash_research_data.get('historical_performance', 'Unknown')}

Historical Trading Recommendations:
{chr(10).join([f'• {rec}' for rec in flash_research_data.get('trading_recommendations', [])])}

Data Source: {flash_research_data.get('source', 'unknown')}
"""
        else:
            prompt += """
❌ NO FLASH RESEARCH DATA AVAILABLE
(Using our basic scoring only)
"""
        
        prompt += f"""

=== YOUR TASK ===
1. Analyze if our scoring is accurate given the Flash Research data
2. Find any patterns or insights we missed
3. Generate a comprehensive Telegram alert in English
4. Focus on WHY this gap matters for day traders
5. Include statistical edge from Flash Research if available

Make the Telegram message informative but concise - traders need to make quick decisions!
"""
        
        return prompt
    
    def _parse_flash_research_response(self, ai_response: str, gap_data: Dict, our_analysis: Dict) -> Dict:
        """Parse AI response for Flash Research analysis"""
        try:
            import json
            import re
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                # Add metadata
                parsed['symbol'] = gap_data['symbol']
                parsed['analysis_timestamp'] = datetime.now().isoformat()
                parsed['our_original_score'] = our_analysis.get('total_score', 0)
                
                return parsed
            else:
                # Fallback - create basic telegram message
                return self._fallback_telegram_message(gap_data, our_analysis, None)
                
        except Exception as e:
            self.logger.error(f"Error parsing Flash Research response: {str(e)}")
            return self._fallback_telegram_message(gap_data, our_analysis, None)
    
    def _fallback_telegram_message(self, gap_data: Dict, our_analysis: Dict, 
                                 flash_research_data: Optional[Dict]) -> Dict:
        """Generate fallback telegram message when AI fails"""
        symbol = gap_data['symbol']
        gap_percent = gap_data.get('gap_percent', 0)
        current_price = gap_data.get('current_price', 0)
        market_cap = gap_data.get('market_cap', 0) / 1_000_000  # Convert to millions
        float_millions = gap_data.get('float_shares', 0) / 1_000_000
        total_score = our_analysis.get('total_score', 0)
        
        direction = "🔥" if gap_percent > 0 else "📉"
        
        message = f"""{direction} **{symbol}** Gap {'+' if gap_percent > 0 else ''}{gap_percent:.1f}%
💰 ${current_price:.2f} | Cap: ${market_cap:.1f}M | Float: {float_millions:.1f}M
📊 Score: {total_score}/100"""
        
        if flash_research_data and flash_research_data.get('has_flash_data'):
            continuation_rate = flash_research_data.get('gap_continuation_rate', 0)
            fill_rate = flash_research_data.get('gap_fill_rate', 0) 
            total_gaps = flash_research_data.get('total_gaps_analyzed', 0)
            
            message += f"""

📈 **Historical Edge:**
• {total_gaps} gaps analyzed
• {continuation_rate:.0f}% continuation rate
• {fill_rate:.0f}% gap fill rate"""
        
        return {
            'telegram_message': message,
            'our_score_assessment': 'AI analysis unavailable',
            'key_flash_insights': ['AI analysis failed'],
            'recommended_action': 'Standard gap approach',
            'confidence_level': 50,
            'edge_explanation': 'Basic analysis only'
        }

    def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        if not self.enabled:
            return False
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            self.logger.error(f"OpenAI connection test failed: {str(e)}")
            return False