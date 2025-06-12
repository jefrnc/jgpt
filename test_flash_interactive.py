#!/usr/bin/env python3
"""
Test interactivo para explorar Flash Research manualmente
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def explore_flash_research():
    """Explorar Flash Research de forma interactiva"""
    print("🔍 EXPLORACIÓN INTERACTIVA DE FLASH RESEARCH")
    print("=" * 60)
    
    # Setup driver sin headless para ver la pantalla
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Login
        print("🔐 Haciendo login en Flash Research...")
        driver.get("https://app.flash-research.com/login")
        time.sleep(3)
        
        # Fill login form
        email_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "password")
        
        email_field.send_keys("jsfrnc@gmail.com")
        password_field.send_keys("ge1hwZxFeN")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[class*='bg-custom-sixth']")
        submit_button.click()
        
        print("⏳ Esperando que cargue la aplicación...")
        time.sleep(8)
        
        print(f"📍 URL actual: {driver.current_url}")
        
        # Buscar todos los elementos clickeables
        print("\n🔍 EXPLORANDO ELEMENTOS CLICKEABLES...")
        
        # Buscar enlaces
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"\n📎 Enlaces encontrados ({len(links)}):")
        for i, link in enumerate(links[:15]):  # Solo primeros 15
            href = link.get_attribute("href") or "sin-href"
            text = link.text.strip()
            if text and len(text) < 50:
                print(f"   {i+1}. '{text}' -> {href}")
        
        # Buscar botones
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\n🔘 Botones encontrados ({len(buttons)}):")
        for i, button in enumerate(buttons[:15]):  # Solo primeros 15
            text = button.text.strip()
            classes = button.get_attribute("class") or ""
            if text and len(text) < 50 and "cky-" not in classes:  # Skip cookie buttons
                print(f"   {i+1}. '{text}' -> {classes[:50]}...")
        
        # Buscar elementos de navegación específicos
        print("\n🧭 BUSCANDO NAVEGACIÓN ESPECÍFICA...")
        
        nav_keywords = ["ticket", "analysis", "scanner", "research", "gap", "tool"]
        found_nav = []
        
        for keyword in nav_keywords:
            try:
                # Buscar por texto que contenga la palabra clave
                xpath = f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]"
                elements = driver.find_elements(By.XPATH, xpath)
                
                for elem in elements:
                    text = elem.text.strip()
                    tag = elem.tag_name
                    if text and len(text) < 100:
                        found_nav.append(f"{keyword}: {tag} -> '{text}'")
                        
            except Exception as e:
                continue
        
        if found_nav:
            print("✅ Elementos de navegación encontrados:")
            for nav in found_nav[:10]:  # Solo primeros 10
                print(f"   • {nav}")
        else:
            print("❌ No se encontraron elementos de navegación específicos")
        
        # Buscar formularios de búsqueda
        print("\n🔍 BUSCANDO CAMPOS DE BÚSQUEDA...")
        
        search_inputs = []
        inputs = driver.find_elements(By.TAG_NAME, "input")
        
        for inp in inputs:
            placeholder = inp.get_attribute("placeholder") or ""
            name = inp.get_attribute("name") or ""
            input_type = inp.get_attribute("type") or ""
            
            if any(word in placeholder.lower() for word in ["search", "symbol", "ticker", "stock"]):
                search_inputs.append(f"placeholder: '{placeholder}', name: '{name}', type: '{input_type}'")
            elif any(word in name.lower() for word in ["search", "symbol", "ticker"]):
                search_inputs.append(f"placeholder: '{placeholder}', name: '{name}', type: '{input_type}'")
        
        if search_inputs:
            print("✅ Campos de búsqueda encontrados:")
            for search in search_inputs:
                print(f"   • {search}")
        else:
            print("❌ No se encontraron campos de búsqueda")
        
        # Pausa interactiva para explorar manualmente
        print("\n" + "=" * 60)
        print("🖱️ EXPLORACIÓN MANUAL")
        print("=" * 60)
        print("El navegador está abierto. Puedes:")
        print("1. Navegar manualmente por Flash Research")
        print("2. Buscar 'Ticket Analysis' o herramientas similares")
        print("3. Probar búsquedas de símbolos")
        print("4. Inspeccionar elementos con F12")
        print("\nObserva dónde están ubicadas las opciones de análisis...")
        
        # Mantener el navegador abierto para exploración manual
        input("\n⏸️ Presiona Enter cuando hayas terminado de explorar...")
        
        # Tomar screenshot final
        driver.save_screenshot("/tmp/flash_exploration_final.png")
        print("\n🖼️ Screenshot final guardado: /tmp/flash_exploration_final.png")
        
        # Obtener HTML actual para análisis
        with open("/tmp/flash_exploration_html.html", "w") as f:
            f.write(driver.page_source)
        print("📝 HTML guardado: /tmp/flash_exploration_html.html")
        
    except Exception as e:
        print(f"❌ Error durante exploración: {e}")
    
    finally:
        print("\n🔒 Cerrando navegador...")
        driver.quit()

if __name__ == "__main__":
    explore_flash_research()