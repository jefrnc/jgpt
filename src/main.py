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
import schedule
from dotenv import load_dotenv
from src.scanners.gap_scanner import GapScanner
from src.scanners.float_screener import FloatScreener
from src.alerts.telegram_bot import TelegramAlertBot
from src.utils.logger import setup_logger
from src.utils.market_hours import MarketHoursManager

load_dotenv()


class TradingBot:
    def __init__(self, debug=False):
        self.logger = setup_logger('main', 'DEBUG' if debug else 'INFO')
        self.gap_scanner = GapScanner()
        self.float_screener = FloatScreener()
        self.telegram_bot = TelegramAlertBot()
        self.market_hours = MarketHoursManager()
        self.scan_interval = int(os.getenv('SCANNER_INTERVAL', 300))  # 5 minutes default
        self.is_running = True
        self.alerts_enabled = True
        self.float_screening_enabled = True
        
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
            
            # Run float screening on gap results if enabled
            enhanced_results = []
            if gap_results and self.float_screening_enabled:
                self.logger.info("🔍 Running float analysis on gap stocks...")
                gap_symbols = [gap['symbol'] for gap in gap_results]
                
                for gap in gap_results:
                    # Add float data to gap result
                    float_data = self.float_screener.screen_symbol(gap['symbol'])
                    if float_data:
                        gap['float_data'] = float_data
                        gap['float_score'] = float_data.get('screening_results', {}).get('float_score', 0)
                        gap['is_microfloat'] = float_data.get('screening_results', {}).get('is_microfloat', False)
                        gap['squeeze_setup'] = float_data.get('screening_results', {}).get('squeeze_setup', False)
                    enhanced_results.append(gap)
                
                # Sort by combined score (gap % + float score)
                enhanced_results.sort(key=lambda x: (
                    abs(x.get('gap_percent', 0)) + x.get('float_score', 0) * 0.1
                ), reverse=True)
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
    
    def _format_enhanced_results(self, results):
        """Format results with float data"""
        if not results:
            return "No gaps found matching criteria."
        
        output = f"\n{'='*70}\n"
        output += f"Enhanced Gap + Float Scanner Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}\n"
        output += f"{'='*70}\n\n"
        
        for gap in results:
            output += f"Symbol: {gap['symbol']}\n"
            output += f"Gap: {gap['gap_direction']} {abs(gap['gap_percent'])}%\n"
            output += f"Price: ${gap['previous_close']:.2f} → ${gap['current_price']:.2f}\n"
            output += f"Volume: {gap['volume']:,}\n"
            
            # Add float data if available
            if 'float_data' in gap:
                float_data = gap['float_data']
                float_shares = float_data.get('float_shares', 0)
                if float_shares:
                    if float_shares < 1_000_000:
                        float_str = f"{float_shares/1000:.0f}K"
                    else:
                        float_str = f"{float_shares/1_000_000:.1f}M"
                    
                    output += f"Float: {float_str} shares ({float_data.get('float_category', 'unknown')})\n"
                    output += f"Float Score: {gap.get('float_score', 0)}/100\n"
                    
                    if gap.get('is_microfloat'):
                        output += "🔥 MICROFLOAT!\n"
                    if gap.get('squeeze_setup'):
                        output += "🚨 SQUEEZE SETUP!\n"
            
            output += f"{'-'*50}\n"
        
        return output
    
    async def _send_enhanced_alerts(self, results):
        """Send enhanced alerts with float data"""
        for gap in results[:3]:  # Top 3 only
            # Create enhanced message
            message = self._format_enhanced_alert(gap)
            await self.telegram_bot.send_alert(message)
            await asyncio.sleep(2)  # Delay between messages
    
    def _format_enhanced_alert(self, gap_data):
        """Format enhanced alert with float information"""
        direction_emoji = "🟢" if gap_data['gap_direction'] == 'UP' else "🔴"
        gap_percent = abs(gap_data['gap_percent'])
        
        # Determine alert level
        if gap_percent >= 20:
            alert_emoji = "🚨🚨🚨"
            alert_text = "MEGA GAP!"
        elif gap_percent >= 10:
            alert_emoji = "🔥🔥"
            alert_text = "HOT GAP!"
        else:
            alert_emoji = "📊"
            alert_text = "Gap Alert"
        
        # Check for float enhancement
        if gap_data.get('is_microfloat'):
            alert_emoji = "🔥🚨🔥"
            alert_text = "MICROFLOAT GAP!"
        elif gap_data.get('squeeze_setup'):
            alert_emoji = "🚨💥🚨"
            alert_text = "SQUEEZE + GAP!"
        
        message = (
            f"{alert_emoji} *{alert_text}* {alert_emoji}\n\n"
            f"{direction_emoji} *${gap_data['symbol']}* {direction_emoji}\n"
            f"Gap: *{gap_data['gap_direction']} {gap_percent:.1f}%*\n"
            f"Precio: ${gap_data['previous_close']:.2f} → ${gap_data['current_price']:.2f}\n"
            f"Volumen: {gap_data['volume']:,}\n"
        )
        
        # Add float information if available
        if 'float_data' in gap_data:
            float_data = gap_data['float_data']
            float_shares = float_data.get('float_shares', 0)
            
            if float_shares:
                if float_shares < 1_000_000:
                    float_str = f"{float_shares/1000:.0f}K"
                else:
                    float_str = f"{float_shares/1_000_000:.1f}M"
                
                message += f"🔍 Float: {float_str} shares\n"
                message += f"📊 Float Score: {gap_data.get('float_score', 0)}/100\n"
                
                if gap_data.get('is_microfloat'):
                    message += "🔥 *MICROFLOAT DETECTED!*\n"
                if gap_data.get('squeeze_setup'):
                    message += "🚨 *SQUEEZE SETUP!*\n"
        
        # Add potential setup info
        if gap_percent >= 10 or gap_data.get('float_score', 0) > 70:
            message += "\n💡 *Setup Potencial:* Enhanced Gap & Go\n"
            multiplier = 1.1 if gap_data.get('is_microfloat') else 1.05
            message += f"🎯 Target: ${gap_data['current_price'] * multiplier:.2f}\n"
            message += f"🛑 Stop: ${gap_data['current_price'] * 0.95:.2f}\n"
            
        message += f"\n⏰ {datetime.now().strftime('%H:%M:%S ET')}"
        
        return message
    
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
    
    def run_once(self):
        """Run scanner once and exit"""
        self.run_gap_scan()


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