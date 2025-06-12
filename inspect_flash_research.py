#!/usr/bin/env python3
"""
Inspeccionar Flash Research para entender su estructura real
"""
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def inspect_flash_research_with_requests():
    """Inspect Flash Research using requests first"""
    print("🌐 INSPECTING FLASH RESEARCH WITH REQUESTS")
    print("=" * 50)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Test main domain
        print("1️⃣ Testing main domain...")
        response = requests.get("https://flash-research.com", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"   Content length: {len(response.text)} characters")
        
        # Check if it's a real financial data site
        content_lower = response.text.lower()
        keywords = ['stock', 'ticker', 'symbol', 'gap', 'float', 'research', 'financial', 'trading', 'market']
        found_keywords = [kw for kw in keywords if kw in content_lower]
        print(f"   Financial keywords found: {found_keywords}")
        
        # Check for login/auth mentions
        auth_keywords = ['login', 'signin', 'register', 'auth', 'account']
        found_auth = [kw for kw in auth_keywords if kw in content_lower]
        print(f"   Auth keywords found: {found_auth}")
        
        # Test if it's a placeholder/parking page
        placeholder_indicators = ['coming soon', 'under construction', 'domain for sale', 'parked', 'godaddy']
        is_placeholder = any(indicator in content_lower for indicator in placeholder_indicators)
        print(f"   Appears to be placeholder: {is_placeholder}")
        
        # Save HTML for inspection
        with open('/tmp/flash_research_raw.html', 'w') as f:
            f.write(response.text)
        print(f"   HTML saved to: /tmp/flash_research_raw.html")
        
        return response.status_code == 200 and not is_placeholder
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


def inspect_with_selenium():
    """Inspect with Selenium to handle JavaScript"""
    print("\n🔍 INSPECTING WITH SELENIUM")
    print("=" * 50)
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        print("1️⃣ Loading Flash Research...")
        driver.get("https://flash-research.com")
        time.sleep(3)
        
        # Get basic info
        title = driver.title
        url = driver.current_url
        print(f"   Title: {title}")
        print(f"   Final URL: {url}")
        
        # Check page source
        page_source = driver.page_source
        print(f"   Page source length: {len(page_source)} characters")
        
        # Look for key elements
        print("\n2️⃣ Looking for key elements...")
        
        # Search for any input fields
        inputs = driver.find_elements(By.TAG_NAME, 'input')
        print(f"   Input fields found: {len(inputs)}")
        for i, inp in enumerate(inputs[:5]):  # Show first 5
            print(f"     {i+1}. Type: {inp.get_attribute('type')}, Name: {inp.get_attribute('name')}, Placeholder: {inp.get_attribute('placeholder')}")
        
        # Search for forms
        forms = driver.find_elements(By.TAG_NAME, 'form')
        print(f"   Forms found: {len(forms)}")
        
        # Search for links
        links = driver.find_elements(By.TAG_NAME, 'a')
        print(f"   Links found: {len(links)}")
        
        # Look for specific text patterns
        page_text = driver.page_source.lower()
        
        # Check if it's a real research platform
        research_indicators = [
            'stock analysis', 'market research', 'financial data', 
            'trading signals', 'stock screener', 'gap analysis'
        ]
        found_indicators = [ind for ind in research_indicators if ind in page_text]
        print(f"   Research indicators: {found_indicators}")
        
        # Check for authentication elements
        auth_elements = []
        auth_texts = ['sign in', 'log in', 'register', 'create account']
        for text in auth_texts:
            try:
                element = driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
                auth_elements.append(text)
            except:
                pass
        print(f"   Auth elements found: {auth_elements}")
        
        # Take screenshot
        screenshot_path = '/tmp/flash_research_selenium.png'
        driver.save_screenshot(screenshot_path)
        print(f"   Screenshot saved: {screenshot_path}")
        
        # Save page source
        with open('/tmp/flash_research_selenium.html', 'w') as f:
            f.write(page_source)
        print(f"   Page source saved: /tmp/flash_research_selenium.html")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False
    finally:
        if driver:
            driver.quit()


def analyze_findings():
    """Analyze what we found"""
    print("\n📊 ANALYSIS AND RECOMMENDATIONS")
    print("=" * 50)
    
    # Check if HTML files exist
    try:
        with open('/tmp/flash_research_raw.html', 'r') as f:
            raw_html = f.read().lower()
        
        with open('/tmp/flash_research_selenium.html', 'r') as f:
            selenium_html = f.read().lower()
        
        print("✅ HTML files available for analysis")
        
        # Detailed analysis
        print("\n🔍 Detailed Analysis:")
        
        # Check for React/Angular/Vue (SPA indicators)
        spa_indicators = ['react', 'angular', 'vue', 'app.js', 'bundle.js', 'main.js']
        found_spa = [ind for ind in spa_indicators if ind in selenium_html]
        print(f"   SPA Framework indicators: {found_spa}")
        
        # Check for API endpoints
        api_patterns = ['api/', '/api', 'endpoint', 'rest', 'graphql']
        found_api = [pattern for pattern in api_patterns if pattern in selenium_html]
        print(f"   API patterns found: {found_api}")
        
        # Check for authentication systems
        auth_systems = ['oauth', 'jwt', 'session', 'token', 'firebase', 'auth0']
        found_auth_sys = [sys for sys in auth_systems if sys in selenium_html]
        print(f"   Auth systems: {found_auth_sys}")
        
        # Determine site type
        print("\n🎯 Site Assessment:")
        
        if 'coming soon' in selenium_html or 'under construction' in selenium_html:
            print("   📋 Type: Under construction / Coming soon page")
            recommendation = "Wait for site to be completed"
        elif 'domain for sale' in selenium_html or 'parked domain' in selenium_html:
            print("   📋 Type: Parked domain / For sale")
            recommendation = "Domain not yet developed"
        elif len(found_spa) > 0:
            print("   📋 Type: Single Page Application (React/Vue/Angular)")
            recommendation = "Need to wait for JavaScript to load and find API endpoints"
        elif 'login' in selenium_html and 'research' in selenium_html:
            print("   📋 Type: Potential research platform with authentication")
            recommendation = "Examine authentication flow and try different login approaches"
        else:
            print("   📋 Type: Static website or unknown")
            recommendation = "Manual inspection needed"
        
        print(f"\n💡 Recommendation: {recommendation}")
        
        # Provide next steps
        print("\n🚀 Next Steps for Web Scraping:")
        
        if found_spa:
            print("   1. Wait for JavaScript to fully load (increase timeouts)")
            print("   2. Look for API endpoints in network traffic")
            print("   3. Use Selenium with explicit waits for dynamic content")
            print("   4. Consider using requests to directly call APIs")
        
        if 'login' in selenium_html:
            print("   1. Inspect login form HTML structure manually")
            print("   2. Try different element selectors (CSS vs XPath)")
            print("   3. Look for CSRF tokens or other security measures")
            print("   4. Consider handling CAPTCHAs")
        
        print("   5. Manual browser inspection recommended")
        print("   6. Check browser developer tools for network requests")
        
    except FileNotFoundError:
        print("❌ HTML files not found - analysis incomplete")


def main():
    """Main inspection function"""
    print("🔍 FLASH RESEARCH SITE INSPECTION")
    print("=" * 60)
    
    # Step 1: Basic HTTP inspection
    requests_success = inspect_flash_research_with_requests()
    
    # Step 2: Selenium inspection  
    selenium_success = inspect_with_selenium()
    
    # Step 3: Analysis
    if requests_success or selenium_success:
        analyze_findings()
    else:
        print("\n❌ Unable to access Flash Research - site may be down")
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSION:")
    print("Based on this analysis, we can determine the best approach")
    print("for scraping Flash Research data or building alternative solutions.")


if __name__ == "__main__":
    main()