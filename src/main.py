#!/usr/bin/env python3
"""
Main entry point for the Small-Cap Trading Edge System
"""

import os
import sys
import time
import argparse
import asyncio
from datetime import datetime
from typing import Dict
import schedule
from dotenv import load_dotenv
from src.scanners.gap_scanner import GapScanner
from src.scanners.float_screener import FloatScreener
from src.alerts.telegram_bot import TelegramAlertBot
from src.analysis.pattern_analyzer import PatternAnalyzer
from src.analysis.playbook_generator import PlaybookGenerator
from src.analysis.edge_scorer import EdgeScorer
from src.api.flash_research_client import FlashResearchClient
from src.api.openai_client import OpenAIClient
from src.utils.logger import setup_logger
from src.utils.market_hours import MarketHoursManager

load_dotenv()


class TradingBot:
    def __init__(self, debug=False):
        self.logger = setup_logger('main', 'DEBUG' if debug else 'INFO')
        self.gap_scanner = GapScanner()
        self.float_screener = FloatScreener()
        self.telegram_bot = TelegramAlertBot()
        self.pattern_analyzer = PatternAnalyzer()
        self.playbook_generator = PlaybookGenerator()
        self.edge_scorer = EdgeScorer()
        self.flash_client = FlashResearchClient(use_scraper=True)
        self.openai_client = OpenAIClient()
        self.market_hours = MarketHoursManager()
        self.scan_interval = int(os.getenv('SCANNER_INTERVAL', 300))  # 5 minutes default
        self.is_running = True
        self.alerts_enabled = True
        self.float_screening_enabled = True
        self.ai_analysis_enabled = True
        self.flash_research_enabled = True
        
    def run_gap_scan(self):
        """Execute gap scanner"""
        self.logger.info("Starting gap scan...")
        
        try:
            # Check if we should scan now
            if not self.market_hours.should_scan_now():
                session_info = self.market_hours.get_session_info()
                self.logger.info(f"⏸️  Scanner paused - Market {session_info['session_type']}")
                self.logger.info(f"⏰ Next session: {session_info.get('next_session', 'Unknown')}")
                return
            
            # Get current session info
            session_info = self.market_hours.get_session_info()
            self.logger.info(f"📊 Scanning during {session_info['session_type']} session")
            
            # Get symbols to scan
            symbols = self.gap_scanner.get_market_movers()
            
            # Run gap scan
            gap_results = self.gap_scanner.scan_watchlist(symbols)
            
            # Run enhanced analysis on gap results
            enhanced_results = []
            if gap_results:
                self.logger.info("🔍 Running enhanced analysis (Float + AI) on gap stocks...")
                
                for gap in gap_results:
                    try:
                        # Run comprehensive analysis with Flash Research + AI
                        enhanced_gap = self._run_comprehensive_analysis(gap)
                        enhanced_results.append(enhanced_gap)
                        
                        self.logger.info(f"✅ Analysis completed for {gap['symbol']}: Score {enhanced_gap.get('total_score', 0)}/100")
                        
                    except Exception as e:
                        self.logger.warning(f"❌ Analysis failed for {gap['symbol']}: {str(e)}")
                        # Fallback to basic gap data
                        gap['total_score'] = abs(gap.get('gap_percent', 0))
                        gap['combined_score'] = gap['total_score']
                        enhanced_results.append(gap)
                
                # Sort by combined score (gap % + float score + AI score)
                enhanced_results.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
            else:
                enhanced_results = gap_results
            
            # Display results
            if enhanced_results:
                formatted = self._format_enhanced_results(enhanced_results)
                print(formatted)
                
                # Send Telegram alerts
                if self.alerts_enabled and self.telegram_bot.enabled:
                    self.logger.info("Sending enhanced Telegram alerts...")
                    asyncio.run(self._send_enhanced_alerts(enhanced_results))
            else:
                self.logger.info("No significant gaps found in this scan")
                
        except Exception as e:
            self.logger.error(f"Error during scan: {str(e)}")
    
    def _run_comprehensive_analysis(self, gap_data: Dict) -> Dict:
        """Run comprehensive analysis with Flash Research + AI"""
        symbol = gap_data['symbol']
        self.logger.info(f"🔍 Comprehensive analysis for {symbol}...")
        
        # 1. Get Flash Research data
        flash_data = None
        if self.flash_research_enabled:
            try:
                flash_data = self.flash_client.analyze_symbol(symbol)
                self.logger.info(f"📊 Flash Research data for {symbol}: {flash_data.get('source', 'unknown')}")
            except Exception as e:
                self.logger.warning(f"⚠️ Flash Research failed for {symbol}: {str(e)}")
        
        # 2. Calculate our scoring
        our_analysis = self._calculate_our_scoring(gap_data, flash_data)
        
        # 3. Get comprehensive AI analysis
        ai_result = None
        if self.ai_analysis_enabled and self.openai_client.enabled:
            try:
                ai_result = self.openai_client.analyze_gap_with_flash_research(
                    gap_data=gap_data,
                    our_analysis=our_analysis,
                    flash_research_data=flash_data
                )
                self.logger.info(f"🤖 AI analysis for {symbol}: {ai_result.get('confidence_level', 0)}% confidence")
            except Exception as e:
                self.logger.warning(f"⚠️ AI analysis failed for {symbol}: {str(e)}")
        
        # 4. Combine everything
        enhanced_gap = gap_data.copy()
        enhanced_gap.update({
            'flash_data': flash_data,
            'our_analysis': our_analysis,
            'ai_result': ai_result,
            'total_score': our_analysis.get('total_score', 50),
            'combined_score': our_analysis.get('total_score', 50),
            'telegram_message': ai_result.get('telegram_message') if ai_result else None,
            'edge_explanation': ai_result.get('edge_explanation') if ai_result else None,
            'recommended_action': ai_result.get('recommended_action') if ai_result else 'Standard approach'
        })
        
        return enhanced_gap
    
    def _calculate_our_scoring(self, gap_data: Dict, flash_data: Dict = None) -> Dict:
        """Calculate our scoring system"""
        gap_percent = abs(gap_data.get('gap_percent', 0))
        volume = gap_data.get('volume', 0)
        market_cap = gap_data.get('market_cap', 0)
        float_shares = gap_data.get('float_shares', 0)
        
        # Gap Score (25 points max)
        if gap_percent >= 20:
            gap_score = 25
        elif gap_percent >= 15:
            gap_score = 22
        elif gap_percent >= 10:
            gap_score = 18
        elif gap_percent >= 5:
            gap_score = 12
        else:
            gap_score = 5
        
        # Volume Score (20 points max)
        if volume >= 1_000_000:
            volume_score = 20
        elif volume >= 500_000:
            volume_score = 16
        elif volume >= 100_000:
            volume_score = 12
        else:
            volume_score = 8
        
        # Float Score (15 points max)
        if float_shares > 0:
            if float_shares <= 5_000_000:
                float_score = 15
            elif float_shares <= 10_000_000:
                float_score = 12
            elif float_shares <= 20_000_000:
                float_score = 9
            else:
                float_score = 6
        else:
            float_score = 8  # Default
        
        # Flash Research Score (40 points max)
        flash_score = 0
        if flash_data and flash_data.get('has_flash_data'):
            edge_score = flash_data.get('gap_edge_score', 50)
            flash_score = int((edge_score / 100) * 40)  # Convert to 40 point scale
        else:
            flash_score = 20  # Default when no Flash Research data
        
        # AI Score (10 points max) - placeholder
        ai_score = 8
        
        total_score = gap_score + volume_score + float_score + flash_score + ai_score
        
        # Build reasoning
        reasoning_parts = [
            f"Gap {gap_percent:.1f}% = {gap_score}/25 pts",
            f"Volume {volume:,} = {volume_score}/20 pts",
            f"Float {float_shares/1_000_000:.1f}M = {float_score}/15 pts"
        ]
        
        if flash_data and flash_data.get('has_flash_data'):
            continuation_rate = flash_data.get('gap_continuation_rate', 0)
            reasoning_parts.append(f"Historical Analysis {flash_data.get('gap_edge_score', 0)}/100 ({continuation_rate:.0f}% continuation) = {flash_score}/40 pts")
        else:
            reasoning_parts.append(f"No historical data = {flash_score}/40 pts (default)")
        
        reasoning = " + ".join(reasoning_parts)
        
        return {
            'total_score': total_score,
            'gap_score': gap_score,
            'volume_score': volume_score,
            'float_score': float_score,
            'flash_score': flash_score,
            'ai_score': ai_score,
            'reasoning': reasoning
        }

    def _format_enhanced_results(self, results):
        """Format results with AI analysis and float data"""
        if not results:
            return "No gaps found matching criteria."
        
        output = f"\n{'='*80}\n"
        output += f"AI-Enhanced Gap Scanner Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}\n"
        output += f"{'='*80}\n\n"
        
        for gap in results:
            output += f"Symbol: {gap['symbol']}\n"
            output += f"Gap: {gap['gap_direction']} {abs(gap['gap_percent'])}%\n"
            output += f"Price: ${gap['previous_close']:.2f} → ${gap['current_price']:.2f}\n"
            output += f"Volume: {gap['volume']:,}\n"
            output += f"Combined Score: {gap.get('combined_score', 0):.1f}\n"
            
            # Add AI pattern analysis
            if 'pattern_analysis' in gap:
                pattern = gap['pattern_analysis']
                output += f"🧠 AI Pattern: {pattern.get('pattern_type', 'Unknown')} (Q:{pattern.get('setup_quality', 0)}/100)\n"
                output += f"📚 Playbook: {pattern.get('playbook', 'N/A')[:80]}...\n"
                
                key_factors = pattern.get('key_factors', [])
                if key_factors:
                    output += f"🔑 Key Factors: {', '.join(key_factors[:3])}\n"
            
            # Add float data if available
            if 'float_data' in gap:
                float_data = gap['float_data']
                float_shares = float_data.get('float_shares', 0)
                if float_shares:
                    if float_shares < 1_000_000:
                        float_str = f"{float_shares/1000:.0f}K"
                    else:
                        float_str = f"{float_shares/1_000_000:.1f}M"
                    
                    output += f"🔍 Float: {float_str} shares ({float_data.get('float_category', 'unknown')})\n"
                    
                    if gap.get('is_microfloat'):
                        output += "🔥 MICROFLOAT DETECTED!\n"
                    if gap.get('squeeze_setup'):
                        output += "🚨 SQUEEZE SETUP!\n"
            
            output += f"{'-'*60}\n"
        
        return output
    
    async def _send_enhanced_alerts(self, results):
        """Send comprehensive alerts with Flash Research + AI analysis"""
        for gap in results[:3]:  # Top 3 only
            try:
                # Use AI-generated message if available, otherwise create fallback
                if gap.get('telegram_message'):
                    message = gap['telegram_message']
                    self.logger.info(f"📱 Sending AI-generated alert for {gap['symbol']}")
                else:
                    message = self._create_fallback_alert(gap)
                    self.logger.info(f"📱 Sending fallback alert for {gap['symbol']}")
                
                await self.telegram_bot.send_alert(message)
                await asyncio.sleep(3)  # Delay between messages
                
            except Exception as e:
                self.logger.error(f"❌ Failed to send alert for {gap['symbol']}: {str(e)}")
    
    def _create_fallback_alert(self, gap_data):
        """Create fallback alert when AI analysis is not available"""
        symbol = gap_data['symbol']
        gap_percent = gap_data.get('gap_percent', 0)
        current_price = gap_data.get('current_price', 0)
        market_cap = gap_data.get('market_cap', 0) / 1_000_000  # Convert to millions
        float_shares = gap_data.get('float_shares', 0) / 1_000_000
        total_score = gap_data.get('total_score', 0)
        
        direction_emoji = "🔥" if gap_percent > 0 else "📉"
        
        message = f"""{direction_emoji} **{symbol}** Gap {'+' if gap_percent > 0 else ''}{gap_percent:.1f}%
💰 ${current_price:.2f} | Cap: ${market_cap:.1f}M | Float: {float_shares:.1f}M
📊 Score: {total_score}/100"""
        
        # Add Flash Research data if available
        flash_data = gap_data.get('flash_data')
        if flash_data and flash_data.get('has_flash_data'):
            continuation_rate = flash_data.get('gap_continuation_rate', 0)
            fill_rate = flash_data.get('gap_fill_rate', 0)
            total_gaps = flash_data.get('total_gaps_analyzed', 0)
            edge_score = flash_data.get('gap_edge_score', 0)
            
            message += f"""

📈 **Historical Edge ({edge_score}/100):**
• {total_gaps} gaps analyzed
• {continuation_rate:.0f}% continuation rate
• {fill_rate:.0f}% gap fill rate"""
            
            # Add statistical edge explanation
            if continuation_rate > 75:
                message += f"\n• Strong momentum bias"
            elif continuation_rate > 65:
                message += f"\n• Moderate momentum bias"
            
            if fill_rate < 40:
                message += f"\n• Low gap fill tendency"
        
        # Add our analysis reasoning
        our_analysis = gap_data.get('our_analysis', {})
        if our_analysis and our_analysis.get('reasoning'):
            message += f"""

🧮 **Scoring Breakdown:**
{our_analysis['reasoning']}"""
        
        return message
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'flash_client') and self.flash_client:
                self.flash_client.close()
                self.logger.info("🔒 Flash Research client closed")
        except Exception as e:
            self.logger.warning(f"⚠️ Error closing Flash Research client: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
    
    def run_continuous(self):
        """Run scanner continuously with smart scheduling"""
        self.logger.info("🚀 Starting smart continuous scanner...")
        
        # Show initial market status
        session_info = self.market_hours.get_session_info()
        self.logger.info(f"📅 Current time: {session_info['current_time']} ({session_info['day_of_week']})")
        self.logger.info(f"📊 Market status: {session_info['session_type']}")
        
        if not session_info['is_active']:
            self.logger.info(f"⏰ Next session in {session_info['wait_time_minutes']} minutes")
        
        # Clear any existing scheduled jobs
        schedule.clear()
        
        try:
            while self.is_running:
                # Get optimal interval based on current session
                current_interval = self.market_hours.get_optimal_scan_interval()
                
                # If interval changed, reschedule
                if current_interval != self.scan_interval:
                    self.scan_interval = current_interval
                    schedule.clear()
                    schedule.every(self.scan_interval).seconds.do(self.run_gap_scan)
                    self.logger.info(f"📅 Updated scan interval to {self.scan_interval}s")
                
                # Run scan
                self.run_gap_scan()
                
                # Wait for next iteration
                self.logger.info(f"⏳ Next scan in {self.scan_interval//60} minutes")
                time.sleep(self.scan_interval)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Scanner stopped by user")
            self.is_running = False
        finally:
            self.cleanup()
    
    def run_once(self):
        """Run scanner once and exit"""
        self.run_gap_scan()
    
    def _calculate_combined_score(self, gap_data: Dict, ai_score: int) -> float:
        """Calculate combined score from gap, float, and AI analysis"""
        gap_percent = abs(gap_data.get('gap_percent', 0))
        float_score = gap_data.get('float_score', 0)
        
        # Weighted scoring: Gap (60%) + AI (30%) + Float (10%)
        combined = (gap_percent * 0.6) + (ai_score * 0.3) + (float_score * 0.1)
        
        return round(combined, 2)


def main():
    parser = argparse.ArgumentParser(description='Small-Cap Trading Edge System')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--interval', type=int, help='Scan interval in seconds')
    
    args = parser.parse_args()
    
    # Override interval if provided
    if args.interval:
        os.environ['SCANNER_INTERVAL'] = str(args.interval)
    
    # Initialize bot
    bot = TradingBot(debug=args.debug)
    
    # Run mode
    if args.once:
        bot.run_once()
    else:
        bot.run_continuous()


if __name__ == "__main__":
    main()