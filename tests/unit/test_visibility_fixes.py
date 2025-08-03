import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


class TestPromptCardVisibility:
    """Test class for verifying prompt card title visibility in both themes"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Setup Chrome driver with headless mode"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        yield driver
        driver.quit()
    
    def test_light_theme_title_visibility(self, driver, live_server):
        """Test that prompt card titles are visible in light theme"""
        # Navigate to prompts page
        driver.get(f"{live_server.url}/prompts")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "prompt-card"))
        )
        
        # Check if theme is light (default)
        html_element = driver.find_element(By.TAG_NAME, "html")
        theme = html_element.get_attribute("data-theme")
        assert theme in ["light", None], f"Expected light theme, got: {theme}"
        
        # Find all prompt card titles
        card_titles = driver.find_elements(By.CSS_SELECTOR, ".prompt-card .card-title")
        
        if card_titles:
            for title in card_titles:
                # Check if title is visible
                assert title.is_displayed(), "Card title should be visible"
                
                # Check computed color
                color = title.value_of_css_property("color")
                assert color != "rgba(0, 0, 0, 0)", f"Title color should not be transparent, got: {color}"
                
                # Check if text content is not empty
                text = title.text.strip()
                assert text, f"Title should have text content, got: '{text}'"
                
                print(f"✓ Light theme: Title '{text}' is visible with color {color}")
        else:
            print("No prompt cards found to test")
    
    def test_dark_theme_title_visibility(self, driver, live_server):
        """Test that prompt card titles are visible in dark theme"""
        # Navigate to prompts page
        driver.get(f"{live_server.url}/prompts")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "prompt-card"))
        )
        
        # Switch to dark theme
        theme_toggle = driver.find_element(By.CLASS_NAME, "theme-toggle")
        theme_toggle.click()
        
        # Wait for theme to apply
        time.sleep(1)
        
        # Check if theme is dark
        html_element = driver.find_element(By.TAG_NAME, "html")
        theme = html_element.get_attribute("data-theme")
        assert theme == "dark", f"Expected dark theme, got: {theme}"
        
        # Find all prompt card titles
        card_titles = driver.find_elements(By.CSS_SELECTOR, ".prompt-card .card-title")
        
        if card_titles:
            for title in card_titles:
                # Check if title is visible
                assert title.is_displayed(), "Card title should be visible in dark theme"
                
                # Check computed color
                color = title.value_of_css_property("color")
                assert color != "rgba(0, 0, 0, 0)", f"Title color should not be transparent in dark theme, got: {color}"
                
                # Check if text content is not empty
                text = title.text.strip()
                assert text, f"Title should have text content in dark theme, got: '{text}'"
                
                print(f"✓ Dark theme: Title '{text}' is visible with color {color}")
        else:
            print("No prompt cards found to test")
    
    def test_theme_switch_preserves_visibility(self, driver, live_server):
        """Test that switching themes preserves title visibility"""
        # Navigate to prompts page
        driver.get(f"{live_server.url}/prompts")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "prompt-card"))
        )
        
        # Get initial titles
        initial_titles = driver.find_elements(By.CSS_SELECTOR, ".prompt-card .card-title")
        if not initial_titles:
            print("No prompt cards found to test")
            return
        
        initial_texts = [title.text.strip() for title in initial_titles]
        initial_colors = [title.value_of_css_property("color") for title in initial_titles]
        
        # Switch to dark theme
        theme_toggle = driver.find_element(By.CLASS_NAME, "theme-toggle")
        theme_toggle.click()
        time.sleep(1)
        
        # Check titles after dark theme
        dark_titles = driver.find_elements(By.CSS_SELECTOR, ".prompt-card .card-title")
        dark_texts = [title.text.strip() for title in dark_titles]
        dark_colors = [title.value_of_css_property("color") for title in dark_titles]
        
        # Switch back to light theme
        theme_toggle.click()
        time.sleep(1)
        
        # Check titles after light theme
        light_titles = driver.find_elements(By.CSS_SELECTOR, ".prompt-card .card-title")
        light_texts = [title.text.strip() for title in light_titles]
        light_colors = [title.value_of_css_property("color") for title in light_titles]
        
        # Verify text content is preserved
        assert initial_texts == dark_texts == light_texts, "Title text should be preserved across theme switches"
        
        # Verify colors change but remain visible
        assert initial_colors != dark_colors, "Colors should change between themes"
        assert dark_colors != light_colors, "Colors should change between themes"
        
        # Verify no transparent colors
        for color in initial_colors + dark_colors + light_colors:
            assert color != "rgba(0, 0, 0, 0)", f"Title color should never be transparent, got: {color}"
        
        print("✓ Theme switching preserves title visibility and content")
    
    def test_css_variables_are_used(self, driver, live_server):
        """Test that CSS variables are properly used for title colors"""
        # Navigate to prompts page
        driver.get(f"{live_server.url}/prompts")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "prompt-card"))
        )
        
        # Check light theme
        html_element = driver.find_element(By.TAG_NAME, "html")
        initial_theme = html_element.get_attribute("data-theme")
        
        # Get title color in light theme
        title = driver.find_element(By.CSS_SELECTOR, ".prompt-card .card-title")
        light_color = title.value_of_css_property("color")
        
        # Switch to dark theme
        theme_toggle = driver.find_element(By.CLASS_NAME, "theme-toggle")
        theme_toggle.click()
        time.sleep(1)
        
        # Get title color in dark theme
        dark_color = title.value_of_css_property("color")
        
        # Verify colors are different (indicating CSS variables are working)
        assert light_color != dark_color, "Title colors should be different between themes"
        
        print(f"✓ CSS variables working: Light theme color: {light_color}, Dark theme color: {dark_color}")


class TestOtherVisibilityIssues:
    """Test class for other potential visibility issues"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Setup Chrome driver with headless mode"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        yield driver
        driver.quit()
    
    def test_content_text_visibility(self, driver, live_server):
        """Test that content text is visible in both themes"""
        # Navigate to prompts page
        driver.get(f"{live_server.url}/prompts")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "prompt-card"))
        )
        
        # Test light theme
        content_texts = driver.find_elements(By.CLASS_NAME, "content-text")
        if content_texts:
            for text_elem in content_texts:
                color = text_elem.value_of_css_property("color")
                assert color != "rgba(0, 0, 0, 0)", f"Content text should be visible in light theme, got: {color}"
        
        # Switch to dark theme
        theme_toggle = driver.find_element(By.CLASS_NAME, "theme-toggle")
        theme_toggle.click()
        time.sleep(1)
        
        # Test dark theme
        content_texts = driver.find_elements(By.CLASS_NAME, "content-text")
        if content_texts:
            for text_elem in content_texts:
                color = text_elem.value_of_css_property("color")
                assert color != "rgba(0, 0, 0, 0)", f"Content text should be visible in dark theme, got: {color}"
        
        print("✓ Content text visibility verified in both themes")
    
    def test_search_highlight_visibility(self, driver, live_server):
        """Test that search highlights are visible in both themes"""
        # Navigate to search page with a query
        driver.get(f"{live_server.url}/prompts/search?q=test")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check for search highlights
        highlights = driver.find_elements(By.CLASS_NAME, "search-highlight")
        if highlights:
            for highlight in highlights:
                # Test light theme
                bg_color = highlight.value_of_css_property("background-color")
                text_color = highlight.value_of_css_property("color")
                assert bg_color != "rgba(0, 0, 0, 0)", f"Highlight background should be visible, got: {bg_color}"
                assert text_color != "rgba(0, 0, 0, 0)", f"Highlight text should be visible, got: {text_color}"
            
            # Switch to dark theme
            theme_toggle = driver.find_element(By.CLASS_NAME, "theme-toggle")
            theme_toggle.click()
            time.sleep(1)
            
            # Test dark theme
            highlights = driver.find_elements(By.CLASS_NAME, "search-highlight")
            for highlight in highlights:
                bg_color = highlight.value_of_css_property("background-color")
                text_color = highlight.value_of_css_property("color")
                assert bg_color != "rgba(0, 0, 0, 0)", f"Highlight background should be visible in dark theme, got: {bg_color}"
                assert text_color != "rgba(0, 0, 0, 0)", f"Highlight text should be visible in dark theme, got: {text_color}"
        
        print("✓ Search highlight visibility verified in both themes") 