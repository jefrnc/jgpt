#!/usr/bin/env python3
"""
Test script para verificar la conexión con Alpaca API
"""

from src.api.alpaca_client import AlpacaClient
from src.utils.logger import setup_logger
import json


def main():
    # Setup logger
    logger = setup_logger('alpaca_test')
    
    try:
        # Initialize client
        logger.info("Inicializando cliente Alpaca...")
        client = AlpacaClient()
        
        # Test 1: Get account info
        logger.info("\n=== Test 1: Información de cuenta ===")
        account = client.get_account()
        logger.info(f"Cuenta: {account.account_number}")
        logger.info(f"Buying Power: ${account.buying_power}")
        logger.info(f"Cash: ${account.cash}")
        logger.info(f"Equity: ${account.equity}")
        
        # Test 2: Check market status
        logger.info("\n=== Test 2: Estado del mercado ===")
        market_hours = client.get_market_hours()
        logger.info(f"Mercado abierto: {market_hours['is_open']}")
        logger.info(f"Horario: {market_hours['open']} - {market_hours['close']}")
        
        # Test 3: Get snapshot for a popular stock
        logger.info("\n=== Test 3: Snapshot de AAPL ===")
        snapshot = client.get_snapshot('AAPL')
        latest_trade = snapshot.latest_trade
        logger.info(f"AAPL - Último precio: ${latest_trade.price}")
        logger.info(f"Volumen: {latest_trade.size}")
        logger.info(f"Timestamp: {latest_trade.timestamp}")
        
        # Test 4: Check if symbol is tradeable
        logger.info("\n=== Test 4: Verificar símbolos ===")
        symbols = ['AAPL', 'TSLA', 'INVALID123']
        for symbol in symbols:
            tradeable = client.is_tradeable(symbol)
            logger.info(f"{symbol}: {'✓ Tradeable' if tradeable else '✗ No tradeable'}")
        
        logger.info("\n✅ Conexión exitosa! Alpaca API funcionando correctamente.")
        
    except Exception as e:
        logger.error(f"Error durante las pruebas: {str(e)}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()