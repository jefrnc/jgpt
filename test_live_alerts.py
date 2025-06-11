#!/usr/bin/env python3
"""
Test live del sistema completo con alertas reales
"""

import os
import asyncio
from src.main import TradingBot
from src.utils.logger import setup_logger
from dotenv import load_dotenv

load_dotenv()

async def test_live_system():
    logger = setup_logger('live_test')
    
    logger.info("=== Test Sistema Completo en Vivo ===")
    
    # Temporalmente reducir umbral para test
    original_gap = os.getenv('MIN_GAP_PERCENT', '5')
    os.environ['MIN_GAP_PERCENT'] = '1'  # 1% para capturar gaps pequeños
    
    bot = TradingBot(debug=True)
    
    logger.info("Ejecutando escaneo con umbral reducido (1%) para test...")
    logger.info("Esto debería encontrar gaps pequeños y enviar alertas reales!")
    
    # Ejecutar escaneo
    bot.run_gap_scan()
    
    # Restaurar umbral original
    os.environ['MIN_GAP_PERCENT'] = original_gap
    
    logger.info("Test completado! ¿Recibiste alertas en Telegram?")

def main():
    asyncio.run(test_live_system())

if __name__ == "__main__":
    main()