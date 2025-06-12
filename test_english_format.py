#!/usr/bin/env python3
"""
Test the new English alert format with Flash Research statistics
"""
from datetime import datetime

def format_new_english_alert():
    """Format alert in new English format with Flash Research data"""
    
    # Test gap data
    gap_data = {
        'symbol': 'KLTO',
        'gap_percent': -24.1,
        'gap_direction': 'DOWN',
        'previous_close': 2.45,
        'current_price': 1.86,
        'volume': 850000,
    }
    
    # Pattern analysis with Flash Research data
    pattern_analysis = {
        'pattern_type': 'Float Squeeze',
        'setup_quality': 85,
        'confidence': 78,
        'playbook': 'Small float (3.2M) with 24.1% gap creates supply/demand imbalance for day trading. Limited supply can amplify intraday moves.',
        'flash_analysis': {
            'has_flash_data': True,
            'gap_continuation_rate': 72,
            'gap_fill_rate': 35,
            'total_gaps_analyzed': 45,
            'avg_gap_size': 18.5,
            'volume_factor': 2.8
        },
        'float_analysis': {
            'is_microfloat': True,
            'float_shares': 3_200_000
        }
    }
    
    # Edge analysis
    edge_analysis = {
        'total_edge_score': 82.5,
        'edge_classification': 'Strong Edge',
        'trading_recommendations': [
            'High probability setup for day trading',
            'Strong 72% historical continuation rate',
            'Low gap fill tendency supports momentum plays'
        ]
    }
    
    # Build the new English alert format
    direction_emoji = "🟢" if gap_data['gap_direction'] == 'UP' else "🔴"
    gap_percent = abs(gap_data['gap_percent'])
    symbol = gap_data['symbol']
    
    edge_score = edge_analysis['total_edge_score']
    
    if edge_score >= 85:
        alert_emoji = "🚨🔥💎"
        priority = "EXCEPTIONAL"
    elif edge_score >= 75:
        alert_emoji = "🔥⚡🎯"
        priority = "STRONG"
    elif edge_score >= 65:
        alert_emoji = "⚡📊🔍"
        priority = "GOOD"
    else:
        alert_emoji = "📊📈"
        priority = "MODERATE"
    
    # Build header
    message = f"{alert_emoji} *{priority} EDGE* {alert_emoji}\n\n"
    message += f"{direction_emoji} *${symbol}* - {pattern_analysis['pattern_type']} {direction_emoji}\n"
    message += f"Gap: *{gap_data['gap_direction']} {gap_percent:.1f}%* | Edge: *{edge_score:.0f}/100*\n"
    message += f"Price: ${gap_data['previous_close']:.2f} → ${gap_data['current_price']:.2f}\n\n"
    
    # Flash Research data - NEW ENGLISH FORMAT
    flash_analysis = pattern_analysis['flash_analysis']
    if flash_analysis.get('has_flash_data', False):
        continuation_rate = flash_analysis['gap_continuation_rate']
        gap_fill_rate = flash_analysis['gap_fill_rate']
        total_gaps = flash_analysis['total_gaps_analyzed']
        volume_factor = flash_analysis['volume_factor']
        avg_gap_size = flash_analysis['avg_gap_size']
        
        # Calculate red vs green closing rates
        if gap_data['gap_direction'] == 'UP':
            green_rate = continuation_rate
            red_rate = 100 - continuation_rate
        else:
            green_rate = 100 - continuation_rate  
            red_rate = continuation_rate
        
        message += f"📊 *Historical Data ({total_gaps} gaps):*\n"
        message += f"   • Continued: {continuation_rate:.0f}% | Reversed: {100-continuation_rate:.0f}%\n"
        message += f"   • Red Close: {red_rate:.0f}% | Green Close: {green_rate:.0f}%\n"
        message += f"   • Gap Fill Rate: {gap_fill_rate:.0f}%\n"
        message += f"   • Avg Gap Size: {avg_gap_size:.1f}%\n"
        message += f"   • Volume Spike: {volume_factor:.1f}x normal\n\n"
    
    # Float context
    float_analysis = pattern_analysis['float_analysis']
    if float_analysis.get('is_microfloat'):
        float_shares = float_analysis['float_shares']
        float_str = f"{float_shares/1_000_000:.1f}M"
        turnover = (gap_data['volume'] / float_shares) * 100
        message += f"🔥 *Float:* {float_str} shares ({turnover:.1f}% turnover)\n"
    
    # Volume context
    volume = gap_data['volume']
    if volume > 500_000:
        message += f"📊 *Volume:* {volume:,.0f} (high)\n"
    
    # AI Analysis insights
    ai_confidence = pattern_analysis['confidence']
    setup_quality = pattern_analysis['setup_quality']
    message += f"🧠 *AI Analysis:* {setup_quality}% quality, {ai_confidence}% confidence\n"
    
    # Key insight from AI
    playbook_text = pattern_analysis['playbook']
    first_sentence = playbook_text.split('.')[0] + '.'
    message += f"💡 *AI Insight:* {first_sentence}\n"
    
    # Trading recommendation
    recommendations = edge_analysis['trading_recommendations']
    top_rec = recommendations[0]
    message += f"🎯 *Rec:* {top_rec}\n"
    
    message += f"\n⏰ {datetime.now().strftime('%H:%M:%S ET')}"
    
    return message

def test_new_format():
    print("🧪 TESTING NEW ENGLISH ALERT FORMAT")
    print("=" * 70)
    print("📱 NEW TELEGRAM ALERT (ENGLISH WITH FLASH RESEARCH DATA):")
    print("=" * 50)
    
    alert_message = format_new_english_alert()
    print(alert_message)
    
    print("=" * 50)
    print("✅ NEW FEATURES:")
    print("• All text in English")
    print("• Red/Green close rates included")
    print("• Flash Research statistics prominent")
    print("• Day trading context")
    print("• Removed '¿Por qué?' section")
    print(f"• Message length: {len(alert_message)} characters")

if __name__ == "__main__":
    test_new_format()