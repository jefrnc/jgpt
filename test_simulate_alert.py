#!/usr/bin/env python3
"""
Simular gap real y enviar alerta para test completo
"""

import asyncio
from src.alerts.telegram_bot import TelegramAlertBot
from src.utils.logger import setup_logger


async def simulate_real_gap():
    logger = setup_logger('simulate_gap')
    
    logger.info("=== Simulando Gap Real para Test ===")
    
    bot = TelegramAlertBot()
    
    if not bot.enabled:
        logger.error("Bot no habilitado!")
        return
    
    # Simular varios gaps como si fueran reales
    simulated_gaps = [
        {
            'symbol': 'SOFI',
            'gap_direction': 'UP',
            'gap_percent': 18.5,
            'previous_close': 12.40,
            'current_price': 14.69,
            'volume': 3200000
        },
        {
            'symbol': 'PLTR',
            'gap_direction': 'DOWN',
            'gap_percent': -12.3,
            'previous_close': 28.50,
            'current_price': 24.99,
            'volume': 1850000
        }
    ]
    
    logger.info(f"Enviando {len(simulated_gaps)} alertas simuladas...")
    
    for gap in simulated_gaps:
        logger.info(f"Enviando alerta para {gap['symbol']} gap {gap['gap_direction']} {abs(gap['gap_percent'])}%")
        message = bot.format_gap_alert(gap)
        await bot.send_alert(message)
        await asyncio.sleep(2)  # Pausa entre mensajes
    
    logger.info("✅ Test completado! Deberías haber recibido las alertas en Telegram")


def main():
    asyncio.run(simulate_real_gap())


if __name__ == "__main__":
    main()