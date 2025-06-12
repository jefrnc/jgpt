#!/usr/bin/env python3
"""
Test simple del bot sin dependencias externas
"""
import asyncio
from datetime import datetime

# Simular gap data para testing
gap_data = {
    'symbol': 'KLTO',
    'gap_percent': -24.1,
    'gap_direction': 'DOWN',
    'previous_close': 2.45,
    'current_price': 1.86,
    'volume': 850000,
    'timestamp': datetime.now().isoformat()
}

# Simular pattern analysis
pattern_analysis = {
    'pattern_type': 'Float Squeeze',
    'setup_quality': 85,
    'confidence': 78,
    'playbook': 'Small float with significant gap creating supply/demand imbalance. Limited supply can amplify moves.',
    'key_factors': ['Large gap', 'Micro float', 'High volume'],
    'risk_level': 'Medium',
    'flash_analysis': {
        'has_flash_data': True,
        'gap_continuation_rate': 72,
        'gap_fill_rate': 35,
        'total_gaps_analyzed': 45,
        'statistical_edge': 'Strong bullish momentum',
        'gap_edge_score': 78
    },
    'float_analysis': {
        'is_microfloat': True,
        'is_nanofloat': False,
        'float_shares': 3_200_000
    },
    'news_analysis': {
        'has_catalyst': False
    }
}

# Simular edge analysis
edge_analysis = {
    'total_edge_score': 82.5,
    'edge_classification': 'Strong Edge',
    'confidence_level': 'High',
    'component_scores': {
        'flash_research': 78.0,
        'gap_characteristics': 85.0,
        'float_dynamics': 90.0,
        'ai_pattern': 82.0,
        'news_catalyst': 50.0
    },
    'trading_recommendations': [
        'High probability setup - consider larger position size',
        'Strong 72% historical continuation rate',
        'Low gap fill tendency supports momentum plays'
    ],
    'edge_summary': 'Strong Edge (Score: 83/100, Flash: 78/100, Cont: 72%)'
}

def format_enhanced_alert(gap_data, pattern_analysis, edge_analysis):
    """Format enhanced alert exactly like main.py"""
    direction_emoji = "🟢" if gap_data['gap_direction'] == 'UP' else "🔴"
    gap_percent = abs(gap_data['gap_percent'])
    symbol = gap_data['symbol']
    
    # Get comprehensive analysis data
    flash_analysis = pattern_analysis.get('flash_analysis', {})
    
    # Determine alert priority and emojis
    edge_score = edge_analysis.get('total_edge_score', 50)
    
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
    
    # Build header with context
    message = f"{alert_emoji} *{priority} EDGE* {alert_emoji}\n\n"
    message += f"{direction_emoji} *${symbol}* - {pattern_analysis.get('pattern_type', 'Gap')} {direction_emoji}\n"
    message += f"Gap: *{gap_data['gap_direction']} {gap_percent:.1f}%* | Edge: *{edge_score:.0f}/100*\n"
    message += f"Precio: ${gap_data['previous_close']:.2f} → ${gap_data['current_price']:.2f}\n\n"
    
    # Add WHY context - the most important part
    message += f"📋 *¿POR QUÉ ESTE MOVIMIENTO?*\n"
    
    # Historical context from Flash Research
    if flash_analysis.get('has_flash_data', False):
        continuation_rate = flash_analysis.get('gap_continuation_rate', 50)
        gap_fill_rate = flash_analysis.get('gap_fill_rate', 50)
        total_gaps = flash_analysis.get('total_gaps_analyzed', 0)
        
        if total_gaps > 10:
            message += f"📊 Historial: {continuation_rate:.0f}% continúa, {gap_fill_rate:.0f}% se cierra (basado en {total_gaps} gaps)\n"
        
        statistical_edge = flash_analysis.get('statistical_edge', '')
        if statistical_edge and statistical_edge != 'Insufficient data':
            message += f"📈 Perfil: {statistical_edge}\n"
    
    # AI Analysis insights
    ai_confidence = pattern_analysis.get('confidence', 0)
    setup_quality = pattern_analysis.get('setup_quality', 0)
    if ai_confidence > 60 and setup_quality > 60:
        message += f"🧠 AI: {setup_quality}% quality, {ai_confidence}% confidence\n"
    
    # Float context
    float_analysis = pattern_analysis.get('float_analysis', {})
    if float_analysis.get('is_microfloat') or float_analysis.get('is_nanofloat'):
        float_shares = float_analysis.get('float_shares', 0)
        if float_shares > 0:
            float_str = f"{float_shares/1_000_000:.1f}M" if float_shares >= 1_000_000 else f"{float_shares/1000:.0f}K"
            turnover = (gap_data['volume'] / float_shares) * 100
            message += f"🔥 Float: {float_str} shares ({turnover:.1f}% volumen vs float)\n"
    
    # Volume context
    volume = gap_data['volume']
    if volume > 1_000_000:
        message += f"📊 Volumen: {volume:,.0f} (muy alto)\n"
    elif volume > 500_000:
        message += f"📊 Volumen: {volume:,.0f} (alto)\n"
    elif volume > 100_000:
        message += f"📊 Volumen: {volume:,.0f}\n"
    
    # Key insight from AI
    playbook_text = pattern_analysis.get('playbook', '')
    if playbook_text and len(playbook_text) > 20:
        first_sentence = playbook_text.split('.')[0] + '.'
        if len(first_sentence) < 100:
            message += f"💡 *AI Insight:* {first_sentence}\n"
    
    # Trading recommendations
    recommendations = edge_analysis.get('trading_recommendations', [])
    if recommendations:
        top_rec = recommendations[0]
        if len(top_rec) < 60:
            message += f"🎯 *Rec:* {top_rec}\n"
    
    message += f"\n⏰ {datetime.now().strftime('%H:%M:%S ET')}"
    
    return message

def test_alert_format():
    print("🧪 TESTING ENHANCED TELEGRAM ALERT FORMAT")
    print("=" * 70)
    
    # Test data
    print(f"\n📊 Test Data:")
    print(f"Symbol: {gap_data['symbol']}")
    print(f"Gap: {gap_data['gap_direction']} {abs(gap_data['gap_percent'])}%")
    print(f"Edge Score: {edge_analysis['total_edge_score']}")
    print(f"Pattern: {pattern_analysis['pattern_type']}")
    
    # Generate alert
    alert_message = format_enhanced_alert(gap_data, pattern_analysis, edge_analysis)
    
    print(f"\n📱 TELEGRAM ALERT PREVIEW:")
    print("=" * 50)
    print(alert_message)
    print("=" * 50)
    
    print(f"\n✅ Alert generated successfully!")
    print(f"📏 Message length: {len(alert_message)} characters")
    
    # Show analysis breakdown
    print(f"\n📋 ANALYSIS BREAKDOWN:")
    print(f"🎯 Edge Score: {edge_analysis['total_edge_score']}/100 ({edge_analysis['edge_classification']})")
    print(f"🧠 AI Quality: {pattern_analysis['setup_quality']}/100")
    print(f"📊 Flash Research: {pattern_analysis['flash_analysis']['gap_edge_score']}/100")
    print(f"🔄 Continuation Rate: {pattern_analysis['flash_analysis']['gap_continuation_rate']}%")
    print(f"🎮 Float: {pattern_analysis['float_analysis']['float_shares']/1_000_000:.1f}M shares")
    
    print(f"\n🚀 KEY FEATURES IMPLEMENTED:")
    print("✅ Multi-source edge scoring (Flash Research + AI + Gap + Float)")
    print("✅ Historical statistics for context")
    print("✅ Rich WHY explanations")
    print("✅ AI pattern recognition")
    print("✅ Concise but informative format")
    print("✅ Spanish context for better understanding")
    
    return alert_message

if __name__ == "__main__":
    test_alert_format()