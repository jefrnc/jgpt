#!/usr/bin/env python3
"""
Main entry point for the Small-Cap Trading Edge System
"""

import os
import sys
import time
import argparse
from datetime import datetime
import schedule
from dotenv import load_dotenv
from src.scanners.gap_scanner import GapScanner
from src.utils.logger import setup_logger

load_dotenv()


class TradingBot:
    def __init__(self, debug=False):
        self.logger = setup_logger('main', 'DEBUG' if debug else 'INFO')
        self.gap_scanner = GapScanner()
        self.scan_interval = int(os.getenv('SCANNER_INTERVAL', 300))  # 5 minutes default
        self.is_running = True
        
    def run_gap_scan(self):
        """Execute gap scanner"""
        self.logger.info("Starting gap scan...")
        
        try:
            # Check market hours
            if self.gap_scanner.is_market_hours():
                self.logger.info("Market is open - scanning for intraday gaps")
            elif self.gap_scanner.is_premarket_hours():
                self.logger.info("Premarket hours - scanning for overnight gaps")
            else:
                self.logger.info("Market closed - waiting for next session")
                return
            
            # Get symbols to scan
            symbols = self.gap_scanner.get_market_movers()
            
            # Run scan
            results = self.gap_scanner.scan_watchlist(symbols)
            
            # Display results
            if results:
                formatted = self.gap_scanner.format_results(results)
                print(formatted)
                
                # Here we would send alerts (Telegram, etc)
                # TODO: Implement alert system
            else:
                self.logger.info("No significant gaps found in this scan")
                
        except Exception as e:
            self.logger.error(f"Error during scan: {str(e)}")
    
    def run_continuous(self):
        """Run scanner continuously"""
        self.logger.info(f"Starting continuous scanner - interval: {self.scan_interval} seconds")
        
        # Run first scan immediately
        self.run_gap_scan()
        
        # Schedule regular scans
        schedule.every(self.scan_interval).seconds.do(self.run_gap_scan)
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Scanner stopped by user")
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