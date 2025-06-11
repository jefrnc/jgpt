#!/usr/bin/env python3
"""
Test market hours manager
"""

from src.utils.market_hours import MarketHoursManager
from src.utils.logger import setup_logger


def main():
    logger = setup_logger('market_hours_test')
    
    logger.info("=== Test Market Hours Manager ===")
    
    manager = MarketHoursManager()
    
    # Get complete session info
    info = manager.get_session_info()
    
    logger.info(f"\n📅 Current Status:")
    logger.info(f"Date: {info['current_date']} ({info['day_of_week']})")
    logger.info(f"Time: {info['current_time']}")
    logger.info(f"Session: {info['session_type']}")
    logger.info(f"Active: {'✅ YES' if info['is_active'] else '❌ NO'}")
    
    logger.info(f"\n⚙️  Configuration:")
    logger.info(f"Premarket enabled: {'✅' if info['premarket_enabled'] else '❌'}")
    logger.info(f"Afterhours enabled: {'✅' if info['afterhours_enabled'] else '❌'}")
    
    if not info['is_active']:
        logger.info(f"\n⏰ Next Session:")
        logger.info(f"Starts: {info['next_session']}")
        logger.info(f"Wait time: {info['wait_time_minutes']} minutes")
    
    # Test scan decision
    should_scan = manager.should_scan_now()
    logger.info(f"\n🔍 Should scan now: {'✅ YES' if should_scan else '❌ NO'}")
    
    # Test optimal interval
    interval = manager.get_optimal_scan_interval()
    logger.info(f"📊 Optimal interval: {interval}s ({interval//60} minutes)")
    
    logger.info(f"\n💡 API Quota Conservation:")
    if should_scan:
        logger.info("✅ Scanner will run - market session active")
    else:
        logger.info("💰 Scanner paused - saving API quota")
        logger.info(f"⏳ Will resume in {info.get('wait_time_minutes', 0)} minutes")


if __name__ == "__main__":
    main()