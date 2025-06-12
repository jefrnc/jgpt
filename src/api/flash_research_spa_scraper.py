import os
import time
import json
from typing import Dict, List, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv
from src.utils.logger import setup_logger

load_dotenv()


class FlashResearchSPAScraper:
    """
    Flash Research SPA (Single Page Application) scraper
    Handles Next.js and JavaScript-heavy sites
    """
    
    def __init__(self, headless: bool = True, debug: bool = False):
        self.logger = setup_logger('flash_spa_scraper')
        self.base_url = "https://flash-research.com"
        self.headless = headless
        self.debug = debug
        
        # Credentials
        self.email = os.getenv('FLASH_RESEARCH_EMAIL', 'jsfrnc@gmail.com')
        self.password = os.getenv('FLASH_RESEARCH_PASSWORD', 'ge1hwZxFeN')
        
        self.driver = None
        self.wait = None
        self.authenticated = False
        
        self.logger.info(f"SPA Flash Research scraper initialized (headless={headless})")
    
    def _setup_driver(self):
        """Setup Chrome driver optimized for SPAs"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless=new")
            
            # SPA-optimized options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Enable JavaScript and disable image loading for speed
            if not self.debug:
                prefs = {"profile.managed_default_content_settings.images": 2}
                chrome_options.add_experimental_option("prefs", prefs)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Anti-detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Longer waits for SPA loading
            self.wait = WebDriverWait(self.driver, 20)
            
            self.logger.info("✅ SPA-optimized Chrome driver setup successful")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup Chrome driver: {str(e)}")
            return False
    
    def wait_for_spa_load(self, timeout: int = 15) -> bool:
        """Wait for SPA to fully load"""
        try:
            self.logger.info("⏳ Waiting for SPA to load...")
            
            # Wait for common SPA indicators to load
            spa_loaded_indicators = [
                "document.readyState === 'complete'",
                "window.performance.navigation.type !== undefined",
                "typeof React !== 'undefined' || typeof Vue !== 'undefined' || typeof angular !== 'undefined'"
            ]
            
            # Wait for page to be ready
            for i in range(timeout):
                try:
                    ready_state = self.driver.execute_script("return document.readyState")
                    if ready_state == 'complete':
                        time.sleep(2)  # Extra wait for async content
                        break
                except:
                    pass
                time.sleep(1)
            
            # Look for any content beyond cookies
            content_selectors = [
                "main", "article", "section", ".container", "#root", "#app",
                "[class*='content']", "[class*='main']", "[id*='main']"
            ]
            
            for selector in content_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.text.strip() and len(element.text.strip()) > 50:
                        self.logger.info(f"✅ SPA content loaded (found: {selector})")
                        return True
                except NoSuchElementException:
                    continue
            
            self.logger.warning("⚠️ SPA load uncertain - proceeding anyway")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error waiting for SPA load: {str(e)}")
            return False
    
    def extract_page_content(self) -> Dict:
        """Extract all visible content from the current page"""
        try:
            self.logger.info("📄 Extracting page content...")
            
            content_data = {
                'url': self.driver.current_url,
                'title': self.driver.title,
                'timestamp': datetime.now().isoformat(),
                'content_sections': []
            }
            
            # Get all text content
            body = self.driver.find_element(By.TAG_NAME, 'body')
            visible_text = body.text
            content_data['full_text_length'] = len(visible_text)
            
            # Look for navigation elements
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "nav, .nav, .navigation, .navbar, .menu")
            nav_links = []
            for nav in nav_elements:
                links = nav.find_elements(By.TAG_NAME, 'a')
                for link in links:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    if href and text:
                        nav_links.append({'text': text, 'href': href})
            
            content_data['navigation_links'] = nav_links
            
            # Look for buttons (especially auth-related)
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            button_texts = []
            for button in buttons:
                text = button.text.strip()
                classes = button.get_attribute('class') or ''
                if text and 'cky-' not in classes:  # Exclude cookie consent buttons
                    button_texts.append({
                        'text': text,
                        'classes': classes,
                        'visible': button.is_displayed()
                    })
            
            content_data['buttons'] = button_texts
            
            # Look for headings and main content
            headings = []
            for level in range(1, 7):
                h_elements = self.driver.find_elements(By.TAG_NAME, f'h{level}')
                for h in h_elements:
                    text = h.text.strip()
                    if text:
                        headings.append({'level': level, 'text': text})
            
            content_data['headings'] = headings
            
            # Look for forms
            forms = self.driver.find_elements(By.TAG_NAME, 'form')
            form_data = []
            for form in forms:
                inputs = form.find_elements(By.TAG_NAME, 'input')
                input_types = []
                for inp in inputs:
                    input_type = inp.get_attribute('type')
                    placeholder = inp.get_attribute('placeholder')
                    name = inp.get_attribute('name')
                    if input_type:
                        input_types.append({
                            'type': input_type,
                            'name': name,
                            'placeholder': placeholder
                        })
                
                if input_types:
                    form_data.append({'inputs': input_types})
            
            content_data['forms'] = form_data
            
            # Look for specific research/trading content
            research_keywords = [
                'stock', 'ticker', 'symbol', 'gap', 'float', 'research', 
                'analysis', 'trading', 'market', 'screener', 'data'
            ]
            
            keyword_matches = []
            text_lower = visible_text.lower()
            for keyword in research_keywords:
                if keyword in text_lower:
                    # Count occurrences and get context
                    count = text_lower.count(keyword)
                    keyword_matches.append({'keyword': keyword, 'count': count})
            
            content_data['research_keywords'] = keyword_matches
            
            # Save screenshot if debug
            if self.debug:
                screenshot_path = f"/tmp/flash_research_content_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                content_data['screenshot'] = screenshot_path
                self.logger.info(f"🖼️ Screenshot saved: {screenshot_path}")
            
            self.logger.info(f"✅ Content extracted: {len(visible_text)} chars, {len(nav_links)} nav links, {len(button_texts)} buttons")
            return content_data
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting content: {str(e)}")
            return {}
    
    def look_for_auth_entry_points(self) -> List[Dict]:
        """Look for ways to authenticate (login buttons, forms, etc.)"""
        try:
            self.logger.info("🔍 Looking for authentication entry points...")
            
            auth_entry_points = []
            
            # Common auth text patterns
            auth_patterns = [
                'sign in', 'login', 'log in', 'sign up', 'register', 
                'create account', 'get started', 'join', 'subscribe'
            ]
            
            # Look for links with auth-related text
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            for link in links:
                text = link.text.strip().lower()
                href = link.get_attribute('href') or ''
                
                for pattern in auth_patterns:
                    if pattern in text or pattern.replace(' ', '') in href.lower():
                        auth_entry_points.append({
                            'type': 'link',
                            'text': link.text.strip(),
                            'href': href,
                            'pattern_matched': pattern,
                            'element_xpath': self._get_element_xpath(link)
                        })
                        break
            
            # Look for buttons with auth-related text
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            for button in buttons:
                text = button.text.strip().lower()
                classes = button.get_attribute('class') or ''
                
                # Skip cookie consent buttons
                if 'cky-' in classes:
                    continue
                
                for pattern in auth_patterns:
                    if pattern in text:
                        auth_entry_points.append({
                            'type': 'button',
                            'text': button.text.strip(),
                            'classes': classes,
                            'pattern_matched': pattern,
                            'element_xpath': self._get_element_xpath(button),
                            'clickable': button.is_enabled()
                        })
                        break
            
            # Look for input fields that might be part of login forms
            inputs = self.driver.find_elements(By.TAG_NAME, 'input')
            potential_auth_forms = []
            
            for inp in inputs:
                input_type = inp.get_attribute('type')
                placeholder = (inp.get_attribute('placeholder') or '').lower()
                name = (inp.get_attribute('name') or '').lower()
                
                # Check if it looks like an auth field
                auth_field_indicators = [
                    'email', 'username', 'password', 'login', 'signin'
                ]
                
                if (input_type in ['email', 'password'] or 
                    any(indicator in placeholder for indicator in auth_field_indicators) or
                    any(indicator in name for indicator in auth_field_indicators)):
                    
                    potential_auth_forms.append({
                        'type': 'input',
                        'input_type': input_type,
                        'name': name,
                        'placeholder': inp.get_attribute('placeholder'),
                        'element_xpath': self._get_element_xpath(inp)
                    })
            
            if potential_auth_forms:
                auth_entry_points.extend(potential_auth_forms)
            
            self.logger.info(f"✅ Found {len(auth_entry_points)} potential auth entry points")
            return auth_entry_points
            
        except Exception as e:
            self.logger.error(f"❌ Error looking for auth entry points: {str(e)}")
            return []
    
    def navigate_and_explore(self, paths: List[str] = None) -> Dict:
        """Navigate to different paths and explore content"""
        if paths is None:
            paths = ['/', '/login', '/signin', '/auth', '/signup', '/register', '/dashboard', '/research']
        
        exploration_results = {}
        
        for path in paths:
            try:
                url = f"{self.base_url}{path}"
                self.logger.info(f"🌐 Exploring: {url}")
                
                self.driver.get(url)
                time.sleep(3)
                
                # Wait for SPA to load
                self.wait_for_spa_load()
                
                # Extract content
                content = self.extract_page_content()
                auth_points = self.look_for_auth_entry_points()
                
                exploration_results[path] = {
                    'final_url': self.driver.current_url,
                    'content': content,
                    'auth_entry_points': auth_points,
                    'exploration_time': datetime.now().isoformat()
                }
                
                # Check if this looks like a different page or redirect
                if self.driver.current_url != url:
                    self.logger.info(f"   Redirected to: {self.driver.current_url}")
                
                time.sleep(2)  # Be respectful
                
            except Exception as e:
                self.logger.error(f"❌ Error exploring {path}: {str(e)}")
                exploration_results[path] = {'error': str(e)}
        
        return exploration_results
    
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
    
    def complete_site_analysis(self) -> Dict:
        """Perform complete Flash Research site analysis"""
        try:
            if not self._setup_driver():
                return {'error': 'Failed to setup driver'}
            
            self.logger.info("🚀 Starting complete Flash Research SPA analysis...")
            
            # Navigate and explore multiple paths
            exploration_results = self.navigate_and_explore()
            
            # Analyze results
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'site_type': 'Next.js SPA',
                'exploration_results': exploration_results,
                'summary': self._analyze_exploration_results(exploration_results)
            }
            
            # Save results if debug
            if self.debug:
                analysis_file = f"/tmp/flash_research_spa_analysis_{int(time.time())}.json"
                with open(analysis_file, 'w') as f:
                    json.dump(analysis, f, indent=2, default=str)
                self.logger.info(f"📊 Analysis saved: {analysis_file}")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"❌ Error in complete analysis: {str(e)}")
            return {'error': str(e)}
        finally:
            self.close()
    
    def _analyze_exploration_results(self, results: Dict) -> Dict:
        """Analyze the exploration results to determine next steps"""
        summary = {
            'total_paths_explored': len(results),
            'successful_explorations': 0,
            'auth_entry_points_found': 0,
            'forms_found': 0,
            'research_content_indicators': 0,
            'recommended_approach': '',
            'next_steps': []
        }
        
        all_auth_points = []
        all_research_keywords = []
        
        for path, data in results.items():
            if 'error' not in data:
                summary['successful_explorations'] += 1
                
                auth_points = data.get('auth_entry_points', [])
                summary['auth_entry_points_found'] += len(auth_points)
                all_auth_points.extend(auth_points)
                
                content = data.get('content', {})
                forms = content.get('forms', [])
                summary['forms_found'] += len(forms)
                
                research_kw = content.get('research_keywords', [])
                if research_kw:
                    summary['research_content_indicators'] += 1
                    all_research_keywords.extend(research_kw)
        
        # Determine recommended approach
        if summary['auth_entry_points_found'] > 0:
            summary['recommended_approach'] = 'Authentication-based scraping'
            summary['next_steps'].append('Try clicking auth entry points and analyze forms')
        elif summary['research_content_indicators'] > 0:
            summary['recommended_approach'] = 'Content extraction without auth'
            summary['next_steps'].append('Extract research data from public pages')
        else:
            summary['recommended_approach'] = 'Alternative data source'
            summary['next_steps'].append('Consider using different APIs or data sources')
        
        if all_research_keywords:
            summary['next_steps'].append('Focus on pages with high research keyword density')
        
        summary['all_auth_entry_points'] = all_auth_points
        summary['unique_research_keywords'] = list(set([kw['keyword'] for kw in all_research_keywords]))
        
        return summary
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.logger.info("🔒 Browser closed")


def test_spa_scraper():
    """Test the SPA scraper"""
    print("🚀 TESTING FLASH RESEARCH SPA SCRAPER")
    print("=" * 60)
    
    # Initialize with debug to see what's happening
    scraper = FlashResearchSPAScraper(headless=False, debug=True)
    
    try:
        # Perform complete analysis
        print("🔍 Starting comprehensive SPA analysis...")
        results = scraper.complete_site_analysis()
        
        # Print results
        print("\n📊 SPA ANALYSIS RESULTS:")
        print("=" * 40)
        
        if 'error' in results:
            print(f"❌ Analysis failed: {results['error']}")
            return
        
        summary = results.get('summary', {})
        print(f"✅ Paths explored: {summary.get('total_paths_explored', 0)}")
        print(f"✅ Successful: {summary.get('successful_explorations', 0)}")
        print(f"✅ Auth entry points: {summary.get('auth_entry_points_found', 0)}")
        print(f"✅ Forms found: {summary.get('forms_found', 0)}")
        print(f"✅ Research indicators: {summary.get('research_content_indicators', 0)}")
        
        print(f"\n🎯 Recommended approach: {summary.get('recommended_approach', 'Unknown')}")
        
        next_steps = summary.get('next_steps', [])
        if next_steps:
            print("\n📝 Next steps:")
            for step in next_steps:
                print(f"   • {step}")
        
        auth_points = summary.get('all_auth_entry_points', [])
        if auth_points:
            print(f"\n🔐 Auth entry points found:")
            for i, point in enumerate(auth_points[:5], 1):  # Show first 5
                print(f"   {i}. {point.get('type', 'unknown')}: {point.get('text', 'no text')}")
        
        research_kw = summary.get('unique_research_keywords', [])
        if research_kw:
            print(f"\n📊 Research keywords found: {', '.join(research_kw[:10])}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


if __name__ == "__main__":
    test_spa_scraper()