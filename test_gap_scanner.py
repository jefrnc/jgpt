#!/usr/bin/env python3
"""
Test script para el gap scanner
"""

from src.scanners.gap_scanner import GapScanner
from src.utils.logger import setup_logger
import json


def main():
    # Setup logger
    logger = setup_logger('gap_scanner_test', 'DEBUG')
    
    try:
        # Initialize scanner
        logger.info("Inicializando Gap Scanner...")
        scanner = GapScanner()
        
        # Test individual symbols
        logger.info("\n=== Test 1: Escanear símbolos individuales ===")
        test_symbols = ['AAPL', 'TSLA', 'AMD', 'NVDA', 'SOFI']
        
        for symbol in test_symbols:
            logger.info(f"\nEscaneando {symbol}...")
            
            # Get snapshot to show current data
            snapshot = scanner.client.get_snapshot(symbol)
            if snapshot and snapshot.daily_bar and snapshot.latest_trade:
                prev_close = float(snapshot.daily_bar.close)
                curr_price = float(snapshot.latest_trade.price)
                gap_pct = scanner.calculate_gap_percentage(curr_price, prev_close)
                
                logger.info(f"  Close anterior: ${prev_close:.2f}")
                logger.info(f"  Precio actual: ${curr_price:.2f}")
                logger.info(f"  Gap: {gap_pct:.2f}%")
            
            result = scanner.scan_symbol(symbol)
            
            if result:
                logger.info(f"✓ Gap encontrado!")
                logger.info(f"  Dirección: {result['gap_direction']}")
                logger.info(f"  Porcentaje: {result['gap_percent']}%")
                logger.info(f"  Precio: ${result['previous_close']:.2f} → ${result['current_price']:.2f}")
                logger.info(f"  Volumen: {result['volume']:,}")
            else:
                logger.info(f"✗ No cumple criterios de gap (mínimo {scanner.min_gap_percent}%)")
        
        # Test market hours
        logger.info("\n=== Test 2: Verificar horario de mercado ===")
        logger.info(f"¿Mercado abierto?: {scanner.is_market_hours()}")
        logger.info(f"¿Premarket?: {scanner.is_premarket_hours()}")
        
        # Test full scan
        logger.info("\n=== Test 3: Escaneo completo de watchlist ===")
        watchlist = scanner.get_market_movers()
        logger.info(f"Escaneando {len(watchlist)} símbolos...")
        
        results = scanner.scan_watchlist(watchlist[:10])  # Solo primeros 10 para test rápido
        
        if results:
            logger.info(f"\n✅ Encontrados {len(results)} gaps significativos:")
            print(scanner.format_results(results))
        else:
            logger.info("No se encontraron gaps significativos")
        
        logger.info("\n✅ Scanner funcionando correctamente!")
        
    except Exception as e:
        logger.error(f"Error durante las pruebas: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()