#!/usr/bin/env python3
"""
Advanced Input Field Investigation
Investigating the specific input field reactivation issue mentioned by @HANSKMIEL
Focus: Text truncation, focus loss, controlled input behavior
"""

import json
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class InputFieldInvestigator:
    def __init__(self, base_url="http://72.60.176.200:8080"):
        self.base_url = base_url
        self.driver = None
        self.investigation_results = []
        self.issues_found = []
        
    def setup_driver(self):
        """Setup Chrome WebDriver with detailed logging"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--v=1")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(5)
            return True
        except Exception as e:
            print(f"❌ Failed to setup WebDriver: {e}")
            return False
    
    def log_result(self, test_name, status, details=""):
        """Log investigation results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.investigation_results.append(result)
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
        """Login to VPS"""
        try:
            print("🚀 Logging into VPS...")
            self.driver.get(self.base_url)
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check if already logged in
            try:
                self.driver.find_element(By.XPATH, "//h1[contains(text(), 'Dashboard') or contains(text(), 'Landschap')]")
                self.log_result("Already Logged In", "PASS", "Already authenticated")
                return True
            except NoSuchElementException:
                pass
            
            # Login
            try:
                username_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @type='email' or @name='username']"))
                )
                password_field = self.driver.find_element(By.XPATH, "//input[@type='password' or @name='password']")
                
                username_field.clear()
                username_field.send_keys("admin")
                password_field.clear()
                password_field.send_keys("admin123")
                
                login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Log') or contains(text(), 'Inlog') or @type='submit']")
                login_button.click()
                
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Dashboard') or contains(text(), 'Landschap')]"))
                )
                
                self.log_result("VPS Login", "PASS", "Successfully logged in")
                return True
                
            except Exception as e:
                self.log_issue("Login", f"Failed to login: {e}")
                return False
                
        except Exception as e:
            self.log_issue("VPS Access", f"Failed to access VPS: {e}")
            return False
    
    def navigate_to_plants(self):
        """Try to navigate to Plants section"""
        try:
            print("🌱 Attempting to navigate to Plants section...")
            
            # Try multiple navigation strategies
            navigation_strategies = [
                ("Direct URL", f"{self.base_url}/plants"),
                ("Navigation Link", "//a[contains(text(), 'Plants') or contains(text(), 'Planten')]"),
                ("Menu Item", "//nav//a[contains(@href, 'plants')]"),
                ("Sidebar Link", "//aside//a[contains(@href, 'plants')]"),
                ("Button Navigation", "//button[contains(text(), 'Plants') or contains(text(), 'Planten')]")
            ]
            
            for strategy_name, selector in navigation_strategies:
                try:
                    if strategy_name == "Direct URL":
                        self.driver.get(selector)
                        time.sleep(2)
                    else:
                        element = self.driver.find_element(By.XPATH, selector)
                        self.driver.execute_script("arguments[0].click();", element)
                        time.sleep(2)
                    
                    # Check if we're on plants page
                    try:
                        self.driver.find_element(By.XPATH, "//h1[contains(text(), 'Plants') or contains(text(), 'Planten')] | //div[contains(@class, 'plants')] | //button[contains(text(), 'Add Plant') or contains(text(), 'Plant Toevoegen')]")
                        self.log_result(f"Navigation via {strategy_name}", "PASS", "Successfully reached Plants section")
                        return True
                    except NoSuchElementException:
                        continue
                        
                except Exception:
                    continue
            
            self.log_issue("Navigation", "Failed to navigate to Plants section with any strategy")
            return False
            
        except Exception as e:
            self.log_issue("Plants Navigation", f"Error navigating to plants: {e}")
            return False
    
    def investigate_add_plant_form(self):
        """Investigate the Add Plant form and input behavior"""
        try:
            print("📝 Investigating Add Plant form...")
            
            # Try to find and click Add Plant button
            add_button_selectors = [
                "//button[contains(text(), 'Add Plant')]",
                "//button[contains(text(), 'Plant Toevoegen')]",
                "//button[contains(text(), 'Add')]",
                "//button[contains(text(), 'Toevoegen')]",
                "//button[contains(@class, 'add')]",
                "//a[contains(text(), 'Add Plant')]"
            ]
            
            add_button = None
            for selector in add_button_selectors:
                try:
                    add_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"   Found Add button with selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not add_button:
                self.log_issue("Add Plant Form", "Add Plant button not found")
                return False
            
            # Click the Add button
            self.driver.execute_script("arguments[0].click();", add_button)
            time.sleep(2)
            
            # Look for form modal or form container
            form_selectors = [
                "//form",
                "//div[contains(@class, 'modal')]//form",
                "//div[contains(@class, 'dialog')]//form",
                "//div[contains(@role, 'dialog')]//form"
            ]
            
            form_element = None
            for selector in form_selectors:
                try:
                    form_element = self.driver.find_element(By.XPATH, selector)
                    print(f"   Found form with selector: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not form_element:
                self.log_issue("Add Plant Form", "Add Plant form not found after clicking Add button")
                return False
            
            # Find input fields in the form
            input_fields = form_element.find_elements(By.XPATH, ".//input[@type='text'] | .//textarea")
            
            if len(input_fields) == 0:
                self.log_issue("Input Fields", "No text input fields found in Add Plant form")
                return False
            
            self.log_result("Add Plant Form Access", "PASS", f"Successfully accessed form with {len(input_fields)} input fields")
            
            # Test each input field
            for i, input_field in enumerate(input_fields[:3]):  # Test first 3 fields
                self.investigate_input_field_behavior(input_field, f"Field {i+1}")
            
            return True
            
        except Exception as e:
            self.log_issue("Add Plant Form Investigation", f"Error investigating form: {e}")
            return False
    
    def investigate_input_field_behavior(self, input_field, field_name):
        """Deep investigation of input field behavior"""
        try:
            print(f"      🔍 Testing {field_name}...")
            
            # Get field attributes
            field_type = input_field.get_attribute("type")
            field_name_attr = input_field.get_attribute("name")
            field_placeholder = input_field.get_attribute("placeholder")
            input_field.get_attribute("value")
            input_field.get_attribute("id")
            
            self.log_result(f"{field_name} Attributes", "INFO", 
                          f"Type: {field_type}, Name: {field_name_attr}, Placeholder: {field_placeholder}")
            
            # Clear and focus on field
            input_field.clear()
            input_field.click()
            time.sleep(0.5)
            
            # Test character-by-character input
            test_texts = [
                "A",  # Single character
                "Test",  # Short text
                "TestPlantName",  # Medium text  
                "Very Long Plant Name With Many Characters",  # Long text
                "Plant123!@#$%",  # Special characters and numbers
                "Åcér Plätänøïdês",  # Unicode characters
            ]
            
            for test_text in test_texts:
                try:
                    result = self.test_input_behavior(input_field, test_text, field_name)
                    if not result:
                        break
                except StaleElementReferenceException:
                    self.log_issue(f"{field_name} Input", "Input field became stale - potential DOM manipulation issue")
                    break
                except Exception as e:
                    self.log_issue(f"{field_name} Input", f"Error during input test: {e}")
                    break
            
        except Exception as e:
            self.log_issue(f"{field_name} Investigation", f"Error investigating field: {e}")
    
    def test_input_behavior(self, input_field, test_text, field_name):
        """Test specific input behavior patterns"""
        try:
            # Clear field
            input_field.clear()
            time.sleep(0.2)
            
            # Test typing behavior
            focus_issues = []
            value_issues = []
            
            # Type character by character with detailed monitoring
            for i, char in enumerate(test_text):
                try:
                    # Check focus before typing
                    active_element = self.driver.switch_to.active_element
                    if active_element != input_field:
                        focus_issues.append(f"Lost focus before character {i+1}")
                        input_field.click()  # Refocus
                        time.sleep(0.1)
                    
                    # Type character
                    input_field.send_keys(char)
                    time.sleep(0.1)  # Small delay
                    
                    # Check value after typing
                    current_value = input_field.get_attribute("value")
                    expected_value = test_text[:i+1]
                    
                    if current_value != expected_value:
                        value_issues.append(f"Value mismatch at char {i+1}: expected '{expected_value}', got '{current_value}'")
                    
                    # Check focus after typing
                    active_element = self.driver.switch_to.active_element
                    if active_element != input_field:
                        focus_issues.append(f"Lost focus after character {i+1} ('{char}')")
                    
                    # Test for truncation
                    if len(current_value) < len(expected_value):
                        self.log_issue(f"{field_name} Truncation", 
                                     f"Text truncated: expected {len(expected_value)} chars, got {len(current_value)} chars")
                    
                except Exception as e:
                    self.log_issue(f"{field_name} Character Input", f"Error typing character '{char}': {e}")
                    return False
            
            # Final value check
            final_value = input_field.get_attribute("value")
            if final_value != test_text:
                self.log_issue(f"{field_name} Final Value", 
                             f"Final value mismatch: expected '{test_text}', got '{final_value}'")
            
            # Report issues
            if focus_issues:
                self.log_issue(f"{field_name} Focus", f"Focus issues: {focus_issues[:3]}")  # First 3 issues
            
            if value_issues:
                self.log_issue(f"{field_name} Value", f"Value issues: {value_issues[:3]}")  # First 3 issues
            
            if not focus_issues and not value_issues:
                self.log_result(f"{field_name} Input Test", "PASS", f"Successfully typed '{test_text}'")
            
            # Test rapid typing
            input_field.clear()
            time.sleep(0.1)
            input_field.send_keys(test_text)  # Type all at once
            time.sleep(0.2)
            
            rapid_value = input_field.get_attribute("value")
            if rapid_value != test_text:
                self.log_issue(f"{field_name} Rapid Typing", 
                             f"Rapid typing failed: expected '{test_text}', got '{rapid_value}'")
            else:
                self.log_result(f"{field_name} Rapid Typing", "PASS", "Rapid typing successful")
            
            return True
            
        except Exception as e:
            self.log_issue(f"{field_name} Input Behavior", f"Error testing input behavior: {e}")
            return False
    
    def test_alternative_navigation(self):
        """Test if we can access plants through alternative methods"""
        try:
            print("🔄 Testing alternative navigation methods...")
            
            # Try direct API call to see if data is available
            self.driver.execute_script("""
                fetch('/api/plants')
                    .then(response => response.json())
                    .then(data => {
                        window.plantsApiResult = data;
                    })
                    .catch(error => {
                        window.plantsApiError = error.toString();
                    });
            """)
            
            time.sleep(2)
            
            api_result = self.driver.execute_script("return window.plantsApiResult;")
            api_error = self.driver.execute_script("return window.plantsApiError;")
            
            if api_result:
                self.log_result("Plants API Access", "PASS", f"API returned {len(api_result.get('plants', []))} plants")
            elif api_error:
                self.log_issue("Plants API", f"API error: {api_error}")
            
            # Try to see current page structure
            page_source = self.driver.page_source
            if "plants" in page_source.lower():
                plant_mentions = page_source.lower().count("plants")
                self.log_result("Plants Content Detection", "PASS", f"Found {plant_mentions} mentions of 'plants' in page")
            else:
                self.log_issue("Plants Content", "No 'plants' content found in current page")
            
        except Exception as e:
            self.log_issue("Alternative Navigation", f"Error testing alternatives: {e}")
    
    def generate_investigation_report(self):
        """Generate comprehensive investigation report"""
        total_tests = len(self.investigation_results)
        passed_tests = len([r for r in self.investigation_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.investigation_results if r["status"] == "FAIL"])
        total_issues = len(self.issues_found)
        
        print("\n" + "="*80)
        print("INPUT FIELD INVESTIGATION REPORT")
        print("="*80)
        print(f"🌐 VPS URL: {self.base_url}")
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"🔍 Issues Found: {total_issues}")
        
        if total_issues > 0:
            print("\n🔍 DETAILED ISSUES:")
            print("-" * 40)
            for issue in self.issues_found:
                print(f"  [{issue['category']}] {issue['issue']}")
        
        # Check for specific patterns
        focus_issues = [i for i in self.issues_found if "focus" in i["issue"].lower()]
        truncation_issues = [i for i in self.issues_found if "truncat" in i["issue"].lower()]
        value_issues = [i for i in self.issues_found if "value" in i["issue"].lower()]
        
        print("\n📋 ISSUE PATTERNS:")
        print("-" * 40)
        print(f"  Focus Issues: {len(focus_issues)}")
        print(f"  Truncation Issues: {len(truncation_issues)}")
        print(f"  Value Issues: {len(value_issues)}")
        
        print("\n" + "="*80)
        
        # Save detailed report
        report_data = {
            "vps_url": self.base_url,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "issues_found": total_issues
            },
            "issue_patterns": {
                "focus_issues": len(focus_issues),
                "truncation_issues": len(truncation_issues),
                "value_issues": len(value_issues)
            },
            "detailed_results": self.investigation_results,
            "issues_found": self.issues_found
        }
        
        with open("input_field_investigation_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        return total_issues == 0
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()
    
    def run_investigation(self):
        """Run complete input field investigation"""
        print("🚀 Starting Input Field Investigation...")
        print(f"🌐 Testing VPS at: {self.base_url}")
        print("🎯 Focus: Input reactivation, text truncation, focus loss")
        print("-" * 80)
        
        if not self.setup_driver():
            return False
        
        try:
            # Login
            if not self.login_to_vps():
                return False
            
            # Try to navigate to plants
            if self.navigate_to_plants():
                # Investigate the form
                self.investigate_add_plant_form()
            else:
                # Test alternative methods
                self.test_alternative_navigation()
            
            # Generate report
            return self.generate_investigation_report()
            
        finally:
            self.cleanup()

def main():
    investigator = InputFieldInvestigator()
    success = investigator.run_investigation()
    exit_code = 0 if success else 1
    print(f"\n🏁 Investigation completed with exit code: {exit_code}")
    return exit_code

if __name__ == "__main__":
    import sys
    sys.exit(main())