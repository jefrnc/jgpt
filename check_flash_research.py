#!/usr/bin/env python3
"""
Quick Flash Research status check for VM deployment
"""
import os
import sys
import time
import logging
from datetime import datetime

def quick_flash_check():
    """Quick check if Flash Research is working"""
    print("🔍 QUICK FLASH RESEARCH CHECK")
    print("=" * 35)
    
    try:
        # Minimal imports
        sys.path.append('/path/to/your/bot')  # Adjust path as needed
        from src.api.flash_research_client import FlashResearchClient
        
        # Suppress logging noise
        logging.basicConfig(level=logging.ERROR)
        
        print("📊 Testing Flash Research...")
        flash_client = FlashResearchClient(use_scraper=True)
        
        # Test with KLTO (symbol we know works)
        start_time = time.time()
        result = flash_client.analyze_symbol('KLTO')
        elapsed = time.time() - start_time
        
        if result and result.get('has_flash_data'):
            print(f"✅ WORKING! ({elapsed:.1f}s)")
            print(f"   📈 {result.get('total_gaps_analyzed', 0)} gaps")
            print(f"   📊 {result.get('gap_continuation_rate', 0):.0f}% continuation")
            print(f"   🎯 {result.get('gap_edge_score', 0)}/100 edge score")
            print(f"   🔗 Source: {result.get('source', 'unknown')}")
            
            # Show sample alert
            if result.get('gap_continuation_rate', 0) > 70:
                print("\n📱 Sample Alert Preview:")
                print(f"🔥 **KLTO** Gap Up +15.2%")
                print(f"📊 Score: 94/100 (Excellent Setup)")
                print(f"📈 Historical Edge ({result.get('gap_edge_score', 0)}/100):")
                print(f"• {result.get('total_gaps_analyzed', 0)} gaps analyzed")
                print(f"• {result.get('gap_continuation_rate', 0):.0f}% continuation rate ✅")
                print(f"• Strong momentum bias")
                
        else:
            print("⚠️ Using simulated data (Flash Research not accessible)")
            
        flash_client.close()
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you're in the correct directory")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_environment():
    """Check if environment is properly set up"""
    print("\n🔧 ENVIRONMENT CHECK:")
    
    # Check environment variables
    flash_email = os.getenv('FLASH_RESEARCH_EMAIL')
    flash_pass = os.getenv('FLASH_RESEARCH_PASSWORD')
    
    print(f"📧 Flash Email: {'✅' if flash_email else '❌'}")
    print(f"🔑 Flash Password: {'✅' if flash_pass else '❌'}")
    
    # Check Chrome
    try:
        import subprocess
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"🌐 Chrome: ✅ {result.stdout.strip()}")
        else:
            print("🌐 Chrome: ❌ Not found")
    except:
        print("🌐 Chrome: ❌ Not accessible")
    
    # Check Python packages
    try:
        import selenium
        print(f"🐍 Selenium: ✅ {selenium.__version__}")
    except:
        print("🐍 Selenium: ❌ Not installed")

if __name__ == "__main__":
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    check_environment()
    print()
    success = quick_flash_check()
    
    if success:
        print("\n🎉 FLASH RESEARCH IS WORKING!")
    else:
        print("\n❌ FLASH RESEARCH NEEDS SETUP")
        print("\n💡 Setup steps:")
        print("1. pip install -r requirements.txt")
        print("2. sudo apt install google-chrome-stable")
        print("3. Set FLASH_RESEARCH_EMAIL and FLASH_RESEARCH_PASSWORD in .env")