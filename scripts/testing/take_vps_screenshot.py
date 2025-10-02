#!/usr/bin/env python3
"""
Take screenshot of VPS current state to understand UI structure
"""

import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def take_vps_screenshot():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("📸 Taking VPS screenshot...")
        driver.get("http://72.60.176.200:8080")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Try to login if needed
        try:
            username_field = driver.find_element(By.XPATH, "//input[@type='text' or @type='email' or @name='username']")
            password_field = driver.find_element(By.XPATH, "//input[@type='password' or @name='password']")
            
            username_field.clear()
            username_field.send_keys("admin")
            password_field.clear()
            password_field.send_keys("admin123")
            
            login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Log') or contains(text(), 'Inlog') or @type='submit']")
            login_button.click()
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Dashboard') or contains(text(), 'Landschap')]"))
            )
            print("✅ Logged in successfully")
        except:
            print("ℹ️ Already logged in or login not needed")
        
        # Take screenshot
        driver.save_screenshot("vps_current_state.png")
        print("✅ Screenshot saved as vps_current_state.png")
        
        # Get page structure info
        print("\n🔍 Current Page Structure:")
        try:
            # Find navigation elements
            nav_elements = driver.find_elements(By.XPATH, "//nav//a | //aside//a | //div[contains(@class, 'nav')]//a")
            print(f"   Navigation links found: {len(nav_elements)}")
            for i, elem in enumerate(nav_elements[:10]):  # First 10
                try:
                    print(f"   {i+1}. {elem.text.strip()} -> {elem.get_attribute('href')}")
                except:
                    print(f"   {i+1}. [Unable to get text/href]")
                    
            # Check for language selector
            lang_selectors = driver.find_elements(By.XPATH, "//select[option[contains(text(), 'English') or contains(text(), 'Nederlands')]]")
            print(f"   Language selectors found: {len(lang_selectors)}")
            
            # Get page title and main content
            title = driver.title
            main_heading = driver.find_element(By.XPATH, "//h1").text if driver.find_elements(By.XPATH, "//h1") else "No h1 found"
            print(f"   Page title: {title}")
            print(f"   Main heading: {main_heading}")
            
        except Exception as e:
            print(f"   Error getting page structure: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    take_vps_screenshot()