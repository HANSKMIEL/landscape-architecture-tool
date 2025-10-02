#!/usr/bin/env python3
"""
Enhanced VPS Testing Script
Addresses specific issues mentioned by @HANSKMIEL:
1. Language switching - only some texts change
2. Other panels (settings, etc.) not tested
3. Missing texts identification
4. Input field reactivation issues
5. Features and functions that still need work
"""

import json
import re
import subprocess
import sys
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class VPSEnhancedTester:
    def __init__(self, base_url="http://72.60.176.200:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.issues_found = []
        self.missing_translations = []
        self.driver = None
        
    def setup_selenium(self):
        """Setup Selenium WebDriver for UI testing"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            self.log_issue("Selenium Setup", f"Failed to setup Selenium: {e}")
            return False
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {details}")
        
    def log_issue(self, category, issue):
        """Log specific issues found"""
        self.issues_found.append({
            "category": category,
            "issue": issue,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        print(f"🔍 ISSUE [{category}]: {issue}")
        
    def test_language_switching_comprehensive(self):
        """Test language switching and identify missing translations"""
        if not self.driver:
            self.log_test("Language Switching Setup", "FAIL", "Selenium not available")
            return False
            
        try:
            print("\n🌍 Testing Language Switching Comprehensively...")
            
            # Navigate to VPS
            self.driver.get(self.base_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "root"))
            )
            
            # Try to find login form first
            try:
                # Login with admin credentials
                username_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @type='email']"))
                )
                password_field = self.driver.find_element(By.XPATH, "//input[@type='password']")
                
                username_field.send_keys("admin")
                password_field.send_keys("admin123")
                
                # Find and click login button
                login_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Log') or contains(., 'Inlog')]")
                login_button.click()
                
                # Wait for dashboard to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Dashboard') or contains(., 'Landschap')]"))
                )
                
                self.log_test("Login for Language Testing", "PASS", "Successfully logged in")
                
            except Exception as e:
                self.log_test("Login for Language Testing", "WARN", f"Login step failed: {e}")
                # Continue anyway, might already be logged in
            
            # Test language switching
            self.test_language_switch_effects()
            
            return True
            
        except Exception as e:
            self.log_test("Language Switching Test", "FAIL", str(e))
            return False
    
    def test_language_switch_effects(self):
        """Test effects of language switching on different UI elements"""
        try:
            # Find language selector (combobox or select)
            language_selectors = [
                "//select[contains(@class, 'language') or contains(@aria-label, 'language')]",
                "//div[contains(@class, 'language-selector')]//select",
                "//select[option[contains(., 'Nederlands') or contains(., 'English')]]",
                "//combobox"
            ]
            
            language_element = None
            for selector in language_selectors:
                try:
                    language_element = self.driver.find_element(By.XPATH, selector)
                    break
                except Exception:
                    # Selector not found, try next
                    continue
            
            if not language_element:
                self.log_issue("Language Switching", "Language selector not found - cannot test language switching")
                return False
            
            # Get initial page text in Dutch
            initial_text = self.driver.find_element(By.TAG_NAME, "body").text
            dutch_texts = self.extract_dutch_texts(initial_text)
            
            # Switch to English
            self.switch_language_to_english(language_element)
            time.sleep(2)  # Wait for language change to take effect
            
            # Get page text after switch
            english_text = self.driver.find_element(By.TAG_NAME, "body").text
            english_texts = self.extract_english_texts(english_text)
            
            # Compare texts to identify what changed and what didn't
            self.compare_language_texts(dutch_texts, english_texts)
            
            # Test specific UI elements
            self.test_ui_elements_translation()
            
            return True
            
        except Exception as e:
            self.log_issue("Language Switch Effects", f"Error testing language effects: {e}")
            return False
    
    def extract_dutch_texts(self, text):
        """Extract Dutch-specific texts"""
        dutch_indicators = [
            "Leveranciers", "Planten", "Producten", "Klanten", "Projecten",
            "Instellingen", "Dashboard", "Toevoegen", "Bewerken", "Verwijderen",
            "Opslaan", "Annuleren", "Welkom", "Gegevens", "Afgerond", "In uitvoering"
        ]
        
        found_dutch = []
        for indicator in dutch_indicators:
            if indicator in text:
                found_dutch.append(indicator)
        
        return found_dutch
    
    def extract_english_texts(self, text):
        """Extract English-specific texts"""  
        english_indicators = [
            "Suppliers", "Plants", "Products", "Clients", "Projects",
            "Settings", "Dashboard", "Add", "Edit", "Delete",
            "Save", "Cancel", "Welcome", "Data", "Completed", "In Progress"
        ]
        
        found_english = []
        for indicator in english_indicators:
            if indicator in text:
                found_english.append(indicator)
        
        return found_english
    
    def switch_language_to_english(self, language_element):
        """Switch language to English"""
        try:
            # Try different methods to switch language
            if language_element.tag_name.lower() == "select":
                # It's a select element
                from selenium.webdriver.support.ui import Select
                select = Select(language_element)
                
                # Try to select English
                try:
                    select.select_by_visible_text("🇬🇧 English")
                except Exception:
                    try:
                        select.select_by_visible_text("English")
                    except Exception:
                        try:
                            select.select_by_value("en")
                        except Exception:
                            self.log_issue("Language Switching", "Could not find English option in language selector")
                            return False
            else:
                # Try clicking approach
                language_element.click()
                time.sleep(1)
                
                # Look for English option
                english_options = [
                    "//option[contains(., 'English')]",
                    "//div[contains(., 'English')]",
                    "//span[contains(., 'English')]"
                ]
                
                for option_xpath in english_options:
                    try:
                        english_option = self.driver.find_element(By.XPATH, option_xpath)
                        english_option.click()
                        break
                    except Exception:
                        # Option not found, try next xpath
                        continue
            
            self.log_test("Language Switch Action", "PASS", "Attempted to switch to English")
            return True
            
        except Exception as e:
            self.log_issue("Language Switch Action", f"Failed to switch language: {e}")
            return False
    
    def compare_language_texts(self, dutch_texts, english_texts):
        """Compare Dutch and English texts to identify translation issues"""
        print("\n📊 Language Comparison Results:")
        print(f"   Dutch texts found: {len(dutch_texts)} - {dutch_texts}")
        print(f"   English texts found: {len(english_texts)} - {english_texts}")
        
        # Check if language actually switched
        dutch_only = set(dutch_texts) - set(english_texts)
        english_only = set(english_texts) - set(dutch_texts)
        unchanged = set(dutch_texts) & set(english_texts)
        
        if len(english_only) > 0:
            self.log_test("Language Translation Working", "PASS", f"Found {len(english_only)} English translations")
        else:
            self.log_issue("Language Translation", "No English translations detected - language switching may not be working")
        
        if len(dutch_only) > 0:
            self.log_issue("Language Translation", f"These texts remained in Dutch: {list(dutch_only)}")
            
        if len(unchanged) > 0:
            self.log_issue("Language Translation", f"These texts appear in both languages (may be untranslated): {list(unchanged)}")
    
    def test_ui_elements_translation(self):
        """Test specific UI elements for translation"""
        try:
            # Test navigation elements
            nav_elements = self.driver.find_elements(By.XPATH, "//nav//a | //nav//button")
            
            untranslated_nav = []
            for element in nav_elements[:10]:  # Test first 10 nav elements
                text = element.text.strip()
                if text and self.is_dutch_text(text):
                    untranslated_nav.append(text)
            
            if untranslated_nav:
                self.log_issue("Navigation Translation", f"Untranslated navigation elements: {untranslated_nav}")
            else:
                self.log_test("Navigation Translation", "PASS", "Navigation elements appear to be translated")
            
            # Test button elements
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            untranslated_buttons = []
            
            for button in buttons[:20]:  # Test first 20 buttons
                text = button.text.strip()
                if text and self.is_dutch_text(text):
                    untranslated_buttons.append(text)
            
            if untranslated_buttons:
                self.log_issue("Button Translation", f"Untranslated buttons: {untranslated_buttons}")
            else:
                self.log_test("Button Translation", "PASS", "Buttons appear to be translated")
                
        except Exception as e:
            self.log_issue("UI Elements Translation", f"Error testing UI elements: {e}")
    
    def is_dutch_text(self, text):
        """Check if text contains Dutch indicators"""
        dutch_words = [
            "Leveranciers", "Planten", "Producten", "Klanten", "Projecten",
            "Toevoegen", "Bewerken", "Verwijderen", "Opslaan", "Annuleren",
            "Instellingen", "Welkom", "Gegevens", "van", "en", "het", "de"
        ]
        
        return any(word in text for word in dutch_words)
    
    def test_all_panels_comprehensive(self):
        """Test all panels mentioned: Settings and other sections"""
        if not self.driver:
            self.log_test("Panel Testing Setup", "FAIL", "Selenium not available")
            return False
            
        panels_to_test = [
            ("Settings", ["//a[contains(., 'Settings') or contains(., 'Instellingen')]", "//nav//a[contains(@href, 'settings')]"]),
            ("Suppliers", ["//a[contains(., 'Suppliers') or contains(., 'Leveranciers')]", "//nav//a[contains(@href, 'suppliers')]"]),
            ("Plants", ["//a[contains(., 'Plants') or contains(., 'Planten')]", "//nav//a[contains(@href, 'plants')]"]),
            ("Products", ["//a[contains(., 'Products') or contains(., 'Producten')]", "//nav//a[contains(@href, 'products')]"]),
            ("Clients", ["//a[contains(., 'Clients') or contains(., 'Klanten')]", "//nav//a[contains(@href, 'clients')]"]),
            ("Projects", ["//a[contains(., 'Projects') or contains(., 'Projecten')]", "//nav//a[contains(@href, 'projects')]"]),
            ("Reports", ["//a[contains(., 'Reports') or contains(., 'Rapporten')]", "//nav//a[contains(@href, 'reports')]"]),
            ("Photos", ["//a[contains(., 'Photos') or contains(., 'Foto')]", "//nav//a[contains(@href, 'photos')]"])
        ]
        
        panel_results = {}
        
        for panel_name, selectors in panels_to_test:
            result = self.test_individual_panel(panel_name, selectors)
            panel_results[panel_name] = result
        
        # Summary
        working_panels = sum(1 for r in panel_results.values() if r)
        total_panels = len(panel_results)
        
        self.log_test("Panel Testing Summary", "PASS" if working_panels == total_panels else "WARN", 
                     f"{working_panels}/{total_panels} panels working correctly")
        
        return panel_results
    
    def test_individual_panel(self, panel_name, selectors):
        """Test an individual panel"""
        try:
            print(f"\n🔍 Testing {panel_name} Panel...")
            
            # Try to find and click the panel link
            panel_link = None
            for selector in selectors:
                try:
                    panel_link = self.driver.find_element(By.XPATH, selector)
                    break
                except Exception:
                    # Selector not found, try next
                    continue
            
            if not panel_link:
                self.log_issue(f"{panel_name} Panel", f"Could not find navigation link for {panel_name}")
                return False
            
            # Click the panel link
            panel_link.click()
            time.sleep(3)  # Wait for panel to load
            
            # Check if panel loaded correctly
            current_url = self.driver.current_url
            if panel_name.lower() in current_url.lower():
                self.log_test(f"{panel_name} Navigation", "PASS", f"Successfully navigated to {panel_name}")
            else:
                self.log_issue(f"{panel_name} Panel", f"Navigation may have failed - URL: {current_url}")
            
            # Test panel-specific functionality
            if panel_name == "Settings":
                return self.test_settings_panel()
            if panel_name == "Plants":
                return self.test_plants_panel_input_fields()
            return self.test_generic_panel_functionality(panel_name)
                
        except Exception as e:
            self.log_issue(f"{panel_name} Panel", f"Error testing panel: {e}")
            return False
    
    def test_settings_panel(self):
        """Test Settings panel specifically"""
        try:
            # Look for settings tabs/sections
            settings_sections = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'tab') or contains(@class, 'section')]")
            
            if len(settings_sections) == 0:
                self.log_issue("Settings Panel", "No settings sections found")
                return False
            
            self.log_test("Settings Panel Load", "PASS", f"Found {len(settings_sections)} settings sections")
            
            # Test language settings if available
            language_settings = self.driver.find_elements(By.XPATH, "//*[contains(., 'Language') or contains(., 'Taal')]")
            if language_settings:
                self.log_test("Language Settings", "PASS", "Language settings section found")
            else:
                self.log_issue("Language Settings", "Language settings section not found in Settings")
            
            # Check for missing translations in settings
            settings_text = self.driver.find_element(By.TAG_NAME, "body").text
            if self.has_missing_translations(settings_text):
                self.log_issue("Settings Translation", "Found missing translations in Settings panel")
            
            return True
            
        except Exception as e:
            self.log_issue("Settings Panel Test", f"Error testing settings: {e}")
            return False
    
    def test_plants_panel_input_fields(self):
        """Test Plants panel input field issues"""
        try:
            # Look for Add Plant button
            add_buttons = self.driver.find_elements(By.XPATH, "//button[contains(., 'Add') or contains(., 'Toevoegen')]")
            
            if not add_buttons:
                self.log_issue("Plants Panel", "No Add button found in Plants panel")
                return False
            
            # Click Add Plant button
            add_buttons[0].click()
            time.sleep(2)
            
            # Look for input fields in the modal/form
            input_fields = self.driver.find_elements(By.XPATH, "//input[@type='text'] | //textarea")
            
            if len(input_fields) == 0:
                self.log_issue("Plants Input Fields", "No input fields found in Add Plant form")
                return False
            
            self.log_test("Plants Form Display", "PASS", f"Found {len(input_fields)} input fields")
            
            # Test input field behavior (the reactivation issue)
            self.test_input_field_behavior(input_fields[0])
            
            return True
            
        except Exception as e:
            self.log_issue("Plants Panel Input Test", f"Error testing input fields: {e}")
            return False
    
    def test_input_field_behavior(self, input_field):
        """Test the specific input field reactivation issue"""
        try:
            # Focus on the input field
            input_field.click()
            time.sleep(0.5)
            
            # Type some characters one by one to test reactivation issue
            test_text = "TestPlant"
            issues_found = []
            
            for i, char in enumerate(test_text):
                input_field.send_keys(char)
                time.sleep(0.2)  # Small delay between characters
                
                # Check if input field still has focus
                active_element = self.driver.switch_to.active_element
                if active_element != input_field:
                    issues_found.append(f"Lost focus after character {i+1} ('{char}')")
                
                # Check current value
                current_value = input_field.get_attribute("value")
                expected_value = test_text[:i+1]
                
                if current_value != expected_value:
                    issues_found.append(f"Value mismatch after '{char}': expected '{expected_value}', got '{current_value}'")
            
            if issues_found:
                self.log_issue("Input Field Behavior", f"Input field issues found: {issues_found}")
            else:
                self.log_test("Input Field Behavior", "PASS", "Input field behaves correctly")
            
            # Clear the field
            input_field.clear()
            
        except Exception as e:
            self.log_issue("Input Field Behavior Test", f"Error testing input behavior: {e}")
    
    def test_generic_panel_functionality(self, panel_name):
        """Test generic panel functionality"""
        try:
            # Check if panel has content
            content_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'content') or contains(@class, 'main')]")
            
            if len(content_elements) == 0:
                self.log_issue(f"{panel_name} Content", f"No content found in {panel_name} panel")
                return False
            
            # Check for error messages
            error_elements = self.driver.find_elements(By.XPATH, "//*[contains(., 'Error') or contains(., 'Fout')]")
            if error_elements:
                self.log_issue(f"{panel_name} Errors", f"Found error messages in {panel_name}")
                return False
            
            # Check for loading states
            loading_elements = self.driver.find_elements(By.XPATH, "//*[contains(., 'Loading') or contains(., 'Laden')]")
            if loading_elements:
                self.log_test(f"{panel_name} Loading", "INFO", f"Found loading states in {panel_name}")
            
            self.log_test(f"{panel_name} Functionality", "PASS", f"{panel_name} panel appears functional")
            return True
            
        except Exception as e:
            self.log_issue(f"{panel_name} Generic Test", f"Error in generic test: {e}")
            return False
    
    def has_missing_translations(self, text):
        """Check for missing translations patterns"""
        # Common patterns that indicate missing translations
        missing_patterns = [
            r"\b[a-z]+\.[a-z]+\b",  # dot notation like 'plants.title'
            r"\{[^}]+\}",           # placeholder patterns like {name}
            r"undefined",           # undefined values
            r"null",                # null values
            r"[A-Z_]{3,}",         # ALL_CAPS constants
        ]
        
        return any(re.search(pattern, text) for pattern in missing_patterns)
    
    def identify_missing_features(self):
        """Identify features and functions that still need work"""
        missing_features = {
            "incomplete_translations": [],
            "broken_functionality": [],
            "ui_issues": [],
            "performance_issues": []
        }
        
        # Analyze test results to identify missing features
        for result in self.test_results:
            if result["status"] == "FAIL":
                missing_features["broken_functionality"].append(result["test"])
            elif result["status"] == "WARN":
                missing_features["ui_issues"].append(result["test"])
        
        # Analyze issues to categorize them
        for issue in self.issues_found:
            if "translation" in issue["category"].lower():
                missing_features["incomplete_translations"].append(issue["issue"])
            elif "input" in issue["category"].lower() or "field" in issue["category"].lower():
                missing_features["ui_issues"].append(issue["issue"])
        
        return missing_features
    
    def generate_comprehensive_report(self):
        """Generate comprehensive report addressing all @HANSKMIEL concerns"""
        missing_features = self.identify_missing_features()
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warning_tests = len([r for r in self.test_results if r["status"] == "WARN"])
        total_issues = len(self.issues_found)
        
        print("\n" + "="*80)
        print("ENHANCED VPS TESTING REPORT - ADDRESSING @HANSKMIEL CONCERNS")
        print("="*80)
        print(f"🌐 VPS URL: {self.base_url}")
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warning_tests}")
        print(f"🔍 Issues Found: {total_issues}")
        
        print("\n🌍 LANGUAGE SWITCHING ANALYSIS:")
        print("-" * 40)
        translation_issues = [i for i in self.issues_found if "translation" in i["category"].lower()]
        if translation_issues:
            print("❌ Language switching issues identified:")
            for issue in translation_issues[:5]:  # Show first 5
                print(f"   • {issue['issue']}")
        else:
            print("✅ No major language switching issues found")
        
        print("\n🎛️ PANEL TESTING RESULTS:")
        print("-" * 40)
        panel_issues = [i for i in self.issues_found if "panel" in i["category"].lower()]
        if panel_issues:
            print("❌ Panel issues identified:")
            for issue in panel_issues:
                print(f"   • {issue['issue']}")
        else:
            print("✅ All tested panels appear functional")
        
        print("\n📝 INPUT FIELD ANALYSIS:")
        print("-" * 40)
        input_issues = [i for i in self.issues_found if "input" in i["category"].lower() or "field" in i["category"].lower()]
        if input_issues:
            print("❌ Input field issues identified:")
            for issue in input_issues:
                print(f"   • {issue['issue']}")
        else:
            print("✅ No input field issues detected")
        
        print("\n🚧 MISSING FEATURES & FUNCTIONS:")
        print("-" * 40)
        if missing_features["incomplete_translations"]:
            print("🌍 Translation gaps:")
            for item in missing_features["incomplete_translations"][:3]:
                print(f"   • {item}")
        
        if missing_features["broken_functionality"]:
            print("🔧 Broken functionality:")
            for item in missing_features["broken_functionality"][:3]:
                print(f"   • {item}")
        
        if missing_features["ui_issues"]:
            print("🎨 UI issues:")
            for item in missing_features["ui_issues"][:3]:
                print(f"   • {item}")
        
        print("\n" + "="*80)
        
        # Save detailed report
        report_data = {
            "vps_url": self.base_url,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "issues_found": total_issues
            },
            "detailed_results": self.test_results,
            "issues_found": self.issues_found,
            "missing_features": missing_features
        }
        
        with open("vps_enhanced_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        return total_issues == 0 and failed_tests == 0
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()
    
    def run_enhanced_testing(self):
        """Run all enhanced tests addressing @HANSKMIEL concerns"""
        print("🚀 Starting Enhanced VPS Testing to Address Specific Issues...")
        print(f"🌐 Testing VPS at: {self.base_url}")
        print("🎯 Focus Areas: Language switching, All panels, Missing texts, Input fields, Missing features")
        print("-"*80)
        
        # Setup Selenium for UI testing
        selenium_available = self.setup_selenium()
        
        if selenium_available:
            # Test language switching comprehensively
            self.test_language_switching_comprehensive()
            
            # Test all panels comprehensively  
            self.test_all_panels_comprehensive()
        else:
            self.log_test("UI Testing", "WARN", "Selenium not available - limited to API testing")
        
        # Generate comprehensive report
        success = self.generate_comprehensive_report()
        
        # Cleanup
        self.cleanup()
        
        return success

def main():
    tester = VPSEnhancedTester()
    success = tester.run_enhanced_testing()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()