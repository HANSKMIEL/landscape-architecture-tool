#!/usr/bin/env python3
"""
UI Navigation Investigation for Plants Component.

This script investigates UI navigation issues preventing access to the
Add Plant button and other UI elements, and provides solutions for
complete testing.
"""

import json
import time
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def setup_driver():
    """Setup Chrome driver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--headless")  # Run in headless mode for CI
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)
    return driver

def investigate_ui_navigation():
    """Investigate UI navigation issues and document findings"""
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "investigation_type": "UI Navigation Analysis",
        "url_tested": "http://localhost:5174",
        "findings": {},
        "navigation_issues": [],
        "solutions": [],
        "test_results": {}
    }
    
    driver = None
    
    try:
        driver = setup_driver()
        wait = WebDriverWait(driver, 10)
        
        print("🔍 Starting UI Navigation Investigation...")
        
        # Step 1: Load the application
        print("📱 Loading application...")
        driver.get("http://localhost:5174")
        time.sleep(3)
        
        # Step 2: Check login page structure
        print("🔐 Analyzing login page...")
        try:
            # Check for login form presence
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
            results["findings"]["login_page"] = "Found login form"
            
            # Look for demo credentials or login button
            login_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign In') or contains(text(), 'Inloggen')]")
            if login_buttons:
                results["findings"]["login_button"] = f"Found {len(login_buttons)} login button(s)"
            
            # Check for demo credentials display
            demo_text = driver.find_elements(By.XPATH, "//*[contains(text(), 'admin') or contains(text(), 'Demo') or contains(text(), 'Test')]")
            if demo_text:
                results["findings"]["demo_credentials"] = f"Found {len(demo_text)} demo credential element(s)"
                
        except TimeoutException:
            results["navigation_issues"].append("Login page not loading properly")
        
        # Step 3: Attempt login with admin credentials
        print("🔑 Attempting login...")
        try:
            # Try to find username/email field
            username_selectors = [
                "//input[@name='username']",
                "//input[@name='email']", 
                "//input[@type='email']",
                "//input[@placeholder*='username']",
                "//input[@placeholder*='email']"
            ]
            
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = driver.find_element(By.XPATH, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if username_field:
                username_field.clear()
                username_field.send_keys("admin")
                results["findings"]["username_field"] = "Successfully entered admin username"
            else:
                results["navigation_issues"].append("Could not locate username/email field")
            
            # Try to find password field
            password_field = driver.find_element(By.XPATH, "//input[@type='password']")
            password_field.clear()
            # Test credentials (not production password)
            password_field.send_keys("admin123")
            results["findings"]["password_field"] = "Successfully entered password"
            
            # Find and click login button
            login_button = driver.find_element(By.XPATH, "//button[@type='submit' or contains(text(), 'Login') or contains(text(), 'Sign In')]")
            login_button.click()
            
            # Wait for navigation
            time.sleep(3)
            results["findings"]["login_attempt"] = "Login attempt completed"
            
        except NoSuchElementException as e:
            results["navigation_issues"].append(
                f"Login form elements not found: {e!s}"
            )
        
        # Step 4: Check if we're on the dashboard
        print("📊 Checking dashboard access...")
        try:
            # Look for dashboard indicators
            dashboard_indicators = [
                "//h1[contains(text(), 'Dashboard')]",
                "//div[contains(@class, 'dashboard')]",
                "//*[contains(text(), 'Welcome')]",
                "//nav",
                "//aside"  # Sidebar
            ]
            
            dashboard_found = False
            for indicator in dashboard_indicators:
                try:
                    driver.find_element(By.XPATH, indicator)
                    dashboard_found = True
                    results["findings"]["dashboard_access"] = f"Dashboard detected via: {indicator}"
                    break
                except NoSuchElementException:
                    continue
            
            if not dashboard_found:
                results["navigation_issues"].append("Dashboard not accessible after login")
                
        except Exception as e:
            results["navigation_issues"].append(
                f"Dashboard check failed: {e!s}"
            )
        
        # Step 5: Investigate navigation to Plants page
        print("🌱 Investigating Plants page navigation...")
        try:
            # Look for navigation links
            nav_selectors = [
                "//a[contains(text(), 'Plants') or contains(text(), 'Planten')]",
                "//button[contains(text(), 'Plants') or contains(text(), 'Planten')]",
                "//li[contains(text(), 'Plants') or contains(text(), 'Planten')]",
                "//*[@href='/plants' or @href='#/plants']"
            ]
            
            plants_nav = None
            for selector in nav_selectors:
                try:
                    plants_nav = driver.find_element(By.XPATH, selector)
                    results["findings"]["plants_navigation"] = f"Found Plants navigation: {selector}"
                    break
                except NoSuchElementException:
                    continue
            
            if plants_nav:
                # Try to click the Plants navigation
                driver.execute_script("arguments[0].scrollIntoView(true);", plants_nav)
                time.sleep(1)
                plants_nav.click()
                time.sleep(3)
                
                results["findings"]["plants_navigation_click"] = "Successfully clicked Plants navigation"
                
                # Check if we're on the Plants page
                plants_page_indicators = [
                    "//h1[contains(text(), 'Plants') or contains(text(), 'Planten')]",
                    "//*[contains(text(), 'Add Plant') or contains(text(), 'Plant Toevoegen')]",
                    "//button[contains(text(), 'Add Plant')]"
                ]
                
                for indicator in plants_page_indicators:
                    try:
                        driver.find_element(By.XPATH, indicator)
                        results["findings"]["plants_page_access"] = (
                            f"Plants page confirmed: {indicator}"
                        )
                        break
                    except NoSuchElementException:
                        continue
                        
            else:
                results["navigation_issues"].append("Plants navigation link not found")
                
        except Exception as e:
            results["navigation_issues"].append(
                f"Plants navigation failed: {e!s}"
            )
        
        # Step 6: Look for Add Plant button
        print("➕ Searching for Add Plant button...")
        try:
            add_plant_selectors = [
                "//button[contains(text(), 'Add Plant')]",
                "//button[contains(text(), 'Plant Toevoegen')]", 
                "//button[contains(text(), 'Toevoegen')]",
                "//*[contains(@class, 'add') and contains(text(), 'Plant')]",
                "//button[.//*[contains(@class, 'plus')]]",  # Button with plus icon
                "//button[contains(@aria-label, 'Add')]"
            ]
            
            add_button_found = False
            for selector in add_plant_selectors:
                try:
                    add_button = driver.find_element(By.XPATH, selector)
                    add_button_found = True
                    results["findings"]["add_plant_button"] = f"Add Plant button found: {selector}"
                    
                    # Try to click it
                    driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
                    time.sleep(1)
                    add_button.click()
                    time.sleep(2)
                    
                    # Check if modal opened
                    modal_selectors = [
                        "//div[contains(@class, 'modal')]",
                        "//div[contains(@class, 'fixed')]",  # Common modal class
                        "//form[contains(@class, 'space-y')]",
                        "//*[contains(text(), 'Scientific Name')]"
                    ]
                    
                    modal_found = False
                    for modal_selector in modal_selectors:
                        try:
                            driver.find_element(By.XPATH, modal_selector)
                            modal_found = True
                            results["findings"]["add_plant_modal"] = f"Add Plant modal opened: {modal_selector}"
                            break
                        except NoSuchElementException:
                            continue
                    
                    if not modal_found:
                        results["navigation_issues"].append("Add Plant button clicked but modal did not open")
                    
                    break
                    
                except NoSuchElementException:
                    continue
            
            if not add_button_found:
                results["navigation_issues"].append("Add Plant button not found with any selector")
                
        except Exception as e:
            results["navigation_issues"].append(
                f"Add Plant button search failed: {e!s}"
            )
        
        # Step 7: Test input field if modal is open
        print("📝 Testing input field behavior...")
        try:
            # Look for the scientific name input field
            name_input_selectors = [
                "//input[@name='name']",
                "//input[@placeholder*='Scientific']",
                "//input[@placeholder*='Acer']"
            ]
            
            name_input = None
            for selector in name_input_selectors:
                try:
                    name_input = driver.find_element(By.XPATH, selector)
                    results["findings"]["name_input_field"] = f"Scientific name input found: {selector}"
                    break
                except NoSuchElementException:
                    continue
            
            if name_input:
                # Test character-by-character input
                test_text = "Acer platanoides"
                results["test_results"]["input_field_test"] = {
                    "test_text": test_text,
                    "characters_typed": [],
                    "focus_events": []
                }
                
                # Clear the field
                name_input.clear()
                
                # Type character by character and check focus
                for i, char in enumerate(test_text):
                    try:
                        # Check if field still has focus
                        current_focus = driver.switch_to.active_element
                        has_focus = current_focus == name_input
                        
                        results["test_results"]["input_field_test"]["focus_events"].append({
                            "character_index": i,
                            "character": char,
                            "has_focus": has_focus,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        if not has_focus:
                            results["navigation_issues"].append(f"Input field lost focus at character {i}: '{char}'")
                            # Try to refocus
                            name_input.click()
                        
                        # Type the character
                        name_input.send_keys(char)
                        results["test_results"]["input_field_test"]["characters_typed"].append(char)
                        
                        # Small delay to simulate human typing
                        time.sleep(0.1)
                        
                    except Exception as e:
                        results["navigation_issues"].append(
                            f"Input field test failed at character {i}: {e!s}"
                        )
                        break
                
                # Check final value
                final_value = name_input.get_attribute("value")
                results["test_results"]["input_field_test"]["final_value"] = final_value
                results["test_results"]["input_field_test"]["expected_value"] = test_text
                results["test_results"]["input_field_test"]["test_passed"] = final_value == test_text
                
            else:
                results["navigation_issues"].append("Scientific name input field not found for testing")
                
        except Exception as e:
            results["navigation_issues"].append(
                f"Input field testing failed: {e!s}"
            )
        
        # Step 8: Document page structure
        print("🏗️ Documenting page structure...")
        try:
            # Extract key structural elements
            structural_elements = {
                "forms": len(driver.find_elements(By.TAG_NAME, "form")),
                "buttons": len(driver.find_elements(By.TAG_NAME, "button")),
                "inputs": len(driver.find_elements(By.TAG_NAME, "input")),
                "navigation_links": len(driver.find_elements(By.TAG_NAME, "a")),
                "modals": len(driver.find_elements(By.XPATH, "//div[contains(@class, 'modal') or contains(@class, 'fixed')]"))
            }
            
            results["findings"]["page_structure"] = structural_elements
            
        except Exception as e:
            results["navigation_issues"].append(
                f"Page structure analysis failed: {e!s}"
            )
        
        # Step 9: Generate solutions
        print("💡 Generating solutions...")
        results["solutions"] = [
            "Implement keyboard navigation shortcuts for accessibility",
            "Add data-testid attributes for reliable element selection",
            "Ensure modal focus management follows ARIA guidelines",
            "Add loading states during navigation transitions",
            "Implement proper focus trap for modal dialogs",
            "Add visual indicators for interactive elements",
            "Use semantic HTML elements for better navigation",
            "Implement proper error boundaries for failed navigation",
            "Add retry mechanisms for failed UI interactions",
            "Create fallback navigation methods"
        ]
        
        print("✅ UI Navigation Investigation Complete!")
        
    except Exception as e:
        results["navigation_issues"].append(f"Critical investigation error: {e!s}")
        print(f"❌ Investigation failed: {e!s}")
        
    finally:
        if driver:
            driver.quit()
    
    return results

if __name__ == "__main__":
    print("🚀 Starting UI Navigation Investigation...")
    
    # Run the investigation
    investigation_results = investigate_ui_navigation()
    
    # Save results
    with open("ui_navigation_investigation.json", "w") as f:
        json.dump(investigation_results, f, indent=2)
    
    print("\n📊 Investigation Results:")
    print(f"- Findings: {len(investigation_results['findings'])} items documented")
    print(f"- Navigation Issues: {len(investigation_results['navigation_issues'])} issues found")
    print(f"- Solutions: {len(investigation_results['solutions'])} recommendations provided")
    
    if investigation_results["test_results"].get("input_field_test"):
        test_results = investigation_results["test_results"]["input_field_test"]
        print("\n📝 Input Field Test Results:")
        print(f"- Characters typed: {len(test_results.get('characters_typed', []))}")
        print(f"- Focus events tracked: {len(test_results.get('focus_events', []))}")
        print(f"- Test passed: {test_results.get('test_passed', False)}")
    
    print("\n🔍 Key Findings:")
    for key, value in investigation_results["findings"].items():
        print(f"  - {key}: {value}")
    
    print("\n⚠️ Navigation Issues:")
    for issue in investigation_results["navigation_issues"]:
        print(f"  - {issue}")
    
    print("\n📋 Full results saved to: ui_navigation_investigation.json")