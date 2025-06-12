import os
import time
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from dotenv import load_dotenv
from src.utils.logger import setup_logger

load_dotenv()


class FlashResearchAdvancedScraper:
    """
    Advanced Flash Research web scraper with detailed page analysis
    """
    
    def __init__(self, headless: bool = True, debug: bool = False):
        self.logger = setup_logger('flash_advanced_scraper')
        self.base_url = "https://flash-research.com"
        self.headless = headless
        self.debug = debug
        
        # Credentials
        self.email = os.getenv('FLASH_RESEARCH_EMAIL', 'jsfrnc@gmail.com')
        self.password = os.getenv('FLASH_RESEARCH_PASSWORD', 'ge1hwZxFeN')
        
        self.driver = None
        self.wait = None
        self.authenticated = False
        
        self.logger.info(f"Advanced Flash Research scraper initialized (headless={headless}, debug={debug})")
    
    def _setup_driver(self):
        """Setup Chrome driver with enhanced options"""
        try:
            chrome_options = Options()
            
            # Basic options
            if self.headless:
                chrome_options.add_argument("--headless=new")  # Use new headless mode
            
            # Anti-detection options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            # Window and user agent
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Performance options
            if not self.debug:
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-plugins")
                prefs = {"profile.managed_default_content_settings.images": 2}
                chrome_options.add_experimental_option("prefs", prefs)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Execute script to hide webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 15)
            
            self.logger.info("✅ Enhanced Chrome driver setup successful")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup Chrome driver: {str(e)}")
            return False
    
    def inspect_homepage(self) -> Dict:
        """Inspect Flash Research homepage to understand structure"""
        try:
            if not self.driver:
                if not self._setup_driver():
                    return {}
            
            self.logger.info("🔍 Inspecting Flash Research homepage...")
            
            # Navigate to homepage
            self.driver.get(self.base_url)
            time.sleep(3)
            
            inspection_data = {
                'url': self.driver.current_url,
                'title': self.driver.title,
                'timestamp': datetime.now().isoformat()
            }
            
            # Check for common elements
            elements_to_check = [
                ('login_button', "//a[contains(text(), 'Login') or contains(text(), 'Sign In') or contains(@href, 'login')]"),
                ('signup_button', "//a[contains(text(), 'Sign Up') or contains(text(), 'Register')]"),
                ('search_box', "//input[@placeholder*='symbol' or @placeholder*='search' or @placeholder*='stock']"),
                ('navigation_menu', "//nav"),
                ('header', "//header"),
                ('footer', "//footer")
            ]
            
            found_elements = {}
            for element_name, xpath in elements_to_check:
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    found_elements[element_name] = {
                        'found': True,
                        'text': element.text[:100] if element.text else '',
                        'tag': element.tag_name,
                        'href': element.get_attribute('href') if element.tag_name == 'a' else None
                    }
                except NoSuchElementException:
                    found_elements[element_name] = {'found': False}
            
            inspection_data['elements'] = found_elements
            
            # Get page source info
            page_source = self.driver.page_source.lower()
            inspection_data['page_analysis'] = {
                'has_login_form': 'login' in page_source and ('email' in page_source or 'username' in page_source),
                'has_search_functionality': 'search' in page_source,
                'has_stock_data': any(term in page_source for term in ['stock', 'ticker', 'symbol', 'gap', 'float']),
                'has_authentication': any(term in page_source for term in ['signin', 'signup', 'login', 'register']),
                'page_length': len(page_source)
            }
            
            # Look for potential login URLs
            login_urls = []
            for link in self.driver.find_elements(By.TAG_NAME, 'a'):
                href = link.get_attribute('href')
                if href and any(term in href.lower() for term in ['login', 'signin', 'auth']):
                    login_urls.append(href)
            
            inspection_data['login_urls'] = list(set(login_urls))
            
            if self.debug:
                # Save screenshot for debugging
                screenshot_path = f"/tmp/flash_research_homepage_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                inspection_data['screenshot'] = screenshot_path
                self.logger.info(f"🖼️ Screenshot saved: {screenshot_path}")
            
            self.logger.info("✅ Homepage inspection completed")
            return inspection_data
            
        except Exception as e:
            self.logger.error(f"❌ Error inspecting homepage: {str(e)}")
            return {}
    
    def find_login_page(self) -> Optional[str]:
        """Find the actual login page URL"""
        try:
            # Common login page patterns
            login_paths = [
                '/login',
                '/signin',
                '/auth/login',
                '/user/login',
                '/account/login',
                '/members/login'
            ]
            
            for path in login_paths:
                test_url = f"{self.base_url}{path}"
                self.logger.info(f"🔍 Testing login URL: {test_url}")
                
                try:
                    self.driver.get(test_url)
                    time.sleep(2)
                    
                    # Check if this looks like a login page
                    page_source = self.driver.page_source.lower()
                    
                    login_indicators = [
                        'email' in page_source and 'password' in page_source,
                        'username' in page_source and 'password' in page_source,
                        'sign in' in page_source,
                        'login' in page_source and 'form' in page_source
                    ]
                    
                    if any(login_indicators):
                        self.logger.info(f"✅ Found potential login page: {test_url}")
                        return test_url
                        
                except Exception as e:
                    self.logger.debug(f"Login URL {test_url} failed: {str(e)}")
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error finding login page: {str(e)}")
            return None
    
    def analyze_login_form(self, login_url: str) -> Dict:
        """Analyze the login form structure"""
        try:
            self.logger.info(f"🔍 Analyzing login form at: {login_url}")
            
            self.driver.get(login_url)
            time.sleep(3)
            
            form_analysis = {
                'url': login_url,
                'title': self.driver.title,
                'forms_found': []
            }
            
            # Find all forms
            forms = self.driver.find_elements(By.TAG_NAME, 'form')
            
            for i, form in enumerate(forms):
                form_data = {
                    'form_index': i,
                    'action': form.get_attribute('action'),
                    'method': form.get_attribute('method') or 'GET',
                    'inputs': []
                }
                
                # Analyze form inputs
                inputs = form.find_elements(By.TAG_NAME, 'input')
                for input_elem in inputs:
                    input_data = {
                        'type': input_elem.get_attribute('type'),
                        'name': input_elem.get_attribute('name'),
                        'id': input_elem.get_attribute('id'),
                        'placeholder': input_elem.get_attribute('placeholder'),
                        'required': input_elem.get_attribute('required') is not None,
                        'xpath': self._get_element_xpath(input_elem)
                    }
                    form_data['inputs'].append(input_data)
                
                # Look for submit button
                submit_buttons = form.find_elements(By.XPATH, ".//button[@type='submit'] | .//input[@type='submit']")
                form_data['submit_buttons'] = []
                
                for button in submit_buttons:
                    button_data = {
                        'tag': button.tag_name,
                        'type': button.get_attribute('type'),
                        'text': button.text or button.get_attribute('value'),
                        'xpath': self._get_element_xpath(button)
                    }
                    form_data['submit_buttons'].append(button_data)
                
                form_analysis['forms_found'].append(form_data)
            
            # Look for email/username and password fields specifically
            email_selectors = [
                "//input[@type='email']",
                "//input[@name='email']",
                "//input[@id='email']",
                "//input[@name='username']",
                "//input[@id='username']",
                "//input[contains(@placeholder, 'email')]",
                "//input[contains(@placeholder, 'Email')]"
            ]
            
            password_selectors = [
                "//input[@type='password']",
                "//input[@name='password']",
                "//input[@id='password']",
                "//input[contains(@placeholder, 'password')]",
                "//input[contains(@placeholder, 'Password')]"
            ]
            
            form_analysis['email_field'] = self._find_best_selector(email_selectors)
            form_analysis['password_field'] = self._find_best_selector(password_selectors)
            
            if self.debug:
                # Save screenshot of login page
                screenshot_path = f"/tmp/flash_research_login_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                form_analysis['screenshot'] = screenshot_path
                self.logger.info(f"🖼️ Login page screenshot saved: {screenshot_path}")
            
            self.logger.info("✅ Login form analysis completed")
            return form_analysis
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing login form: {str(e)}")
            return {}
    
    def attempt_login_with_analysis(self, form_analysis: Dict) -> bool:
        """Attempt login using the analyzed form data"""
        try:
            if not form_analysis.get('email_field') or not form_analysis.get('password_field'):
                self.logger.error("❌ Email or password field not found in analysis")
                return False
            
            self.logger.info("🔐 Attempting login with analyzed form data...")
            
            # Fill email field
            email_xpath = form_analysis['email_field']['xpath']
            email_element = self.wait.until(EC.presence_of_element_located((By.XPATH, email_xpath)))
            email_element.clear()
            email_element.send_keys(self.email)
            
            # Fill password field  
            password_xpath = form_analysis['password_field']['xpath']
            password_element = self.driver.find_element(By.XPATH, password_xpath)
            password_element.clear()
            password_element.send_keys(self.password)
            
            # Submit form
            submit_selectors = [
                "//button[@type='submit']",
                "//input[@type='submit']",
                "//button[contains(text(), 'Sign In')]",
                "//button[contains(text(), 'Login')]",
                "//button[contains(text(), 'Log In')]"
            ]
            
            submit_element = None
            for selector in submit_selectors:
                try:
                    submit_element = self.driver.find_element(By.XPATH, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if submit_element:
                # Try clicking the submit button
                try:
                    submit_element.click()
                except ElementNotInteractableException:
                    # If click fails, try submitting the form directly
                    password_element.send_keys(Keys.RETURN)
            else:
                # If no submit button found, try pressing Enter
                password_element.send_keys(Keys.RETURN)
            
            # Wait for redirect or login success
            time.sleep(5)
            
            # Check if login was successful
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            success_indicators = [
                'dashboard' in current_url.lower(),
                'profile' in current_url.lower(),
                'welcome' in page_source,
                'logout' in page_source,
                'dashboard' in page_source
            ]
            
            failure_indicators = [
                'error' in page_source,
                'invalid' in page_source,
                'incorrect' in page_source,
                'failed' in page_source,
                'login' in current_url.lower()  # Still on login page
            ]
            
            if any(success_indicators) and not any(failure_indicators):
                self.authenticated = True
                self.logger.info("✅ Login successful!")
                return True
            else:
                self.logger.error("❌ Login failed - checking for error messages")
                
                # Look for error messages
                error_selectors = [
                    "//div[contains(@class, 'error')]",
                    "//div[contains(@class, 'alert')]",
                    "//span[contains(@class, 'error')]",
                    "//p[contains(text(), 'error')]"
                ]
                
                for selector in error_selectors:
                    try:
                        error_element = self.driver.find_element(By.XPATH, selector)
                        if error_element.text:
                            self.logger.error(f"Login error: {error_element.text}")
                    except NoSuchElementException:
                        continue
                
                return False
                
        except TimeoutException:
            self.logger.error("❌ Login timeout - elements not found")
            return False
        except Exception as e:
            self.logger.error(f"❌ Login attempt failed: {str(e)}")
            return False
    
    def _find_best_selector(self, selectors: List[str]) -> Optional[Dict]:
        """Find the best working selector from a list"""
        for selector in selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                return {
                    'xpath': selector,
                    'found': True,
                    'tag': element.tag_name,
                    'type': element.get_attribute('type'),
                    'name': element.get_attribute('name'),
                    'id': element.get_attribute('id')
                }
            except NoSuchElementException:
                continue
        return None
    
    def _get_element_xpath(self, element) -> str:
        """Get XPath for an element"""
        try:
            return self.driver.execute_script("""
                function getElementXPath(element) {
                    if (element.id !== '') {
                        return "//*[@id='" + element.id + "']";
                    }
                    if (element === document.body) {
                        return '/html/body';
                    }
                    var ix = 0;
                    var siblings = element.parentNode.childNodes;
                    for (var i = 0; i < siblings.length; i++) {
                        var sibling = siblings[i];
                        if (sibling === element) {
                            return getElementXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                        }
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                            ix++;
                        }
                    }
                }
                return getElementXPath(arguments[0]);
            """, element)
        except:
            return "//unknown"
    
    def full_site_analysis(self) -> Dict:
        """Perform complete site analysis"""
        try:
            self.logger.info("🔍 Starting full Flash Research site analysis...")
            
            analysis_results = {
                'timestamp': datetime.now().isoformat(),
                'homepage_inspection': {},
                'login_analysis': {},
                'authentication_attempt': False
            }
            
            # Step 1: Inspect homepage
            homepage_data = self.inspect_homepage()
            analysis_results['homepage_inspection'] = homepage_data
            
            # Step 2: Find login page
            login_url = self.find_login_page()
            
            if login_url:
                # Step 3: Analyze login form
                login_analysis = self.analyze_login_form(login_url)
                analysis_results['login_analysis'] = login_analysis
                
                # Step 4: Attempt login
                if login_analysis.get('email_field') and login_analysis.get('password_field'):
                    login_success = self.attempt_login_with_analysis(login_analysis)
                    analysis_results['authentication_attempt'] = login_success
                    
                    if login_success:
                        self.logger.info("🎉 Full authentication successful!")
                    else:
                        self.logger.warning("⚠️ Authentication failed, but analysis data collected")
                else:
                    self.logger.warning("⚠️ Could not identify login form fields")
            else:
                self.logger.warning("⚠️ No login page found")
            
            # Save analysis results
            if self.debug:
                analysis_file = f"/tmp/flash_research_analysis_{int(time.time())}.json"
                with open(analysis_file, 'w') as f:
                    json.dump(analysis_results, f, indent=2, default=str)
                self.logger.info(f"📊 Analysis results saved: {analysis_file}")
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"❌ Error in full site analysis: {str(e)}")
            return {}
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.logger.info("🔒 Browser closed")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close()


def test_advanced_scraper():
    """Test the advanced scraper"""
    print("🚀 TESTING ADVANCED FLASH RESEARCH SCRAPER")
    print("=" * 60)
    
    # Initialize with debug mode
    scraper = FlashResearchAdvancedScraper(headless=False, debug=True)
    
    try:
        # Perform full site analysis
        print("🔍 Starting comprehensive site analysis...")
        results = scraper.full_site_analysis()
        
        # Print results summary
        print("\n📊 ANALYSIS RESULTS SUMMARY:")
        print("=" * 40)
        
        homepage = results.get('homepage_inspection', {})
        if homepage:
            print(f"✅ Homepage analyzed: {homepage.get('title', 'Unknown')}")
            print(f"   URL: {homepage.get('url', 'Unknown')}")
            
            page_analysis = homepage.get('page_analysis', {})
            print(f"   Has login form: {page_analysis.get('has_login_form', False)}")
            print(f"   Has search: {page_analysis.get('has_search_functionality', False)}")
            print(f"   Has stock data: {page_analysis.get('has_stock_data', False)}")
            
            login_urls = homepage.get('login_urls', [])
            if login_urls:
                print(f"   Login URLs found: {len(login_urls)}")
                for url in login_urls:
                    print(f"     - {url}")
        
        login_analysis = results.get('login_analysis', {})
        if login_analysis:
            print(f"\n✅ Login page analyzed: {login_analysis.get('url', 'Unknown')}")
            forms = login_analysis.get('forms_found', [])
            print(f"   Forms found: {len(forms)}")
            
            email_field = login_analysis.get('email_field')
            password_field = login_analysis.get('password_field')
            print(f"   Email field found: {email_field is not None}")
            print(f"   Password field found: {password_field is not None}")
            
            if email_field:
                print(f"     Email selector: {email_field.get('xpath', 'Unknown')}")
            if password_field:
                print(f"     Password selector: {password_field.get('xpath', 'Unknown')}")
        
        auth_success = results.get('authentication_attempt', False)
        print(f"\n🔐 Authentication attempt: {'✅ SUCCESS' if auth_success else '❌ FAILED'}")
        
        if auth_success:
            print("\n🎉 FLASH RESEARCH SCRAPER READY FOR DATA EXTRACTION!")
        else:
            print("\n📝 NEXT STEPS:")
            print("• Review the analysis results and screenshots")
            print("• Manually inspect Flash Research site structure")
            print("• Adjust selectors based on actual HTML structure")
            print("• Consider handling CAPTCHAs or additional security")
    
    finally:
        scraper.close()


if __name__ == "__main__":
    test_advanced_scraper()