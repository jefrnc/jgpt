#!/usr/bin/env python3
"""
Simular comportamiento en fin de semana
"""

import os
from datetime import datetime, time
from unittest.mock import patch
from src.utils.market_hours import MarketHoursManager
from src.utils.logger import setup_logger


def simulate_weekend():
    logger = setup_logger('weekend_test')
    
    logger.info("=== Simulando Fin de Semana ===")
    
    manager = MarketHoursManager()
    
    # Simular sábado 10:00 AM
    with patch.object(manager, 'get_current_time_est') as mock_time:
        # Crear datetime para sábado
        saturday_10am = datetime(2025, 6, 14, 10, 0, 0)  # Sábado
        mock_time.return_value = saturday_10am.replace(tzinfo=manager.eastern.localize(saturday_10am).tzinfo)
        
        info = manager.get_session_info()
        should_scan = manager.should_scan_now()
        interval = manager.get_optimal_scan_interval()
        
        logger.info(f"\n📅 Simulando: {info['day_of_week']} 10:00 AM")
        logger.info(f"Session: {info['session_type']}")
        logger.info(f"Should scan: {'✅ YES' if should_scan else '❌ NO'}")
        logger.info(f"Interval: {interval}s ({interval//3600} hours)")
        
        if not should_scan:
            logger.info(f"💰 API quota saved! No scanning on weekends")

def simulate_afterhours():
    logger = setup_logger('afterhours_test')
    
    logger.info("\n=== Simulando After Hours (8:30 PM) ===")
    
    manager = MarketHoursManager()
    
    # Simular miércoles 8:30 PM
    with patch.object(manager, 'get_current_time_est') as mock_time:
        wednesday_830pm = datetime(2025, 6, 11, 20, 30, 0)  # Miércoles 8:30 PM
        mock_time.return_value = wednesday_830pm.replace(tzinfo=manager.eastern.localize(wednesday_830pm).tzinfo)
        
        info = manager.get_session_info()
        should_scan = manager.should_scan_now()
        interval = manager.get_optimal_scan_interval()
        
        logger.info(f"📅 Simulando: {info['day_of_week']} 8:30 PM")
        logger.info(f"Session: {info['session_type']}")
        logger.info(f"Should scan: {'✅ YES' if should_scan else '❌ NO'}")
        logger.info(f"Interval: {interval}s ({interval//3600} hours)")
        
        if not should_scan:
            logger.info(f"💰 API quota conserved during closed hours")

def simulate_premarket():
    logger = setup_logger('premarket_test')
    
    logger.info("\n=== Simulando Premarket (6:00 AM) ===")
    
    manager = MarketHoursManager()
    
    # Simular jueves 6:00 AM
    with patch.object(manager, 'get_current_time_est') as mock_time:
        thursday_6am = datetime(2025, 6, 12, 6, 0, 0)  # Jueves 6:00 AM
        mock_time.return_value = thursday_6am.replace(tzinfo=manager.eastern.localize(thursday_6am).tzinfo)
        
        info = manager.get_session_info()
        should_scan = manager.should_scan_now()
        interval = manager.get_optimal_scan_interval()
        
        logger.info(f"📅 Simulando: {info['day_of_week']} 6:00 AM")
        logger.info(f"Session: {info['session_type']}")
        logger.info(f"Should scan: {'✅ YES' if should_scan else '❌ NO'}")
        logger.info(f"Interval: {interval}s ({interval//60} minutes)")
        
        if should_scan:
            logger.info(f"🔥 Prime time para overnight gaps!")

def main():
    simulate_weekend()
    simulate_afterhours() 
    simulate_premarket()
    
    logger = setup_logger('summary')
    logger.info(f"\n💡 Resumen de Optimización:")
    logger.info(f"✅ Pausa automática en fines de semana")
    logger.info(f"✅ Intervalos largos (1 hora) cuando mercado cerrado")
    logger.info(f"✅ Intervalos cortos (5 min) en premarket")
    logger.info(f"✅ Conservación de API quota inteligente")

if __name__ == "__main__":
    main()