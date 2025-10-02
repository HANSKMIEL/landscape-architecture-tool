#!/usr/bin/env python3
"""
Comprehensive UI Testing Script
Specifically tests the issues mentioned by @HANSKMIEL:
1. Language switching - only some texts change
2. Settings panel and other panels not tested
3. Input field reactivation issues
4. Missing texts identification
"""

import json
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class ComprehensiveUITester:
    def __init__(self, base_url="http://72.60.176.200:8080"):
        self.base_url = base_url
        self.driver = None
        self.test_results = []
        self.issues_found = []
        self.language_test_results = {}
        
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"❌ Failed to setup WebDriver: {e}")
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
    
    def login_to_vps(self):
        """Login to the VPS with admin credentials"""
        try:
            print("🚀 Navigating to VPS and logging in...")
            self.driver.get(self.base_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check if already logged in by looking for dashboard elements
            try:
                self.driver.find_element(By.XPATH, "//h1[contains(text(), 'Dashboard') or contains(text(), 'Landschap')]")
                self.log_test("Already Logged In", "PASS", "Already authenticated")
                return True
            except NoSuchElementException:
                pass
            
            # Find login form
            try:
                username_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @type='email' or @name='username']"))
                )
                password_field = self.driver.find_element(By.XPATH, "//input[@type='password' or @name='password']")
                
                # Clear and enter credentials
                username_field.clear()
                username_field.send_keys("admin")
                password_field.clear()
                password_field.send_keys("admin123")
                
                # Find and click login button
                login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Log') or contains(text(), 'Inlog') or @type='submit']")
                login_button.click()
                
                # Wait for dashboard to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Dashboard') or contains(text(), 'Landschap')]"))
                )
                
                self.log_test("VPS Login", "PASS", "Successfully logged in")
                return True
                
            except Exception as e:
                self.log_issue("Login", f"Failed to login: {e}")
                return False
                
        except Exception as e:
            self.log_issue("VPS Access", f"Failed to access VPS: {e}")
            return False
    
    def test_language_switching_comprehensive(self):
        """Test language switching across all components"""
        print("\n🌍 Testing Language Switching Comprehensively...")
        
        try:
            # Find language selector
            language_selectors = [
                "//select[contains(@class, 'language')]",
                "//select[option[contains(text(), 'English') or contains(text(), 'Nederlands')]]",
                "//div[contains(@class, 'language')]//select",
                "//select[@name='language']",
                "//div[contains(text(), 'Language') or contains(text(), 'Taal')]//select"
            ]
            
            language_element = None
            for selector in language_selectors:
                try:
                    language_element = self.driver.find_element(By.XPATH, selector)
                    print(f"   Found language selector with: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not language_element:
                self.log_issue("Language Switching", "No language selector found on page")
                return False
            
            # Get current page text to compare
            initial_body_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Test Dutch to English switching
            self.test_language_switch(language_element, "en", "English", initial_body_text)
            
            # Test English to Dutch switching  
            time.sleep(2)
            current_body_text = self.driver.find_element(By.TAG_NAME, "body").text
            self.test_language_switch(language_element, "nl", "Nederlands", current_body_text)
            
            return True
            
        except Exception as e:
            self.log_issue("Language Switching", f"Error during language switching test: {e}")
            return False
    
    def test_language_switch(self, language_element, target_lang, target_name, before_text):
        """Test switching to a specific language"""
        try:
            select = Select(language_element)
            
            # Try different ways to select the language
            selection_success = False
            try:
                select.select_by_value(target_lang)
                selection_success = True
            except:
                try:
                    select.select_by_visible_text(target_name)
                    selection_success = True
                except:
                    # Try finding option by partial text
                    options = select.options
                    for option in options:
                        if target_name.lower() in option.text.lower() or target_lang in option.get_attribute("value"):
                            option.click()
                            selection_success = True
                            break
            
            if not selection_success:
                self.log_issue("Language Selection", f"Could not select {target_name} language")
                return False
            
            # Wait for language change to take effect
            time.sleep(3)
            
            # Get text after language change
            after_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Analyze what changed
            self.analyze_language_change(before_text, after_text, target_lang, target_name)
            
            return True
            
        except Exception as e:
            self.log_issue("Language Switch", f"Error switching to {target_name}: {e}")
            return False
    
    def analyze_language_change(self, before_text, after_text, target_lang, target_name):
        """Analyze what changed during language switching"""
        
        # Define language-specific terms to look for
        dutch_terms = [
            "Leveranciers", "Planten", "Producten", "Klanten", "Projecten",
            "Instellingen", "Dashboard", "Toevoegen", "Bewerken", "Verwijderen",
            "Opslaan", "Annuleren", "Welkom", "Gegevens"
        ]
        
        english_terms = [
            "Suppliers", "Plants", "Products", "Clients", "Projects", 
            "Settings", "Dashboard", "Add", "Edit", "Delete",
            "Save", "Cancel", "Welcome", "Data"
        ]
        
        if target_lang == "en":
            expected_terms = english_terms
            unexpected_terms = dutch_terms
        else:
            expected_terms = dutch_terms
            unexpected_terms = english_terms
        
        found_expected = [term for term in expected_terms if term in after_text]
        found_unexpected = [term for term in unexpected_terms if term in after_text]
        
        # Store results
        self.language_test_results[target_name] = {
            "expected_found": found_expected,
            "unexpected_found": found_unexpected,
            "text_changed": before_text != after_text,
            "before_length": len(before_text),
            "after_length": len(after_text)
        }
        
        if len(found_expected) > 0:
            self.log_test(f"Language Switch to {target_name}", "PASS", 
                         f"Found {len(found_expected)} expected terms: {found_expected[:3]}...")
        else:
            self.log_issue("Language Translation", 
                          f"No expected {target_name} terms found after switching")
        
        if len(found_unexpected) > 0:
            self.log_issue("Incomplete Translation", 
                          f"Still found {len(found_unexpected)} {(target_name == 'English' and 'Dutch') or 'English'} terms: {found_unexpected[:3]}...")
    
    def test_all_panels(self):
        """Test all panels including Settings and other sections"""
        print("\n🎛️ Testing All Panels...")
        
        panels_to_test = [
            ("Settings", ["//a[contains(text(), 'Settings') or contains(text(), 'Instellingen')]"]),
            ("Suppliers", ["//a[contains(text(), 'Suppliers') or contains(text(), 'Leveranciers')]"]),
            ("Plants", ["//a[contains(text(), 'Plants') or contains(text(), 'Planten')]"]),
            ("Products", ["//a[contains(text(), 'Products') or contains(text(), 'Producten')]"]),
            ("Clients", ["//a[contains(text(), 'Clients') or contains(text(), 'Klanten')]"]),
            ("Projects", ["//a[contains(text(), 'Projects') or contains(text(), 'Projecten')]"]),
            ("Reports", ["//a[contains(text(), 'Reports') or contains(text(), 'Rapporten')]"]),
            ("Photos", ["//a[contains(text(), 'Photos') or contains(text(), 'Foto')]"])
        ]
        
        panel_results = {}
        
        for panel_name, selectors in panels_to_test:
            result = self.test_individual_panel(panel_name, selectors)
            panel_results[panel_name] = result
        
        # Summary
        working_panels = sum(1 for r in panel_results.values() if r)
        total_panels = len(panel_results)
        
        self.log_test("Panel Testing Summary", 
                     "PASS" if working_panels >= total_panels * 0.8 else "WARN",
                     f"{working_panels}/{total_panels} panels accessible")
        
        return panel_results
    
    def test_individual_panel(self, panel_name, selectors):
        """Test access to an individual panel"""
        try:
            print(f"   🔍 Testing {panel_name} panel...")
            
            # Try to find and click the panel link
            panel_link = None
            for selector in selectors:
                try:
                    panel_link = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not panel_link:
                self.log_issue(f"{panel_name} Panel", f"Navigation link not found for {panel_name}")
                return False
            
            # Click the panel link
            panel_link.click()
            time.sleep(2)
            
            # Check if panel loaded
            try:
                # Look for panel-specific content
                content_indicators = [
                    f"//h1[contains(text(), '{panel_name}')]",
                    f"//h2[contains(text(), '{panel_name}')]", 
                    "//div[contains(@class, 'content')]",
                    "//main",
                    "//div[contains(@class, 'panel')]"
                ]
                
                content_found = False
                for indicator in content_indicators:
                    try:
                        self.driver.find_element(By.XPATH, indicator)
                        content_found = True
                        break
                    except NoSuchElementException:
                        continue
                
                if content_found:
                    self.log_test(f"{panel_name} Panel Access", "PASS", f"Successfully accessed {panel_name}")
                    
                    # Test panel-specific functionality
                    if panel_name == "Settings":
                        self.test_settings_panel_functionality()
                    elif panel_name == "Plants":
                        self.test_plants_input_fields()
                    
                    return True
                self.log_issue(f"{panel_name} Panel", f"No content found after clicking {panel_name}")
                return False
                    
            except Exception as e:
                self.log_issue(f"{panel_name} Panel", f"Error checking panel content: {e}")
                return False
                
        except Exception as e:
            self.log_issue(f"{panel_name} Panel", f"Error testing panel: {e}")
            return False
    
    def test_settings_panel_functionality(self):
        """Test Settings panel specific functionality"""
        try:
            print("      🔧 Testing Settings panel functionality...")
            
            # Look for settings sections/tabs
            settings_elements = [
                "//div[contains(@class, 'tab') or contains(@class, 'setting')]",
                "//button[contains(@class, 'tab')]",
                "//div[contains(text(), 'Language') or contains(text(), 'Taal')]",
                "//div[contains(text(), 'Theme') or contains(text(), 'Thema')]"
            ]
            
            sections_found = 0
            for element_xpath in settings_elements:
                try:
                    elements = self.driver.find_elements(By.XPATH, element_xpath)
                    sections_found += len(elements)
                except:
                    continue
            
            if sections_found > 0:
                self.log_test("Settings Sections", "PASS", f"Found {sections_found} settings elements")
            else:
                self.log_issue("Settings Functionality", "No settings sections or tabs found")
            
            # Test language selector in settings if available
            try:
                self.driver.find_element(By.XPATH, "//select[option[contains(text(), 'English') or contains(text(), 'Nederlands')]]")
                self.log_test("Settings Language Selector", "PASS", "Language selector found in settings")
            except NoSuchElementException:
                self.log_issue("Settings Language", "No language selector found in settings panel")
            
        except Exception as e:
            self.log_issue("Settings Testing", f"Error testing settings: {e}")
    
    def test_plants_input_fields(self):
        """Test Plants panel input field behavior"""
        try:
            print("      🌱 Testing Plants input field behavior...")
            
            # Look for Add Plant button
            add_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Add') or contains(text(), 'Toevoegen')]")
            
            if not add_buttons:
                self.log_issue("Plants Input", "No Add button found in Plants panel")
                return False
            
            # Click Add Plant button
            add_buttons[0].click()
            time.sleep(2)
            
            # Look for input fields in modal/form
            input_fields = self.driver.find_elements(By.XPATH, "//input[@type='text'] | //textarea")
            
            if len(input_fields) == 0:
                self.log_issue("Plants Input", "No input fields found in Add Plant form")
                return False
            
            # Test input field behavior
            self.test_input_field_focus_behavior(input_fields[0])
            
            # Close modal by pressing Escape or clicking cancel
            try:
                cancel_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel') or contains(text(), 'Annuleren')]")
                cancel_button.click()
            except:
                self.driver.send_keys(Keys.ESCAPE)
            
            return True
            
        except Exception as e:
            self.log_issue("Plants Input Testing", f"Error testing input fields: {e}")
            return False
    
    def test_input_field_focus_behavior(self, input_field):
        """Test the specific input field focus/reactivation issue"""
        try:
            print("         🔍 Testing input field focus behavior...")
            
            # Clear field and focus
            input_field.clear()
            input_field.click()
            time.sleep(0.5)
            
            # Test typing behavior character by character
            test_text = "TestPlant"
            focus_issues = []
            
            for i, char in enumerate(test_text):
                # Type one character
                input_field.send_keys(char)
                time.sleep(0.3)  # Small delay to simulate real typing
                
                # Check if field still has focus
                active_element = self.driver.switch_to.active_element
                if active_element != input_field:
                    focus_issues.append(f"Lost focus after character {i+1} ('{char}')")
                    # Try to refocus
                    input_field.click()
                
                # Check current value
                current_value = input_field.get_attribute("value")
                expected_value = test_text[:i+1]
                
                if current_value != expected_value:
                    focus_issues.append(f"Value mismatch after '{char}': expected '{expected_value}', got '{current_value}'")
            
            if focus_issues:
                self.log_issue("Input Field Focus", f"Focus issues detected: {focus_issues}")
            else:
                self.log_test("Input Field Focus", "PASS", "No focus issues detected")
            
            # Clear the field
            input_field.clear()
            
        except Exception as e:
            self.log_issue("Input Field Focus Test", f"Error testing focus behavior: {e}")
    
    def identify_missing_texts(self):
        """Identify missing or untranslated texts"""
        print("\n📝 Identifying Missing Texts...")
        
        try:
            page_source = self.driver.page_source
            
            # Look for common patterns that indicate missing translations
            missing_patterns = [
                r"\b[a-z]+\.[a-z]+\.[a-z]+\b",  # dot notation like 'plants.categories.tree'
                r"\{[^}]+\}",                    # placeholder patterns like {name}
                r"undefined",                    # undefined values
                r"\bundefined\b",               # undefined as separate word
                r"null",                        # null values
                r"\[object Object\]",           # serialized objects
            ]
            
            import re
            missing_found = []
            
            for pattern in missing_patterns:
                matches = re.findall(pattern, page_source, re.IGNORECASE)
                if matches:
                    missing_found.extend(matches[:3])  # Limit to first 3 matches per pattern
            
            if missing_found:
                self.log_issue("Missing Texts", f"Found potential missing texts: {missing_found}")
            else:
                self.log_test("Missing Texts Check", "PASS", "No obvious missing text patterns found")
                
        except Exception as e:
            self.log_issue("Missing Text Analysis", f"Error analyzing missing texts: {e}")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warning_tests = len([r for r in self.test_results if r["status"] == "WARN"])
        total_issues = len(self.issues_found)
        
        print("\n" + "="*80)
        print("COMPREHENSIVE UI TEST REPORT - VPS VALIDATION")
        print("="*80)
        print(f"🌐 VPS URL: {self.base_url}")
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warning_tests}")
        print(f"🔍 Issues Found: {total_issues}")
        
        print("\n🌍 LANGUAGE SWITCHING RESULTS:")
        print("-" * 40)
        for lang, results in self.language_test_results.items():
            print(f"Language: {lang}")
            print(f"  Expected terms found: {len(results['expected_found'])}")
            print(f"  Unexpected terms found: {len(results['unexpected_found'])}")
            print(f"  Text changed: {results['text_changed']}")
            if results["unexpected_found"]:
                print(f"  Issues: {results['unexpected_found'][:3]}...")
        
        if total_issues > 0:
            print("\n🔍 ISSUES FOUND:")
            print("-" * 40)
            for issue in self.issues_found:
                print(f"  [{issue['category']}] {issue['issue']}")
        
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
            "language_test_results": self.language_test_results,
            "detailed_results": self.test_results,
            "issues_found": self.issues_found
        }
        
        with open("comprehensive_ui_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        return total_issues == 0 and failed_tests == 0
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()
    
    def run_comprehensive_tests(self):
        """Run all comprehensive UI tests"""
        print("🚀 Starting Comprehensive UI Testing...")
        print(f"🌐 Testing VPS at: {self.base_url}")
        print("🎯 Focus: Language switching, All panels, Input fields, Missing texts")
        print("-" * 80)
        
        if not self.setup_driver():
            return False
        
        try:
            # Login to VPS
            if not self.login_to_vps():
                return False
            
            # Test language switching comprehensively
            self.test_language_switching_comprehensive()
            
            # Test all panels
            self.test_all_panels()
            
            # Identify missing texts
            self.identify_missing_texts()
            
            # Generate comprehensive report
            return self.generate_comprehensive_report()
            
            
        finally:
            self.cleanup()

def main():
    tester = ComprehensiveUITester()
    success = tester.run_comprehensive_tests()
    exit_code = 0 if success else 1
    print(f"\n🏁 Test completed with exit code: {exit_code}")
    return exit_code

if __name__ == "__main__":
    import sys
    sys.exit(main())