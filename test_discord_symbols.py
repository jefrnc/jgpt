#!/usr/bin/env python3
"""
Test símbolos mencionados en Discord para ver si nuestro bot los detectaría
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from src.api.alpaca_client import AlpacaClient
from src.scanners.gap_scanner import GapScanner
from src.scanners.float_screener import FloatScreener
from src.utils.logger import setup_logger

load_dotenv()

def test_discord_symbols():
    logger = setup_logger('discord_test')
    
    # Símbolos del Discord del 11 de Junio
    symbols = ['KLTO', 'SIR', 'CARM', 'OEGD', 'KNW', 'KZIA', 'VTAK', 'HSDT']
    
    print("🔍 Analizando símbolos del Discord (11 de Junio)")
    print("=" * 70)
    
    client = AlpacaClient()
    gap_scanner = GapScanner(client)
    float_screener = FloatScreener()
    
    # Resultados
    gaps_detected = []
    micro_floats = []
    
    for symbol in symbols:
        print(f"\n📊 Analizando {symbol}:")
        
        try:
            # Get snapshot
            snapshot = client.get_snapshot(symbol)
            
            if snapshot and snapshot.latest_trade and snapshot.prev_daily_bar:
                latest_price = snapshot.latest_trade.price
                prev_close = snapshot.prev_daily_bar.close
                
                # Calculate gap
                gap_pct = ((latest_price - prev_close) / prev_close) * 100
                
                # Get volume
                volume = snapshot.daily_bar.volume if snapshot.daily_bar else 0
                
                print(f"  💰 Precio actual: ${latest_price:.2f}")
                print(f"  📈 Precio cierre anterior: ${prev_close:.2f}")
                print(f"  🚀 Gap: {gap_pct:+.1f}%")
                print(f"  📊 Volumen: {volume:,}")
                
                if abs(gap_pct) > 5:
                    gaps_detected.append((symbol, gap_pct))
                    print(f"  ✅ GAP DETECTADO por nuestro bot!")
                
                # Check float
                try:
                    float_data = float_screener.get_float_data(symbol)
                    if float_data and float_data.get('shares_float'):
                        float_m = float_data['shares_float'] / 1_000_000
                        category = float_data.get('float_category', 'Unknown')
                        
                        print(f"  🏷️ Float: {float_m:.1f}M shares")
                        print(f"  📍 Categoría: {category}")
                        
                        if category in ['Nano Float', 'Micro Float']:
                            micro_floats.append((symbol, float_m, category))
                            print(f"  ✅ MICRO/NANO FLOAT detectado!")
                except Exception as e:
                    print(f"  ⚠️ Sin datos de float")
                    
            else:
                print(f"  ❌ Sin datos de precio disponibles")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE DETECCIÓN:")
    print(f"\n🚀 Gaps detectados (>5%): {len(gaps_detected)}")
    for symbol, gap in gaps_detected:
        print(f"   - {symbol}: {gap:+.1f}%")
    
    print(f"\n🏷️ Micro/Nano floats detectados: {len(micro_floats)}")
    for symbol, float_m, category in micro_floats:
        print(f"   - {symbol}: {float_m:.1f}M ({category})")
    
    print("\n💡 ANÁLISIS:")
    print("✅ Nuestro bot SÍ detectaría:")
    print("   - Gaps significativos (>5%)")
    print("   - Micro/nano floats")
    print("\n❌ Nuestro bot NO detectaría (aún):")
    print("   - Noticias/catalysts")
    print("   - Volumen inusual vs promedio")
    print("   - Sectores calientes")
    print("   - Divergencias técnicas")
    
    # Verificar si el bot está corriendo
    print("\n🤖 ESTADO DEL BOT:")
    try:
        os.system("systemctl is-active trading-bot")
    except:
        print("No se pudo verificar el estado del servicio")

if __name__ == "__main__":
    test_discord_symbols()