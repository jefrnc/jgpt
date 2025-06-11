#!/usr/bin/env python3
"""
Test del scanner enhanced con datos simulados de float
"""

import asyncio
from src.alerts.telegram_bot import TelegramAlertBot
from src.utils.logger import setup_logger


def simulate_enhanced_gaps():
    """Simular gaps con datos de float para demostrar funcionalidad"""
    
    # Datos simulados que representan lo que obtendríamos de APIs reales
    enhanced_gaps = [
        {
            'symbol': 'SOFI',
            'gap_direction': 'UP',
            'gap_percent': 15.5,
            'previous_close': 8.40,
            'current_price': 9.70,
            'volume': 2800000,
            'float_data': {
                'symbol': 'SOFI',
                'shares_outstanding': 950_000_000,
                'float_shares': 8_500_000,  # MICROFLOAT!
                'market_cap': 9_215_000_000,
                'float_category': 'micro_float',
                'data_source': 'yfinance'
            },
            'float_score': 85,  # High score!
            'is_microfloat': True,
            'squeeze_setup': False
        },
        {
            'symbol': 'LCID',
            'gap_direction': 'UP',
            'gap_percent': 22.3,
            'previous_close': 3.20,
            'current_price': 3.91,
            'volume': 5200000,
            'float_data': {
                'symbol': 'LCID',
                'shares_outstanding': 1_800_000_000,
                'float_shares': 4_200_000,  # NANO FLOAT!
                'market_cap': 7_038_000_000,
                'float_category': 'nano_float',
                'data_source': 'finnhub'
            },
            'float_score': 95,  # Maximum score!
            'is_microfloat': True,
            'squeeze_setup': True  # Perfect setup!
        },
        {
            'symbol': 'AAPL',
            'gap_direction': 'DOWN',
            'gap_percent': -5.2,
            'previous_close': 202.50,
            'current_price': 192.00,
            'volume': 85000000,
            'float_data': {
                'symbol': 'AAPL',
                'shares_outstanding': 15_500_000_000,
                'float_shares': 15_400_000_000,  # HUGE FLOAT
                'market_cap': 3_100_000_000_000,
                'float_category': 'high_float',
                'data_source': 'yfinance'
            },
            'float_score': 5,  # Low score
            'is_microfloat': False,
            'squeeze_setup': False
        }
    ]
    
    return enhanced_gaps


async def test_enhanced_alerts():
    logger = setup_logger('enhanced_scanner_test')
    
    logger.info("=== Test Enhanced Scanner (Simulado) ===")
    
    # Get simulated data
    enhanced_gaps = simulate_enhanced_gaps()
    
    # Display console results
    logger.info("\n🔍 Enhanced Gap + Float Results:")
    
    for gap in enhanced_gaps:
        float_data = gap['float_data']
        float_shares = float_data.get('float_shares', 0)
        
        if float_shares < 1_000_000:
            float_str = f"{float_shares/1000:.0f}K"
        else:
            float_str = f"{float_shares/1_000_000:.1f}M"
        
        logger.info(f"\n📊 {gap['symbol']}:")
        logger.info(f"  Gap: {gap['gap_direction']} {abs(gap['gap_percent'])}%")
        logger.info(f"  Price: ${gap['previous_close']:.2f} → ${gap['current_price']:.2f}")
        logger.info(f"  Float: {float_str} shares ({float_data['float_category']})")
        logger.info(f"  Float Score: {gap['float_score']}/100")
        
        if gap['is_microfloat']:
            logger.info(f"  🔥 MICROFLOAT DETECTED!")
        if gap['squeeze_setup']:
            logger.info(f"  🚨 SQUEEZE SETUP!")
    
    # Test enhanced Telegram alerts
    bot = TelegramAlertBot()
    if bot.enabled:
        logger.info(f"\n📱 Sending enhanced Telegram alerts...")
        
        for gap in enhanced_gaps[:2]:  # Send top 2
            message = format_enhanced_alert(gap)
            await bot.send_alert(message)
            await asyncio.sleep(2)
        
        logger.info(f"✅ Enhanced alerts sent!")
    else:
        logger.info(f"📱 Telegram not configured - alerts would be sent")


def format_enhanced_alert(gap_data):
    """Format enhanced alert with float information"""
    direction_emoji = "🟢" if gap_data['gap_direction'] == 'UP' else "🔴"
    gap_percent = abs(gap_data['gap_percent'])
    
    # Determine alert level based on float + gap combo
    if gap_data.get('squeeze_setup'):
        alert_emoji = "🚨💥🚨"
        alert_text = "SQUEEZE + GAP COMBO!"
    elif gap_data.get('is_microfloat') and gap_percent > 15:
        alert_emoji = "🔥🚨🔥"
        alert_text = "MEGA MICROFLOAT GAP!"
    elif gap_data.get('is_microfloat'):
        alert_emoji = "🔥🔥"
        alert_text = "MICROFLOAT GAP!"
    elif gap_percent >= 20:
        alert_emoji = "🚨🚨🚨"
        alert_text = "MEGA GAP!"
    else:
        alert_emoji = "📊"
        alert_text = "Enhanced Gap Alert"
    
    message = (
        f"{alert_emoji} *{alert_text}* {alert_emoji}\n\n"
        f"{direction_emoji} *${gap_data['symbol']}* {direction_emoji}\n"
        f"Gap: *{gap_data['gap_direction']} {gap_percent:.1f}%*\n"
        f"Precio: ${gap_data['previous_close']:.2f} → ${gap_data['current_price']:.2f}\n"
        f"Volumen: {gap_data['volume']:,}\n"
    )
    
    # Add float information
    float_data = gap_data['float_data']
    float_shares = float_data.get('float_shares', 0)
    
    if float_shares:
        if float_shares < 1_000_000:
            float_str = f"{float_shares/1000:.0f}K"
        else:
            float_str = f"{float_shares/1_000_000:.1f}M"
        
        message += f"🔍 Float: {float_str} shares\n"
        message += f"📊 Float Score: {gap_data.get('float_score', 0)}/100\n"
        message += f"🏷️ Category: {float_data.get('float_category', 'unknown').replace('_', ' ')}\n"
        
        if gap_data.get('is_microfloat'):
            message += "🔥 *MICROFLOAT PLAY!*\n"
        if gap_data.get('squeeze_setup'):
            message += "🚨 *PERFECT SQUEEZE SETUP!*\n"
    
    # Enhanced targets for microfloats
    if gap_data.get('is_microfloat'):
        message += "\n💡 *Microfloat Strategy:*\n"
        message += f"🎯 Target 1: ${gap_data['current_price'] * 1.15:.2f} (+15%)\n"
        message += f"🎯 Target 2: ${gap_data['current_price'] * 1.30:.2f} (+30%)\n"
        message += f"🛑 Stop: ${gap_data['current_price'] * 0.92:.2f} (-8%)\n"
    else:
        message += "\n💡 *Standard Setup:*\n"
        message += f"🎯 Target: ${gap_data['current_price'] * 1.05:.2f} (+5%)\n"
        message += f"🛑 Stop: ${gap_data['current_price'] * 0.97:.2f} (-3%)\n"
        
    message += f"\n⏰ Simulated - Demo data"
    
    return message


def main():
    print("""
    ╔══════════════════════════════════════════════════╗
    ║       Enhanced Gap + Float Scanner Demo          ║
    ║                                                  ║
    ║   🔥 Detecta microfloats + gaps                  ║
    ║   🚨 Identifica squeeze setups                   ║
    ║   📊 Scoring inteligente                         ║
    ║   📱 Alertas enhanced                            ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    asyncio.run(test_enhanced_alerts())


if __name__ == "__main__":
    main()