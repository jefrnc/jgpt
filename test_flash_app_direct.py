#!/usr/bin/env python3
"""
Test directo de app.flash-research.com para scraping real
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_flash_app_login():
    """Test login en app.flash-research.com"""
    print("🔐 TESTING FLASH RESEARCH APP LOGIN")
    print("=" * 50)
    
    # Setup driver
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")  # Comentar para ver el browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to the correct signin page
        app_url = "https://flash-research.com/signin"
        print(f"🌐 Navigating to: {app_url}")
        
        driver.get(app_url)
        time.sleep(5)  # Wait for app to load
        
        print(f"📍 Current URL: {driver.current_url}")
        print(f"📄 Page title: {driver.title}")
        
        # Take screenshot
        screenshot_path = "/tmp/flash_app_login.png"
        driver.save_screenshot(screenshot_path)
        print(f"🖼️ Screenshot saved: {screenshot_path}")
        
        # Look for login form elements
        print("\n🔍 Looking for login form elements...")
        
        # Try different selectors for email/username
        email_selectors = [
            'input[type="email"]',
            'input[name="email"]',
            'input[name="username"]',
            'input[placeholder*="email"]',
            'input[placeholder*="Email"]',
            'input[id*="email"]',
            'input[id*="username"]'
        ]
        
        email_field = None
        for selector in email_selectors:
            try:
                email_field = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Email field found: {selector}")
                break
            except NoSuchElementException:
                continue
        
        # Try different selectors for password
        password_selectors = [
            'input[type="password"]',
            'input[name="password"]',
            'input[placeholder*="password"]',
            'input[placeholder*="Password"]',
            'input[id*="password"]'
        ]
        
        password_field = None
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Password field found: {selector}")
                break
            except NoSuchElementException:
                continue
        
        # Look for submit button
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:contains("Sign In")',
            'button:contains("Login")',
            'button:contains("Log In")',
            '.login-button',
            '.signin-button',
            '.submit-button'
        ]
        
        submit_button = None
        for selector in submit_selectors:
            try:
                submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Submit button found: {selector}")
                break
            except NoSuchElementException:
                continue
        
        # If we found the form elements, try to login
        if email_field and password_field:
            print("\n🔐 Attempting login...")
            
            # Credentials
            email = "jsfrnc@gmail.com"
            password = "ge1hwZxFeN"
            
            # Fill form
            email_field.clear()
            email_field.send_keys(email)
            
            password_field.clear()
            password_field.send_keys(password)
            
            # Submit
            if submit_button:
                submit_button.click()
            else:
                # Try pressing Enter
                password_field.send_keys(Keys.RETURN)
            
            print("📤 Login form submitted")
            
            # Wait for response
            time.sleep(5)
            
            # Check result
            new_url = driver.current_url
            new_title = driver.title
            
            print(f"📍 After login URL: {new_url}")
            print(f"📄 After login title: {new_title}")
            
            # Take screenshot after login attempt
            screenshot_after = "/tmp/flash_app_after_login.png"
            driver.save_screenshot(screenshot_after)
            print(f"🖼️ After login screenshot: {screenshot_after}")
            
            # Check for success indicators
            page_source = driver.page_source.lower()
            success_indicators = [
                'dashboard', 'welcome', 'logout', 'profile', 'scanner', 'research'
            ]
            
            found_success = []
            for indicator in success_indicators:
                if indicator in page_source:
                    found_success.append(indicator)
            
            if found_success:
                print(f"✅ Login appears successful! Found: {found_success}")
                
                # Try to extract some data
                print("\n📊 Looking for research data...")
                
                # Look for stock/gap related content
                research_keywords = ['gap', 'stock', 'ticker', 'symbol', 'price', 'volume']
                found_research = []
                
                for keyword in research_keywords:
                    if keyword in page_source:
                        count = page_source.count(keyword)
                        found_research.append(f"{keyword}({count})")
                
                if found_research:
                    print(f"📈 Research data found: {', '.join(found_research)}")
                else:
                    print("⚠️ No research data found yet")
                
                # Look for navigation or data tables
                try:
                    tables = driver.find_elements(By.TAG_NAME, 'table')
                    if tables:
                        print(f"📋 Found {len(tables)} data tables")
                        
                        # Try to extract headers from first table
                        first_table = tables[0]
                        headers = first_table.find_elements(By.TAG_NAME, 'th')
                        if headers:
                            header_texts = [h.text.strip() for h in headers if h.text.strip()]
                            print(f"   Table headers: {header_texts}")
                except:
                    pass
                
                return True
                
            else:
                print("❌ Login failed or no success indicators found")
                
                # Look for error messages
                error_selectors = [
                    '.error', '.alert', '.warning', '.message',
                    '[class*="error"]', '[class*="alert"]'
                ]
                
                for selector in error_selectors:
                    try:
                        error_elem = driver.find_element(By.CSS_SELECTOR, selector)
                        if error_elem.text.strip():
                            print(f"❌ Error message: {error_elem.text.strip()}")
                    except:
                        continue
                
                return False
        
        else:
            print("❌ Login form elements not found")
            print(f"   Email field: {'Found' if email_field else 'Not found'}")
            print(f"   Password field: {'Found' if password_field else 'Not found'}")
            
            # Get page source for analysis
            with open('/tmp/flash_app_source.html', 'w') as f:
                f.write(driver.page_source)
            print("📝 Page source saved to /tmp/flash_app_source.html")
            
            return False
    
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False
    
    finally:
        driver.quit()
        print("🔒 Browser closed")

def analyze_flash_app():
    """Analyze what we found"""
    print("\n📊 FLASH RESEARCH APP ANALYSIS")
    print("=" * 40)
    
    # Check if we have saved files
    import os
    files_to_check = [
        '/tmp/flash_app_login.png',
        '/tmp/flash_app_after_login.png', 
        '/tmp/flash_app_source.html'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path}: {size} bytes")
        else:
            print(f"❌ {file_path}: Not found")
    
    # If we have HTML source, analyze it
    html_file = '/tmp/flash_app_source.html'
    if os.path.exists(html_file):
        print("\n🔍 Analyzing HTML source...")
        
        with open(html_file, 'r') as f:
            content = f.read().lower()
        
        # Look for authentication methods
        auth_methods = ['oauth', 'firebase', 'auth0', 'cognito', 'supabase']
        found_auth = [method for method in auth_methods if method in content]
        
        if found_auth:
            print(f"🔐 Auth methods detected: {found_auth}")
        
        # Look for API endpoints
        api_patterns = ['/api/', 'graphql', 'endpoint', 'fetch(']
        found_apis = [pattern for pattern in api_patterns if pattern in content]
        
        if found_apis:
            print(f"🔗 API patterns found: {found_apis}")
        
        # Look for React/Next.js patterns
        spa_patterns = ['react', 'next', '_next', 'jsx', 'tsx']
        found_spa = [pattern for pattern in spa_patterns if pattern in content]
        
        if found_spa:
            print(f"⚛️ SPA framework indicators: {found_spa}")

if __name__ == "__main__":
    # Run the test
    success = test_flash_app_login()
    
    # Analyze results
    analyze_flash_app()
    
    print(f"\n🎯 FINAL RESULT: {'SUCCESS' if success else 'NEEDS MORE WORK'}")
    
    if success:
        print("✅ Ready to extract Flash Research data!")
    else:
        print("📝 Next steps:")
        print("• Analyze screenshots and HTML source")
        print("• Identify correct login selectors")
        print("• Handle any CAPTCHA or 2FA")
        print("• Test different authentication approaches")