#!/usr/bin/env python3
"""
Test scanner con símbolos del Discord
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from src.api.alpaca_client import AlpacaClient
from src.scanners.gap_scanner import GapScanner
from src.scanners.float_screener import FloatScreener
from src.scanners.news_scanner import NewsScanner
from src.utils.logger import setup_logger

load_dotenv()

def test_scanners():
    logger = setup_logger('test_scanner')
    print("\n🔍 PRUEBA DE SCANNERS - Trading Bot")
    print("=" * 70)
    print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Initialize components
    client = AlpacaClient()
    gap_scanner = GapScanner(client)
    float_screener = FloatScreener()
    news_scanner = NewsScanner()
    
    # Símbolos a testear
    test_symbols = ['KLTO', 'KZIA', 'VTAK', 'HSDT', 'CARM', 'OEGD', 'KNW', 'SIR', 
                   'AMC', 'GME', 'MARA', 'RIOT', 'SOFI', 'DWAC']
    
    print("\n📊 ESCANEANDO GAPS Y FLOATS...")
    gaps_found = []
    
    for symbol in test_symbols:
        try:
            # Get snapshot
            snapshot = client.get_snapshot(symbol)
            
            if snapshot and snapshot.latest_trade and snapshot.prev_daily_bar:
                latest_price = snapshot.latest_trade.price
                prev_close = snapshot.prev_daily_bar.close
                gap_pct = ((latest_price - prev_close) / prev_close) * 100
                volume = snapshot.daily_bar.volume if snapshot.daily_bar else 0
                
                # Get float data
                float_data = float_screener.get_float_data(symbol)
                float_str = "Unknown"
                if float_data and float_data.get('shares_float'):
                    float_m = float_data['shares_float'] / 1_000_000
                    float_str = f"{float_m:.1f}M"
                
                # Print results
                print(f"\n{symbol}:")
                print(f"  Price: ${prev_close:.2f} → ${latest_price:.2f} ({gap_pct:+.1f}%)")
                print(f"  Volume: {volume:,}")
                print(f"  Float: {float_str}")
                
                if abs(gap_pct) > 5:
                    gaps_found.append({
                        'symbol': symbol,
                        'gap': gap_pct,
                        'price': latest_price,
                        'volume': volume,
                        'float': float_str
                    })
                    print(f"  ✅ GAP DETECTADO!")
                
                # Check news
                news_data = news_scanner.scan_symbol_news(symbol, hours_back=48)
                if news_data and news_data['has_catalyst']:
                    print(f"  📰 NEWS CATALYST! Score: {news_data['catalyst_score']}")
                    if news_data['key_headlines']:
                        print(f"     {news_data['key_headlines'][0][:60]}...")
                        
        except Exception as e:
            print(f"\n{symbol}: ❌ Error - {str(e)[:50]}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 RESUMEN:")
    print(f"✅ Gaps detectados (>5%): {len(gaps_found)}")
    
    if gaps_found:
        print("\n🚀 ALERTAS QUE SE ENVIARÍAN:")
        for gap in gaps_found:
            print(f"\n{gap['symbol']}:")
            print(f"  Gap: {gap['gap']:+.1f}%")
            print(f"  Price: ${gap['price']:.2f}")
            print(f"  Volume: {gap['volume']:,}")
            print(f"  Float: {gap['float']}")
    else:
        print("\n⚠️ No se detectaron gaps significativos en este momento")
    
    print("\n💡 NOTA: El bot escanea automáticamente:")
    print("   - Premarket: 4:00-9:30 AM ET (cada 3 min)")
    print("   - Market hours: 9:30 AM-4:00 PM ET (cada 10 min)")
    print("   - After hours: 4:00-8:00 PM ET (cada 30 min)")

if __name__ == "__main__":
    test_scanners()