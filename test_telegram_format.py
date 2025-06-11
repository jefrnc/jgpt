#!/usr/bin/env python3
"""
Test para ver cómo se ve el formato de los mensajes de Telegram
"""

from src.alerts.telegram_bot import TelegramAlertBot
from src.utils.logger import setup_logger


def main():
    logger = setup_logger('telegram_format_test')
    
    logger.info("=== Test de Formato de Mensajes Telegram ===")
    
    bot = TelegramAlertBot()
    
    # Test different gap scenarios
    test_gaps = [
        {
            'symbol': 'SOFI',
            'gap_direction': 'UP',
            'gap_percent': 25.5,
            'previous_close': 8.50,
            'current_price': 10.67,
            'volume': 2500000
        },
        {
            'symbol': 'LCID',
            'gap_direction': 'UP',
            'gap_percent': 15.2,
            'previous_close': 4.20,
            'current_price': 4.84,
            'volume': 1800000
        },
        {
            'symbol': 'PLTR',
            'gap_direction': 'DOWN',
            'gap_percent': -8.5,
            'previous_close': 25.60,
            'current_price': 23.42,
            'volume': 980000
        },
        {
            'symbol': 'NVDA',
            'gap_direction': 'UP',
            'gap_percent': 3.2,
            'previous_close': 140.50,
            'current_price': 145.00,
            'volume': 750000
        }
    ]
    
    logger.info("\nEjemplos de mensajes que se enviarían:\n")
    
    for i, gap in enumerate(test_gaps, 1):
        message = bot.format_gap_alert(gap)
        
        print(f"═══ Ejemplo {i}: {gap['symbol']} Gap {gap['gap_direction']} {abs(gap['gap_percent'])}% ═══")
        print(message)
        print("═" * 60)
        print()
    
    # Test summary message
    logger.info("Ejemplo de resumen diario:")
    print("\n" + "═" * 60)
    print("RESUMEN DIARIO:")
    print("═" * 60)
    
    summary_message = f"""📊 *Resumen del Día*

Total gaps detectados: {len(test_gaps)}

*Top 3 Gaps:*
🥇 $SOFI: UP 25.5%
🥈 $LCID: UP 15.2%
🥉 $PLTR: DOWN 8.5%"""
    
    print(summary_message)
    print("═" * 60)
    
    logger.info("\n✅ Formato de mensajes listo!")
    logger.info("Para recibir alertas reales, configura el bot siguiendo el README")


if __name__ == "__main__":
    main()