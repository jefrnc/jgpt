#!/usr/bin/env python3
"""
Script para configurar y probar el bot de Telegram
"""

import asyncio
from src.alerts.telegram_bot import TelegramAlertBot
from src.utils.logger import setup_logger


async def test_bot():
    logger = setup_logger('telegram_setup')
    
    logger.info("=== Configuración del Bot de Telegram ===\n")
    
    # Check if bot is configured
    bot = TelegramAlertBot()
    
    if not bot.enabled:
        logger.error("❌ Bot no configurado!")
        logger.info("\nPasos para configurar:")
        logger.info("1. Abre Telegram y busca @BotFather")
        logger.info("2. Envía /newbot y sigue las instrucciones")
        logger.info("3. Copia el token que te da BotFather")
        logger.info("4. Agrega a tu .env: TELEGRAM_BOT_TOKEN=tu_token_aqui")
        logger.info("5. Ejecuta este script de nuevo")
        return
    
    logger.info("✅ Bot configurado correctamente!")
    logger.info("\nAhora necesitas obtener tu Chat ID:")
    logger.info("1. Inicia una conversación con tu bot en Telegram")
    logger.info("2. Envía /start al bot")
    logger.info("3. El bot te responderá con tu Chat ID")
    logger.info("4. Agrega a tu .env: TELEGRAM_CHAT_ID=tu_chat_id")
    
    # Test message
    if bot.chat_id:
        logger.info("\n✅ Chat ID configurado! Enviando mensaje de prueba...")
        
        test_gap = {
            'symbol': 'TEST',
            'gap_direction': 'UP',
            'gap_percent': 15.5,
            'previous_close': 10.00,
            'current_price': 11.55,
            'volume': 1234567
        }
        
        message = bot.format_gap_alert(test_gap)
        await bot.send_alert(message)
        
        logger.info("✅ Mensaje enviado! Revisa tu Telegram.")
    else:
        logger.info("\n⚠️  Chat ID no configurado aún")
        logger.info("Sigue los pasos anteriores para obtenerlo")


def main():
    print("""
    ╔══════════════════════════════════════╗
    ║   Configuración Bot Telegram         ║
    ║   Trading Edge System                ║
    ╚══════════════════════════════════════╝
    """)
    
    asyncio.run(test_bot())


if __name__ == "__main__":
    main()