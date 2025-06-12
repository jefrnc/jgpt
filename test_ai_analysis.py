#!/usr/bin/env python3
"""
Test AI-enhanced pattern analysis system
"""
import asyncio
from datetime import datetime
from src.api.openai_client import OpenAIClient
from src.api.flash_research_client import FlashResearchClient
from src.analysis.pattern_analyzer import PatternAnalyzer
from src.analysis.playbook_generator import PlaybookGenerator
from src.analysis.edge_scorer import EdgeScorer
from src.scanners.gap_scanner import GapScanner
from src.scanners.float_screener import FloatScreener
from src.alerts.telegram_bot import TelegramAlertBot
from src.utils.logger import setup_logger


async def test_ai_pattern_analysis():
    """Test the full AI analysis pipeline"""
    logger = setup_logger('ai_test')
    
    print("🧠 TESTING AI-ENHANCED PATTERN ANALYSIS")
    print("=" * 60)
    
    # Initialize components
    openai_client = OpenAIClient()
    flash_research = FlashResearchClient()
    pattern_analyzer = PatternAnalyzer()
    playbook_generator = PlaybookGenerator()
    edge_scorer = EdgeScorer()
    gap_scanner = GapScanner()
    float_screener = FloatScreener()
    telegram_bot = TelegramAlertBot()
    
    # Test OpenAI connection first
    print("\n🔌 Testing OpenAI Connection...")
    if openai_client.enabled:
        connection_ok = openai_client.test_connection()
        if connection_ok:
            print("✅ OpenAI connection successful")
        else:
            print("❌ OpenAI connection failed")
            return
    else:
        print("⚠️ OpenAI not enabled, running local analysis only")
    
    # Test Flash Research connection
    print("\n🔌 Testing Flash Research Connection...")
    flash_connection_ok = flash_research.test_connection()
    if flash_connection_ok:
        print("✅ Flash Research connection successful")
    else:
        print("⚠️ Flash Research connection failed - will use limited data")
    
    # Get test symbols (recent volatile small caps)
    test_symbols = ['KLTO', 'KZIA', 'VTAK', 'HSDT', 'CARM']
    
    print(f"\n📊 Testing AI analysis on {len(test_symbols)} symbols...")
    
    for symbol in test_symbols:
        print(f"\n{'='*40}")
        print(f"🔍 ANALYZING {symbol}")
        print(f"{'='*40}")
        
        try:
            # Simulate gap data (you can replace with real gap scanner results)
            gap_data = gap_scanner.scan_symbol(symbol)
            
            if not gap_data:
                print(f"❌ No gap data available for {symbol}")
                continue
            
            print(f"📈 Gap detected: {gap_data['gap_direction']} {abs(gap_data['gap_percent']):.1f}%")
            
            # Get float data
            float_data = float_screener.screen_symbol(symbol)
            if float_data:
                float_shares = float_data.get('float_shares', 0)
                float_str = f"{float_shares/1_000_000:.1f}M" if float_shares >= 1_000_000 else f"{float_shares/1000:.0f}K"
                print(f"🔍 Float: {float_str} shares")
            
            # Run AI pattern analysis
            print("🧠 Running AI pattern analysis...")
            pattern_analysis = pattern_analyzer.analyze_gap_setup(gap_data, float_data)
            
            if pattern_analysis:
                print(f"✅ Pattern identified: {pattern_analysis['pattern_type']}")
                print(f"📊 Setup quality: {pattern_analysis['setup_quality']}/100")
                print(f"🎯 Confidence: {pattern_analysis['confidence']}%")
                print(f"⚠️ Risk level: {pattern_analysis['risk_level']}")
                
                # Display key factors
                key_factors = pattern_analysis.get('key_factors', [])
                if key_factors:
                    print(f"🔑 Key factors: {', '.join(key_factors)}")
                
                # Display playbook
                playbook = pattern_analysis.get('playbook', '')
                if playbook:
                    print(f"📚 Playbook: {playbook[:100]}...")
                
                # Generate enhanced playbook
                print("\n📖 Generating enhanced playbook...")
                enhanced_playbook = playbook_generator.generate_enhanced_playbook(pattern_analysis)
                
                if enhanced_playbook:
                    print(f"🎯 Enhanced description: {enhanced_playbook['description'][:80]}...")
                    print(f"📈 Expected behavior: {enhanced_playbook['expected_behavior'][:80]}...")
                    
                    # Show current observations
                    observations = enhanced_playbook.get('current_observations', [])
                    if observations:
                        print(f"👁️ Observations: {observations[0]}")
                    
                    # Show alert summary
                    alert_summary = enhanced_playbook.get('alert_summary', '')
                    print(f"📱 Alert summary: {alert_summary}")
                
                # Calculate comprehensive edge score
                print("\n🎯 Calculating comprehensive edge score...")
                edge_analysis = edge_scorer.calculate_edge_score(
                    gap_data,
                    pattern_analysis.get('flash_analysis', {}),
                    pattern_analysis.get('float_analysis', {}),
                    pattern_analysis.get('news_analysis', {}),
                    pattern_analysis
                )
                
                if edge_analysis:
                    print(f"📊 Total Edge Score: {edge_analysis['total_edge_score']:.1f}/100")
                    print(f"🏆 Edge Classification: {edge_analysis['edge_classification']}")
                    print(f"🔍 Confidence Level: {edge_analysis['confidence_level']}")
                    
                    # Show component breakdown
                    components = edge_analysis.get('component_scores', {})
                    print("📋 Component Scores:")
                    for component, score in components.items():
                        print(f"   - {component}: {score:.1f}")
                    
                    # Show top recommendations
                    recommendations = edge_analysis.get('trading_recommendations', [])
                    if recommendations:
                        print(f"💡 Top Recommendation: {recommendations[0]}")
                    
                    print(f"📈 Edge Summary: {edge_analysis.get('edge_summary', 'N/A')}")
                
                # Test Telegram alert formatting
                print("\n📱 Testing Telegram alert format...")
                
                # Create enhanced gap data for alert (simulate main.py structure)
                enhanced_gap = gap_data.copy()
                enhanced_gap['pattern_analysis'] = pattern_analysis
                enhanced_gap['playbook'] = enhanced_playbook
                enhanced_gap['edge_analysis'] = edge_analysis
                enhanced_gap['edge_score'] = edge_analysis['total_edge_score']
                enhanced_gap['combined_score'] = edge_analysis['total_edge_score']
                
                if float_data:
                    enhanced_gap['float_data'] = float_data
                    enhanced_gap['is_microfloat'] = float_data.get('screening_results', {}).get('is_microfloat', False)
                
                # Format alert message (simulate the main.py method)
                alert_message = format_test_alert(enhanced_gap)
                print("📨 Telegram alert preview:")
                print("-" * 40)
                print(alert_message)
                print("-" * 40)
                
                # Optionally send test alert
                send_test = input(f"\n🤔 Send test alert for {symbol} to Telegram? (y/n): ").lower().strip()
                if send_test == 'y' and telegram_bot.enabled:
                    try:
                        await telegram_bot.send_alert(f"🧪 AI TEST - {symbol}\n\n{alert_message}")
                        print("✅ Test alert sent to Telegram")
                    except Exception as e:
                        print(f"❌ Failed to send alert: {str(e)}")
                
            else:
                print("❌ AI pattern analysis failed")
                
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {str(e)}")
            logger.error(f"Error in AI analysis test for {symbol}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 AI ANALYSIS TEST COMPLETED")
    print("=" * 60)


def format_test_alert(gap_data):
    """Format test alert exactly like main.py enhanced method"""
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


if __name__ == "__main__":
    asyncio.run(test_ai_pattern_analysis())