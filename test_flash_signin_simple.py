#!/usr/bin/env python3
"""
Test simple de Flash Research signin page
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

def test_flash_signin():
    """Test simple de la página de signin"""
    print("🔐 SIMPLE FLASH RESEARCH SIGNIN TEST")
    print("=" * 50)
    
    # Setup driver
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")  # Comentar para ver
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to signin
        signin_url = "https://flash-research.com/signin"
        print(f"🌐 Loading: {signin_url}")
        
        driver.get(signin_url)
        time.sleep(8)  # More time for SPA to load
        
        print(f"📍 Final URL: {driver.current_url}")
        print(f"📄 Title: {driver.title}")
        
        # Save screenshot
        driver.save_screenshot("/tmp/flash_signin_page.png")
        print("🖼️ Screenshot saved: /tmp/flash_signin_page.png")
        
        # Save page source
        with open("/tmp/flash_signin_source.html", "w") as f:
            f.write(driver.page_source)
        print("📝 HTML saved: /tmp/flash_signin_source.html")
        
        # Get all input elements
        print("\n🔍 Analyzing input elements...")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Found {len(inputs)} input elements:")
        
        for i, inp in enumerate(inputs):
            input_type = inp.get_attribute("type") or "text"
            name = inp.get_attribute("name") or "no-name"
            placeholder = inp.get_attribute("placeholder") or "no-placeholder"
            id_attr = inp.get_attribute("id") or "no-id"
            classes = inp.get_attribute("class") or "no-class"
            
            print(f"   {i+1}. Type: {input_type}, Name: {name}, ID: {id_attr}")
            print(f"      Placeholder: {placeholder}")
            print(f"      Classes: {classes[:50]}...")
            print()
        
        # Get all buttons
        print("🔍 Analyzing button elements...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} button elements:")
        
        for i, btn in enumerate(buttons):
            text = btn.text.strip()
            btn_type = btn.get_attribute("type") or "button"
            classes = btn.get_attribute("class") or "no-class"
            
            if text and "cky-" not in classes:  # Skip cookie buttons
                print(f"   {i+1}. Text: '{text}', Type: {btn_type}")
                print(f"      Classes: {classes[:50]}...")
                print()
        
        # Look for forms
        print("🔍 Analyzing form elements...")
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"Found {len(forms)} form elements")
        
        # Try to identify login fields by common patterns
        print("\n🎯 Identifying potential login fields...")
        
        email_candidates = []
        password_candidates = []
        
        for inp in inputs:
            input_type = inp.get_attribute("type") or ""
            name = inp.get_attribute("name") or ""
            placeholder = inp.get_attribute("placeholder") or ""
            id_attr = inp.get_attribute("id") or ""
            
            # Check for email field
            if (input_type == "email" or 
                "email" in name.lower() or 
                "email" in placeholder.lower() or
                "email" in id_attr.lower()):
                email_candidates.append(inp)
                print(f"📧 Email candidate: type={input_type}, name={name}, placeholder={placeholder}")
            
            # Check for password field
            if (input_type == "password" or
                "password" in name.lower() or
                "password" in placeholder.lower() or
                "password" in id_attr.lower()):
                password_candidates.append(inp)
                print(f"🔒 Password candidate: type={input_type}, name={name}, placeholder={placeholder}")
        
        # Try to login if we found candidates
        if email_candidates and password_candidates:
            print(f"\n🚀 Attempting login with {len(email_candidates)} email and {len(password_candidates)} password fields...")
            
            email_field = email_candidates[0]
            password_field = password_candidates[0]
            
            # Credentials
            email = "jsfrnc@gmail.com"
            password = "ge1hwZxFeN"
            
            # Fill fields
            email_field.clear()
            email_field.send_keys(email)
            print("📧 Email entered")
            
            password_field.clear()
            password_field.send_keys(password)
            print("🔒 Password entered")
            
            # Look for submit button
            submit_candidates = []
            for btn in buttons:
                text = btn.text.strip().lower()
                btn_type = btn.get_attribute("type") or ""
                
                if (btn_type == "submit" or
                    "sign in" in text or
                    "login" in text or
                    "log in" in text or
                    text == "continue"):
                    submit_candidates.append(btn)
            
            if submit_candidates:
                print(f"🎯 Found {len(submit_candidates)} submit button candidates")
                submit_button = submit_candidates[0]
                submit_button.click()
                print("🚀 Submit button clicked")
            else:
                # Try Enter key
                password_field.send_keys(Keys.RETURN)
                print("⌨️ Enter key pressed")
            
            # Wait for response
            time.sleep(5)
            
            # Check result
            final_url = driver.current_url
            final_title = driver.title
            
            print(f"\n📍 After login URL: {final_url}")
            print(f"📄 After login title: {final_title}")
            
            # Save after-login state
            driver.save_screenshot("/tmp/flash_after_login.png")
            with open("/tmp/flash_after_login_source.html", "w") as f:
                f.write(driver.page_source)
            
            print("🖼️ After-login screenshot: /tmp/flash_after_login.png")
            print("📝 After-login HTML: /tmp/flash_after_login_source.html")
            
            # Check for success
            page_text = driver.page_source.lower()
            success_indicators = ["dashboard", "welcome", "logout", "scanner", "research", "gaps"]
            found_indicators = [ind for ind in success_indicators if ind in page_text]
            
            if found_indicators:
                print(f"✅ Login SUCCESS! Found: {found_indicators}")
                
                # Try to find some research data
                print("\n📊 Looking for research data...")
                
                # Check page content
                visible_text = driver.find_element(By.TAG_NAME, "body").text
                research_keywords = ["stock", "ticker", "gap", "volume", "price", "%"]
                found_research = []
                
                for keyword in research_keywords:
                    count = visible_text.lower().count(keyword.lower())
                    if count > 0:
                        found_research.append(f"{keyword}({count})")
                
                if found_research:
                    print(f"📈 Research keywords found: {', '.join(found_research)}")
                
                return True
            else:
                print("❌ Login failed - no success indicators")
                return False
        
        else:
            print("❌ Could not identify login form fields")
            print(f"   Email candidates: {len(email_candidates)}")
            print(f"   Password candidates: {len(password_candidates)}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    finally:
        input("🔍 Press Enter to close browser (check screenshots first)...")
        driver.quit()

if __name__ == "__main__":
    success = test_flash_signin()
    print(f"\n🎯 RESULT: {'SUCCESS' if success else 'FAILED'}")
    
    if success:
        print("✅ Flash Research login working! Ready for data extraction.")
    else:
        print("📝 Check the saved screenshots and HTML files for debugging.")