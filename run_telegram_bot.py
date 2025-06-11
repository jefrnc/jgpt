#!/usr/bin/env python3
"""
Script para ejecutar solo el bot de Telegram (para obtener Chat ID)
"""

from src.alerts.telegram_bot import TelegramAlertBot
from src.utils.logger import setup_logger


def main():
    logger = setup_logger('telegram_runner')
    
    logger.info("Iniciando bot de Telegram...")
    logger.info("Envía /start al bot para obtener tu Chat ID")
    
    bot = TelegramAlertBot()
    
    if not bot.enabled:
        logger.error("Bot no habilitado - verifica TELEGRAM_BOT_TOKEN en .env")
        return
    
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot detenido")


if __name__ == "__main__":
    main()