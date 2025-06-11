#!/usr/bin/env python3
"""
Test real del bot con envío de alertas a Telegram
"""
import asyncio
from datetime import datetime
from src.scanners.gap_scanner import GapScanner
from src.alerts.telegram_bot import TelegramAlertBot
from src.utils.logger import setup_logger

async def test_real_alerts():
    logger = setup_logger('test_alerts')
    
    print("🔍 PRUEBA REAL - Bot con alertas a Telegram")
    print("=" * 60)
    
    # Initialize components
    gap_scanner = GapScanner()
    telegram_bot = TelegramAlertBot()
    
    if not telegram_bot.enabled:
        print("❌ Telegram bot no configurado")
        return
    
    print("✅ Telegram bot configurado")
    print(f"📱 Chat ID: {telegram_bot.chat_id}")
    
    # Get symbols to scan (same as real bot)
    symbols = gap_scanner.get_market_movers()
    print(f"📊 Escaneando {len(symbols)} símbolos...")
    
    # Run gap scan
    results = gap_scanner.scan_watchlist(symbols)
    print(f"🔍 Gaps encontrados: {len(results)}")
    
    if results:
        print("\n🚀 ENVIANDO ALERTAS:")
        for gap in results:
            print(f"\n📊 {gap['symbol']}:")
            print(f"   Gap: {gap['gap_direction']} {abs(gap['gap_percent']):.1f}%")
            print(f"   Precio: ${gap['previous_close']:.2f} → ${gap['current_price']:.2f}")
            print(f"   Volumen: {gap['volume']:,}")
            
            # Format and send alert
            alert_msg = telegram_bot.format_gap_alert(gap)
            try:
                await telegram_bot.send_alert(alert_msg)
                print(f"   ✅ Alerta enviada a Telegram")
            except Exception as e:
                print(f"   ❌ Error enviando alerta: {str(e)}")
    else:
        print("\n⚠️ No hay gaps para alertar ahora")
        
        # Send test message anyway
        test_msg = f"🤖 Bot Test - {datetime.now().strftime('%H:%M:%S')}\n\nNo gaps detected right now, but bot is working correctly!\n\nNext scan will be during market hours."
        try:
            await telegram_bot.send_alert(test_msg)
            print("✅ Mensaje de prueba enviado")
        except Exception as e:
            print(f"❌ Error enviando prueba: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_real_alerts())