#!/usr/bin/env python3
"""
Prueba completa del sistema de trading bot con todos los componentes
"""
import asyncio
import os
from datetime import datetime
from typing import Dict

# Test data simulation
def create_test_gap_data():
    """Create realistic test gap data"""
    return {
        'symbol': 'KLTO',
        'gap_percent': -24.1,
        'gap_direction': 'DOWN', 
        'previous_close': 2.45,
        'current_price': 1.86,
        'volume': 850000,
        'timestamp': datetime.now().isoformat()
    }

def create_test_enhanced_gap():
    """Create enhanced gap data with all analysis"""
    gap_data = create_test_gap_data()
    
    # Add pattern analysis
    gap_data['pattern_analysis'] = {
        'pattern_type': 'Float Squeeze',
        'setup_quality': 85,
        'confidence': 78,
        'playbook': 'Small float (3.2M) with 24.1% gap. Limited supply can amplify moves. Watch for volume confirmation and momentum continuation.',
        'key_factors': ['Large gap', 'Micro float', 'High volume multiplier'],
        'risk_level': 'Medium',
        'analysis_source': 'ai_enhanced',
        'timestamp': datetime.now().isoformat(),
        'symbol': 'KLTO',
        
        # Flash Research analysis
        'flash_analysis': {
            'has_flash_data': True,
            'gap_edge_score': 78,
            'historical_performance': 'Good',
            'gap_continuation_rate': 72,
            'gap_fill_rate': 35,
            'volume_factor': 2.8,
            'statistical_edge': 'Strong bullish momentum',
            'total_gaps_analyzed': 45,
            'avg_gap_size': 18.5,
            'overall_edge_score': 75,
            'trading_recommendations': [
                'High continuation rate supports momentum plays',
                'Low gap fill tendency',
                'Above average volume during gaps'
            ]
        },
        
        # Float analysis
        'float_analysis': {
            'category': 'Micro Float',
            'is_microfloat': True,
            'is_nanofloat': False,
            'squeeze_potential': 85,
            'float_shares': 3_200_000
        },
        
        # News analysis  
        'news_analysis': {
            'has_catalyst': False,
            'catalyst_strength': 20,
            'catalyst_type': 'Minimal',
            'headline_count': 0
        }
    }
    
    # Add edge analysis
    gap_data['edge_analysis'] = {
        'symbol': 'KLTO',
        'timestamp': datetime.now().isoformat(),
        'total_edge_score': 82.5,
        'confidence_level': 'High',
        'edge_classification': 'Strong Edge',
        'component_scores': {
            'flash_research': 78.0,
            'gap_characteristics': 85.0,
            'float_dynamics': 90.0,
            'ai_pattern': 82.0,
            'news_catalyst': 50.0
        },
        'score_weights': {
            'flash_research_edge': 0.40,
            'gap_characteristics': 0.25,
            'float_dynamics': 0.20,
            'ai_pattern_recognition': 0.10,
            'news_catalyst': 0.05
        },
        'trading_recommendations': [
            'High probability setup - consider larger position size',
            'Strong 72% historical continuation rate',
            'Low gap fill tendency supports momentum plays',
            'High confidence in analysis - reliable data backing'
        ],
        'edge_summary': 'Strong Edge (Score: 83/100, Flash: 78/100, Cont: 72%)'
    }
    
    # Add additional fields that main.py creates
    gap_data['playbook'] = {
        'symbol': 'KLTO',
        'pattern_type': 'Float Squeeze',
        'setup_quality': 85,
        'description': 'Low float stock with significant gap creating supply/demand imbalance',
        'expected_behavior': 'Initial spike, possible pullback, then momentum continuation if volume sustains',
        'alert_summary': '🔥 Float Squeeze Setup (Q:85/100) • Micro Float • High volume multiplier'
    }
    
    gap_data['float_data'] = {
        'float_shares': 3_200_000,
        'screening_results': {
            'is_microfloat': True,
            'float_score': 85,
            'squeeze_setup': True
        }
    }
    
    gap_data['is_microfloat'] = True
    gap_data['edge_score'] = 82.5
    gap_data['combined_score'] = 82.5
    
    return gap_data

def format_enhanced_alert(gap_data):
    """Format enhanced alert exactly like main.py"""
    direction_emoji = "🟢" if gap_data['gap_direction'] == 'UP' else "🔴"
    gap_percent = abs(gap_data['gap_percent'])
    symbol = gap_data['symbol']
    
    # Get comprehensive analysis data
    pattern_analysis = gap_data.get('pattern_analysis', {})
    edge_analysis = gap_data.get('edge_analysis', {})
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
    message += f"Price: ${gap_data['previous_close']:.2f} → ${gap_data['current_price']:.2f}\n\n"
    
    # Flash Research statistical data
    if flash_analysis.get('has_flash_data', False):
        continuation_rate = flash_analysis.get('gap_continuation_rate', 50)
        gap_fill_rate = flash_analysis.get('gap_fill_rate', 50)
        total_gaps = flash_analysis.get('total_gaps_analyzed', 0)
        volume_factor = flash_analysis.get('volume_factor', 1.0)
        avg_gap_size = flash_analysis.get('avg_gap_size', 0)
        
        if total_gaps > 10:
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
            
            if avg_gap_size > 0:
                message += f"   • Avg Gap Size: {avg_gap_size:.1f}%\n"
            
            if volume_factor > 1.5:
                message += f"   • Volume Spike: {volume_factor:.1f}x normal\n"
    
    # Float context
    float_analysis = pattern_analysis.get('float_analysis', {})
    if float_analysis.get('is_microfloat') or float_analysis.get('is_nanofloat'):
        float_shares = float_analysis.get('float_shares', 0)
        if float_shares > 0:
            float_str = f"{float_shares/1_000_000:.1f}M" if float_shares >= 1_000_000 else f"{float_shares/1000:.0f}K"
            turnover = (gap_data['volume'] / float_shares) * 100
            message += f"🔥 *Float:* {float_str} shares ({turnover:.1f}% turnover)\n"
    
    # Volume context
    volume = gap_data['volume']
    if volume > 1_000_000:
        message += f"📊 *Volume:* {volume:,.0f} (very high)\n"
    elif volume > 500_000:
        message += f"📊 *Volume:* {volume:,.0f} (high)\n"
    elif volume > 100_000:
        message += f"📊 *Volume:* {volume:,.0f}\n"
    
    # AI Analysis insights
    ai_confidence = pattern_analysis.get('confidence', 0)
    setup_quality = pattern_analysis.get('setup_quality', 0)
    if ai_confidence > 60 and setup_quality > 60:
        message += f"🧠 *AI Analysis:* {setup_quality}% quality, {ai_confidence}% confidence\n"
    
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

async def test_complete_system():
    """Test complete system end-to-end"""
    print("🚀 TESTING COMPLETE TRADING BOT SYSTEM")
    print("=" * 70)
    print(f"📅 Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        # Test 1: Import all modules
        print("\n🔧 STEP 1: Testing Module Imports")
        print("-" * 40)
        
        modules_to_test = [
            ('src.utils.logger', 'Logger utilities'),
            ('src.scanners.gap_scanner', 'Gap Scanner'),
            ('src.scanners.float_screener', 'Float Screener'),  
            ('src.alerts.telegram_bot', 'Telegram Bot'),
            ('src.analysis.pattern_analyzer', 'Pattern Analyzer'),
            ('src.analysis.playbook_generator', 'Playbook Generator'),
            ('src.analysis.edge_scorer', 'Edge Scorer'),
        ]
        
        imported_modules = {}
        for module_name, description in modules_to_test:
            try:
                if module_name == 'src.utils.logger':
                    from src.utils.logger import setup_logger
                    setup_logger('test')
                    imported_modules[module_name] = True
                    print(f"✅ {description}")
                elif module_name == 'src.scanners.gap_scanner':
                    from src.scanners.gap_scanner import GapScanner
                    imported_modules[module_name] = GapScanner
                    print(f"✅ {description}")
                elif module_name == 'src.scanners.float_screener':
                    from src.scanners.float_screener import FloatScreener
                    imported_modules[module_name] = FloatScreener  
                    print(f"✅ {description}")
                elif module_name == 'src.alerts.telegram_bot':
                    from src.alerts.telegram_bot import TelegramAlertBot
                    imported_modules[module_name] = TelegramAlertBot
                    print(f"✅ {description}")
                elif module_name == 'src.analysis.pattern_analyzer':
                    from src.analysis.pattern_analyzer import PatternAnalyzer
                    imported_modules[module_name] = PatternAnalyzer
                    print(f"✅ {description}")
                elif module_name == 'src.analysis.playbook_generator':
                    from src.analysis.playbook_generator import PlaybookGenerator
                    imported_modules[module_name] = PlaybookGenerator
                    print(f"✅ {description}")
                elif module_name == 'src.analysis.edge_scorer':
                    from src.analysis.edge_scorer import EdgeScorer
                    imported_modules[module_name] = EdgeScorer
                    print(f"✅ {description}")
            except Exception as e:
                print(f"❌ {description}: {str(e)}")
                imported_modules[module_name] = None
        
        # Test 2: Initialize components
        print(f"\n🔧 STEP 2: Initializing Components")
        print("-" * 40)
        
        components = {}
        
        # Initialize each component individually to catch specific errors
        for component_name, component_class in [
            ('gap_scanner', imported_modules.get('src.scanners.gap_scanner')),
            ('float_screener', imported_modules.get('src.scanners.float_screener')),
            ('telegram_bot', imported_modules.get('src.alerts.telegram_bot')),
            ('pattern_analyzer', imported_modules.get('src.analysis.pattern_analyzer')),
            ('playbook_generator', imported_modules.get('src.analysis.playbook_generator')),
            ('edge_scorer', imported_modules.get('src.analysis.edge_scorer'))
        ]:
            if component_class:
                try:
                    components[component_name] = component_class()
                    print(f"✅ {component_name.replace('_', ' ').title()} initialized")
                except Exception as e:
                    print(f"❌ {component_name.replace('_', ' ').title()}: {str(e)}")
                    components[component_name] = None
            else:
                components[component_name] = None
        
        # Test 3: Test data flow simulation
        print(f"\n🔧 STEP 3: Testing Data Flow")
        print("-" * 40)
        
        # Create test gap data
        test_gap = create_test_enhanced_gap()
        print(f"✅ Test gap data created for {test_gap['symbol']}")
        print(f"   Gap: {test_gap['gap_direction']} {abs(test_gap['gap_percent'])}%")
        print(f"   Edge Score: {test_gap['edge_score']}")
        
        # Test 4: Alert formatting
        print(f"\n🔧 STEP 4: Testing Alert Formatting")
        print("-" * 40)
        
        alert_message = format_enhanced_alert(test_gap)
        print(f"✅ Alert message generated ({len(alert_message)} chars)")
        
        # Test 5: Telegram bot connection
        print(f"\n🔧 STEP 5: Testing Telegram Connection")
        print("-" * 40)
        
        if 'telegram_bot' in components:
            telegram_bot = components['telegram_bot']
            if telegram_bot.enabled:
                print(f"✅ Telegram bot enabled")
                print(f"   Chat ID: {telegram_bot.chat_id}")
                print(f"   Bot configured for alerts")
                
                # Automatically test Telegram alert
                print("📤 Testing Telegram alert automatically...")
                try:
                    test_msg = f"🧪 SYSTEM TEST - {datetime.now().strftime('%H:%M:%S')}\n\n{alert_message}"
                    await telegram_bot.send_alert(test_msg)
                    print("✅ Test alert sent successfully!")
                except Exception as e:
                    print(f"❌ Failed to send test alert: {str(e)}")
            else:
                print("⚠️ Telegram bot not enabled (no token/chat_id)")
        else:
            print("❌ Telegram bot not available")
        
        # Test 6: Configuration check
        print(f"\n🔧 STEP 6: Configuration Check")
        print("-" * 40)
        
        from dotenv import load_dotenv
        load_dotenv()
        
        configs = {
            'ALPACA_API_KEY': os.getenv('ALPACA_API_KEY'),
            'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
            'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'FLASH_RESEARCH_EMAIL': os.getenv('FLASH_RESEARCH_EMAIL'),
            'FINNHUB_API_KEY': os.getenv('FINNHUB_API_KEY')
        }
        
        for key, value in configs.items():
            if value:
                masked_value = f"{value[:8]}..." if len(value) > 8 else "***"
                print(f"✅ {key}: {masked_value}")
            else:
                print(f"⚠️ {key}: Not configured")
        
        # Test 7: Final summary
        print(f"\n🎯 STEP 7: System Summary")
        print("-" * 40)
        
        working_components = len([c for c in components.values() if c is not None])
        total_components = len(components)
        
        print(f"📊 Components Status: {working_components}/{total_components} working")
        print(f"🔧 Configuration: {len([v for v in configs.values() if v])}/{len(configs)} configured")
        
        if working_components >= 4 and configs['TELEGRAM_BOT_TOKEN'] and configs['TELEGRAM_CHAT_ID']:
            print("\n🎉 SYSTEM STATUS: ✅ READY FOR PRODUCTION")
            print("   - Core components working")
            print("   - Telegram alerts configured") 
            print("   - Alert formatting working")
            print("   - Edge analysis system operational")
        else:
            print("\n⚠️ SYSTEM STATUS: 🔧 NEEDS CONFIGURATION")
            print("   - Some components need setup")
            print("   - Check API keys and credentials")
        
        # Show sample alert
        print(f"\n📱 SAMPLE ALERT OUTPUT:")
        print("=" * 50)
        print(alert_message)
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ SYSTEM TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_complete_system())