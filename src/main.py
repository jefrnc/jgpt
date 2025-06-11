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
from src.alerts.telegram_bot import TelegramAlertBot
from src.utils.logger import setup_logger
from src.utils.market_hours import MarketHoursManager

load_dotenv()


class TradingBot:
    def __init__(self, debug=False):
        self.logger = setup_logger('main', 'DEBUG' if debug else 'INFO')
        self.gap_scanner = GapScanner()
        self.telegram_bot = TelegramAlertBot()
        self.market_hours = MarketHoursManager()
        self.scan_interval = int(os.getenv('SCANNER_INTERVAL', 300))  # 5 minutes default
        self.is_running = True
        self.alerts_enabled = True
        
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
            
            # Run scan
            results = self.gap_scanner.scan_watchlist(symbols)
            
            # Display results
            if results:
                formatted = self.gap_scanner.format_results(results)
                print(formatted)
                
                # Send Telegram alerts
                if self.alerts_enabled and self.telegram_bot.enabled:
                    self.logger.info("Sending Telegram alerts...")
                    asyncio.run(self.telegram_bot.send_gap_alerts(results))
            else:
                self.logger.info("No significant gaps found in this scan")
                
        except Exception as e:
            self.logger.error(f"Error during scan: {str(e)}")
    
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