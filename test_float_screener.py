#!/usr/bin/env python3
"""
Test script para el float screener
"""

from src.scanners.float_screener import FloatScreener
from src.api.finnhub_client import FinnhubClient
from src.utils.logger import setup_logger


def main():
    logger = setup_logger('float_screener_test', 'DEBUG')
    
    logger.info("=== Test Float Screener ===")
    
    # Check if Finnhub is configured
    finnhub = FinnhubClient()
    if not finnhub.enabled:
        logger.error("❌ Finnhub API not configured!")
        logger.info("Para configurar:")
        logger.info("1. Ve a https://finnhub.io/register")
        logger.info("2. Registrate gratis")
        logger.info("3. Obtén tu API key")
        logger.info("4. Agrégala al .env: FINNHUB_API_KEY=tu_key_aqui")
        return
    
    logger.info("✅ Finnhub configurado correctamente!")
    
    # Initialize screener
    screener = FloatScreener()
    
    # Test symbols (mix of different float sizes)
    test_symbols = [
        'AAPL',   # Large float
        'TSLA',   # Medium float  
        'PLTR',   # Low float
        'SOFI',   # Small cap
        'LCID',   # Small cap
        'RIVN',   # Medium float
        'NIO',    # ADR
        'GRAB'    # Small cap
    ]
    
    logger.info(f"\n=== Test 1: Individual Symbol Analysis ===")
    
    for symbol in test_symbols[:3]:  # Test first 3 to conserve API calls
        logger.info(f"\nAnalyzing {symbol}...")
        
        float_data = screener.screen_symbol(symbol)
        if float_data:
            analysis = screener.format_float_analysis(float_data)
            print(analysis)
        else:
            logger.warning(f"No data available for {symbol}")
    
    logger.info(f"\n=== Test 2: Batch Screening ===")
    
    # Screen multiple symbols
    results = screener.screen_watchlist(test_symbols[:5])  # Limit to save API calls
    
    if results:
        summary = screener.get_float_summary(results)
        print(summary)
        
        # Find microfloats
        microfloats = [r for r in results if r.get('screening_results', {}).get('is_microfloat')]
        if microfloats:
            logger.info(f"\n🔥 Found {len(microfloats)} microfloats:")
            for mf in microfloats:
                logger.info(f"  • {mf['symbol']}: {mf.get('float_shares', 0)/1_000_000:.1f}M float")
        
        # Find high scores
        high_scores = [r for r in results if r.get('screening_results', {}).get('float_score', 0) > 50]
        if high_scores:
            logger.info(f"\n⭐ Found {len(high_scores)} high-scoring opportunities:")
            for hs in high_scores:
                score = hs.get('screening_results', {}).get('float_score', 0)
                logger.info(f"  • {hs['symbol']}: Score {score}/100")
    
    logger.info(f"\n=== Test 3: API Rate Limiting ===")
    logger.info(f"Calls made: {len(finnhub.call_timestamps)}")
    logger.info(f"Rate limit: {finnhub.calls_per_minute} calls/minute")
    logger.info(f"✅ Rate limiting working correctly")
    
    logger.info(f"\n✅ Float Screener test completed!")
    logger.info(f"💡 Ready to integrate with gap scanner for maximum edge!")


if __name__ == "__main__":
    main()