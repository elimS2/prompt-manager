"""
Unit tests for prompt list JavaScript functionality.
"""
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


class TestPromptListJavaScript:
    """Test cases for prompt list JavaScript functionality."""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Set up Chrome driver for testing."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        yield driver
        driver.quit()
    
    def test_content_toggle_functionality(self, driver, live_server):
        """Test that content toggle buttons work correctly."""
        # Navigate to prompts list page
        driver.get(f"{live_server.url}/prompts")
        
        # Find toggle buttons
        toggle_buttons = driver.find_elements(By.CLASS_NAME, "toggle-content-btn")
        
        if toggle_buttons:
            # Click first toggle button
            toggle_buttons[0].click()
            
            # Wait for content to appear
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "content-preview"))
            )
            
            # Verify content is visible
            content_preview = driver.find_element(By.CLASS_NAME, "content-preview")
            assert content_preview.is_displayed()
            
            # Click again to hide
            toggle_buttons[0].click()
            
            # Wait for content to disappear
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "content-preview"))
            )
    
    def test_copy_functionality(self, driver, live_server):
        """Test that copy buttons work correctly."""
        # Navigate to prompts list page
        driver.get(f"{live_server.url}/prompts")
        
        # Find copy buttons
        copy_buttons = driver.find_elements(By.CLASS_NAME, "copy-content-btn")
        
        if copy_buttons:
            # Get original button text
            original_text = copy_buttons[0].text
            
            # Click copy button
            copy_buttons[0].click()
            
            # Wait for success state
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "btn-success"))
            )
            
            # Verify button changed to success state
            success_button = driver.find_element(By.CLASS_NAME, "btn-success")
            assert "bi-check" in success_button.get_attribute("innerHTML")
    
    def test_checkbox_selection(self, driver, live_server):
        """Test that checkbox selection works for merge functionality."""
        # Navigate to prompts list page
        driver.get(f"{live_server.url}/prompts")
        
        # Find checkboxes
        checkboxes = driver.find_elements(By.CLASS_NAME, "prompt-checkbox")
        merge_btn = driver.find_element(By.ID, "mergeBtn")
        
        if len(checkboxes) >= 2:
            # Initially merge button should be disabled
            assert merge_btn.get_attribute("disabled") is not None
            
            # Select first checkbox
            checkboxes[0].click()
            
            # Merge button should still be disabled (need 2+ selections)
            assert merge_btn.get_attribute("disabled") is not None
            
            # Select second checkbox
            checkboxes[1].click()
            
            # Merge button should now be enabled
            assert merge_btn.get_attribute("disabled") is None
    
    def test_keyboard_shortcuts(self, driver, live_server):
        """Test keyboard shortcuts functionality."""
        # Navigate to prompts list page
        driver.get(f"{live_server.url}/prompts")
        
        # Test Ctrl+K for search focus
        search_input = driver.find_element(By.CSS_SELECTOR, "input[type='search']")
        
        # Press Ctrl+K
        from selenium.webdriver.common.action_chains import ActionChains
        actions = ActionChains(driver)
        actions.key_down(Keys.CONTROL).send_keys('k').key_up(Keys.CONTROL).perform()
        
        # Verify search input is focused
        assert driver.switch_to.active_element == search_input
    
    def test_filter_functionality(self, driver, live_server):
        """Test that filter radio buttons work correctly."""
        # Navigate to prompts list page
        driver.get(f"{live_server.url}/prompts")
        
        # Find filter inputs
        filter_inputs = driver.find_elements(By.CSS_SELECTOR, "input[name='is_active']")
        
        if filter_inputs:
            # Click on "Active" filter
            active_filter = None
            for input_elem in filter_inputs:
                if input_elem.get_attribute("value") == "true":
                    active_filter = input_elem
                    break
            
            if active_filter:
                active_filter.click()
                
                # Verify URL changed
                WebDriverWait(driver, 10).until(
                    lambda d: "is_active=true" in d.current_url
                )
    
    def test_responsive_design(self, driver, live_server):
        """Test responsive design on mobile viewport."""
        # Set mobile viewport
        driver.set_window_size(375, 667)  # iPhone SE size
        
        # Navigate to prompts list page
        driver.get(f"{live_server.url}/prompts")
        
        # Verify layout is responsive
        cards = driver.find_elements(By.CLASS_NAME, "prompt-card")
        if cards:
            # Check that cards are properly sized for mobile
            card_width = cards[0].size['width']
            viewport_width = driver.execute_script("return window.innerWidth;")
            
            # Card should be close to viewport width (accounting for padding)
            assert card_width > viewport_width * 0.9
    
    def test_accessibility_features(self, driver, live_server):
        """Test accessibility features."""
        # Navigate to prompts list page
        driver.get(f"{live_server.url}/prompts")
        
        # Check for proper ARIA labels
        copy_buttons = driver.find_elements(By.CLASS_NAME, "copy-content-btn")
        if copy_buttons:
            assert copy_buttons[0].get_attribute("title") == "Copy content"
        
        toggle_buttons = driver.find_elements(By.CLASS_NAME, "toggle-content-btn")
        if toggle_buttons:
            assert toggle_buttons[0].get_attribute("title") == "Toggle content"
        
        # Check for proper focus indicators
        copy_buttons[0].click()
        assert "outline" in copy_buttons[0].get_attribute("class") or "focus" in copy_buttons[0].get_attribute("class")


class TestPromptListCSS:
    """Test cases for prompt list CSS styling."""
    
    def test_content_preview_styles(self, driver, live_server):
        """Test that content preview has proper styling."""
        driver.get(f"{live_server.url}/prompts")
        
        # Find content preview
        content_previews = driver.find_elements(By.CLASS_NAME, "content-preview")
        
        if content_previews:
            # Check background color
            background_color = content_previews[0].value_of_css_property("background-color")
            assert background_color != "rgba(0, 0, 0, 0)"  # Should have background
            
            # Check border radius
            border_radius = content_previews[0].value_of_css_property("border-radius")
            assert border_radius != "0px"  # Should have rounded corners
    
    def test_button_styles(self, driver, live_server):
        """Test that buttons have proper styling."""
        driver.get(f"{live_server.url}/prompts")
        
        # Check copy button styles
        copy_buttons = driver.find_elements(By.CLASS_NAME, "copy-content-btn")
        if copy_buttons:
            # Check border radius
            border_radius = copy_buttons[0].value_of_css_property("border-radius")
            assert border_radius != "0px"  # Should have rounded corners
            
            # Check transition
            transition = copy_buttons[0].value_of_css_property("transition")
            assert "all" in transition  # Should have transition effects


if __name__ == "__main__":
    pytest.main([__file__]) 