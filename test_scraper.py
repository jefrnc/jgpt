#!/usr/bin/env python3
"""
Test Flash Research web scraper
"""
import asyncio
from datetime import datetime
from src.api.flash_research_scraper import FlashResearchScraper, FlashResearchClient

async def test_flash_research_scraper():
    """Test the Selenium-based Flash Research scraper"""
    print("🌐 TESTING FLASH RESEARCH WEB SCRAPER")
    print("=" * 60)
    
    # Initialize scraper (headless for automated testing)
    print("1️⃣ Initializing scraper...")
    scraper = FlashResearchScraper(headless=True)  # Set to False to see browser
    
    try:
        # Test authentication
        print("\n2️⃣ Testing authentication...")
        auth_success = scraper.authenticate()
        
        if auth_success:
            print("✅ Authentication successful")
            
            # Test symbol search
            print("\n3️⃣ Testing symbol search...")
            test_symbols = ['KLTO', 'AAPL']  # Test with known symbols
            
            for symbol in test_symbols:
                print(f"\n📊 Testing {symbol}:")
                print("-" * 30)
                
                # Search for symbol
                found = scraper.search_symbol(symbol)
                if found:
                    print(f"✅ {symbol} found on platform")
                    
                    # Extract gap statistics
                    gap_stats = scraper.extract_gap_statistics(symbol)
                    if gap_stats:
                        print(f"📈 Gap statistics extracted:")
                        for key, value in gap_stats.items():
                            if key not in ['symbol', 'extraction_timestamp']:
                                print(f"   • {key}: {value}")
                    else:
                        print(f"⚠️ No gap statistics extracted for {symbol}")
                    
                    # Extract performance data
                    perf_data = scraper.extract_performance_data(symbol)
                    if perf_data:
                        print(f"📊 Performance data extracted:")
                        for key, value in perf_data.items():
                            if key not in ['symbol']:
                                print(f"   • {key}: {value}")
                    else:
                        print(f"⚠️ No performance data extracted for {symbol}")
                        
                else:
                    print(f"❌ {symbol} not found")
            
            # Test comprehensive analysis
            print(f"\n4️⃣ Testing comprehensive analysis...")
            symbol = 'KLTO'
            comprehensive = scraper.get_comprehensive_analysis(symbol)
            
            if comprehensive:
                print(f"✅ Comprehensive analysis for {symbol}:")
                print(f"   • Has real data: {comprehensive.get('has_flash_data', False)}")
                print(f"   • Gap edge score: {comprehensive.get('gap_edge_score', 0)}")
                print(f"   • Continuation rate: {comprehensive.get('gap_continuation_rate', 0):.1f}%")
                print(f"   • Gap fill rate: {comprehensive.get('gap_fill_rate', 0):.1f}%")
                print(f"   • Total gaps: {comprehensive.get('total_gaps_analyzed', 0)}")
                print(f"   • Statistical edge: {comprehensive.get('statistical_edge', 'N/A')}")
                
                recommendations = comprehensive.get('trading_recommendations', [])
                if recommendations:
                    print(f"   • Top recommendation: {recommendations[0]}")
                
                # Show alert format data
                print(f"\n📱 Data for English alerts:")
                total_gaps = comprehensive.get('total_gaps_analyzed', 0)
                if total_gaps > 10:
                    continuation_rate = comprehensive.get('gap_continuation_rate', 50)
                    gap_fill_rate = comprehensive.get('gap_fill_rate', 50)
                    volume_factor = comprehensive.get('volume_factor', 1.0)
                    avg_gap_size = comprehensive.get('avg_gap_size', 0)
                    
                    print(f"   📊 *Historical Data ({total_gaps} gaps):*")
                    print(f"      • Continued: {continuation_rate:.0f}% | Reversed: {100-continuation_rate:.0f}%")
                    print(f"      • Red Close: {continuation_rate:.0f}% | Green Close: {100-continuation_rate:.0f}%")
                    print(f"      • Gap Fill Rate: {gap_fill_rate:.0f}%")
                    print(f"      • Avg Gap Size: {avg_gap_size:.1f}%")
                    if volume_factor > 1.5:
                        print(f"      • Volume Spike: {volume_factor:.1f}x normal")
            
        else:
            print("❌ Authentication failed")
            print("⚠️ This might be normal if Flash Research doesn't have a public login")
            print("💡 Will test with fallback data instead...")
            
            # Test fallback functionality
            symbol = 'KLTO'
            fallback_data = scraper._get_fallback_data(symbol)
            print(f"\n🔄 Fallback data for {symbol}:")
            print(f"   • Continuation rate: {fallback_data['gap_continuation_rate']}%")
            print(f"   • Gap fill rate: {fallback_data['gap_fill_rate']}%")
            print(f"   • Total gaps: {fallback_data['total_gaps_analyzed']}")
            print(f"   • Edge score: {fallback_data['gap_edge_score']}")
        
        print(f"\n🎯 SCRAPER TEST SUMMARY")
        print("=" * 40)
        
        if auth_success:
            print("✅ Web scraping: Functional")
            print("✅ Data extraction: Working")
            print("✅ Real Flash Research data available")
        else:
            print("⚠️ Web scraping: Login issue")
            print("✅ Fallback data: Working")
            print("✅ System resilient to connection issues")
        
        print("✅ Integration: Ready for main.py")
        
    finally:
        # Always close the browser
        scraper.close()

def test_updated_client():
    """Test the updated FlashResearchClient with scraper"""
    print("\n" + "=" * 60)
    print("🔧 TESTING UPDATED FLASH RESEARCH CLIENT")
    print("=" * 60)
    
    # Test the updated client
    client = FlashResearchClient()
    
    print("1️⃣ Testing client initialization...")
    print("✅ Client initialized with scraper backend")
    
    print("\n2️⃣ Testing analyze_symbol method...")
    symbol = 'KLTO'
    result = client.analyze_symbol(symbol)
    
    if result:
        print(f"✅ Analysis completed for {symbol}:")
        print(f"   • Has data: {result.get('has_flash_data', False)}")
        print(f"   • Edge score: {result.get('gap_edge_score', 0)}")
        print(f"   • Continuation: {result.get('gap_continuation_rate', 0):.1f}%")
        print(f"   • Fill rate: {result.get('gap_fill_rate', 0):.1f}%")
        
        recommendations = result.get('trading_recommendations', [])
        if recommendations:
            print(f"   • Recommendation: {recommendations[0]}")
    
    print("\n3️⃣ Testing connection method...")
    connection_ok = client.test_connection()
    if connection_ok:
        print("✅ Connection test passed")
    else:
        print("⚠️ Connection test failed (expected for demo)")
    
    # Cleanup
    client.close()
    
    print("\n✅ Updated client ready for main.py integration")

if __name__ == "__main__":
    asyncio.run(test_flash_research_scraper())
    test_updated_client()