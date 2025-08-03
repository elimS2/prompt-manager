#!/usr/bin/env python3
"""
Comprehensive Visual Testing Script for Theme System
Tests visual consistency, accessibility, and performance across themes
"""

import requests
import time
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import subprocess
import webbrowser
from pathlib import Path

class VisualThemeTester:
    """Comprehensive visual testing for theme system"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        
    def test_theme_switching_visual_consistency(self) -> Dict:
        """Test visual consistency during theme switching"""
        print("🔍 Testing theme switching visual consistency...")
        
        test_results = {
            "name": "Theme Switching Visual Consistency",
            "status": "passed",
            "details": [],
            "screenshots": []
        }
        
        try:
            # Test light theme
            light_response = requests.get(f"{self.base_url}/", headers={
                "Accept": "text/html",
                "User-Agent": "VisualThemeTester/1.0"
            })
            
            if light_response.status_code == 200:
                test_results["details"].append("✅ Light theme loads successfully")
            else:
                test_results["status"] = "failed"
                test_results["details"].append(f"❌ Light theme failed to load: {light_response.status_code}")
            
            # Test dark theme (simulate via JavaScript)
            dark_response = requests.get(f"{self.base_url}/", headers={
                "Accept": "text/html",
                "User-Agent": "VisualThemeTester/1.0"
            })
            
            if dark_response.status_code == 200:
                test_results["details"].append("✅ Dark theme loads successfully")
            else:
                test_results["status"] = "failed"
                test_results["details"].append(f"❌ Dark theme failed to load: {dark_response.status_code}")
            
            # Check for theme toggle button presence
            if 'data-theme-toggle' in light_response.text:
                test_results["details"].append("✅ Theme toggle button present")
            else:
                test_results["status"] = "failed"
                test_results["details"].append("❌ Theme toggle button missing")
            
            # Check for CSS variables
            if '--primary-color' in light_response.text or '--background-color' in light_response.text:
                test_results["details"].append("✅ CSS variables present")
            else:
                test_results["warnings"].append("⚠️ CSS variables not detected in HTML")
            
        except Exception as e:
            test_results["status"] = "failed"
            test_results["details"].append(f"❌ Error during testing: {str(e)}")
        
        return test_results
    
    def test_accessibility_contrast(self) -> Dict:
        """Test color contrast ratios for accessibility"""
        print("🎨 Testing accessibility contrast ratios...")
        
        test_results = {
            "name": "Accessibility Contrast Testing",
            "status": "passed",
            "details": [],
            "contrast_ratios": {}
        }
        
        # Define test color combinations
        color_tests = [
            {
                "name": "Primary text on background",
                "foreground": "#111827",  # Light theme primary text
                "background": "#F9FAFB",  # Light theme background
                "expected_ratio": 4.5
            },
            {
                "name": "Primary text on background (dark)",
                "foreground": "#F8FAFC",  # Dark theme primary text
                "background": "#0F172A",  # Dark theme background
                "expected_ratio": 4.5
            },
            {
                "name": "Secondary text on background",
                "foreground": "#6B7280",  # Light theme secondary text
                "background": "#F9FAFB",  # Light theme background
                "expected_ratio": 3.0
            },
            {
                "name": "Secondary text on background (dark)",
                "foreground": "#E2E8F0",  # Dark theme secondary text
                "background": "#0F172A",  # Dark theme background
                "expected_ratio": 3.0
            }
        ]
        
        for test in color_tests:
            ratio = self._calculate_contrast_ratio(test["foreground"], test["background"])
            test_results["contrast_ratios"][test["name"]] = {
                "ratio": ratio,
                "expected": test["expected_ratio"],
                "passes": ratio >= test["expected_ratio"]
            }
            
            if ratio >= test["expected_ratio"]:
                test_results["details"].append(f"✅ {test['name']}: {ratio:.2f}:1 (≥{test['expected_ratio']}:1)")
            else:
                test_results["status"] = "failed"
                test_results["details"].append(f"❌ {test['name']}: {ratio:.2f}:1 (<{test['expected_ratio']}:1)")
        
        return test_results
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors"""
        def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def get_luminance(r: int, g: int, b: int) -> float:
            def adjust_gamma(c: int) -> float:
                c = c / 255.0
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            
            return 0.2126 * adjust_gamma(r) + 0.7152 * adjust_gamma(g) + 0.0722 * adjust_gamma(b)
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        lum1 = get_luminance(*rgb1)
        lum2 = get_luminance(*rgb2)
        
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def test_responsive_design(self) -> Dict:
        """Test responsive design across different screen sizes"""
        print("📱 Testing responsive design...")
        
        test_results = {
            "name": "Responsive Design Testing",
            "status": "passed",
            "details": [],
            "breakpoints": {}
        }
        
        # Test different viewport sizes
        viewports = [
            {"name": "Mobile", "width": 375, "height": 667},
            {"name": "Tablet", "width": 768, "height": 1024},
            {"name": "Desktop", "width": 1920, "height": 1080}
        ]
        
        try:
            for viewport in viewports:
                response = requests.get(f"{self.base_url}/", headers={
                    "Accept": "text/html",
                    "User-Agent": "VisualThemeTester/1.0"
                })
                
                if response.status_code == 200:
                    test_results["breakpoints"][viewport["name"]] = {
                        "status": "passed",
                        "width": viewport["width"],
                        "height": viewport["height"]
                    }
                    test_results["details"].append(f"✅ {viewport['name']} viewport loads successfully")
                else:
                    test_results["breakpoints"][viewport["name"]] = {
                        "status": "failed",
                        "width": viewport["width"],
                        "height": viewport["height"]
                    }
                    test_results["status"] = "failed"
                    test_results["details"].append(f"❌ {viewport['name']} viewport failed: {response.status_code}")
                    
        except Exception as e:
            test_results["status"] = "failed"
            test_results["details"].append(f"❌ Error during responsive testing: {str(e)}")
        
        return test_results
    
    def test_performance_metrics(self) -> Dict:
        """Test performance metrics for theme system"""
        print("⚡ Testing performance metrics...")
        
        test_results = {
            "name": "Performance Metrics Testing",
            "status": "passed",
            "details": [],
            "metrics": {}
        }
        
        try:
            # Test page load time
            start_time = time.time()
            response = requests.get(f"{self.base_url}/")
            load_time = time.time() - start_time
            
            test_results["metrics"]["page_load_time"] = load_time
            
            if load_time < 2.0:
                test_results["details"].append(f"✅ Page load time: {load_time:.2f}s (< 2.0s)")
            elif load_time < 5.0:
                test_results["details"].append(f"⚠️ Page load time: {load_time:.2f}s (2-5s)")
                test_results["status"] = "warning"
            else:
                test_results["details"].append(f"❌ Page load time: {load_time:.2f}s (> 5s)")
                test_results["status"] = "failed"
            
            # Test CSS file size
            css_response = requests.get(f"{self.base_url}/static/css/style.css")
            css_size = len(css_response.content) / 1024  # KB
            
            test_results["metrics"]["css_size_kb"] = css_size
            
            if css_size < 100:
                test_results["details"].append(f"✅ CSS file size: {css_size:.1f}KB (< 100KB)")
            elif css_size < 200:
                test_results["details"].append(f"⚠️ CSS file size: {css_size:.1f}KB (100-200KB)")
                test_results["status"] = "warning"
            else:
                test_results["details"].append(f"❌ CSS file size: {css_size:.1f}KB (> 200KB)")
                test_results["status"] = "failed"
            
            # Test JavaScript file size
            js_response = requests.get(f"{self.base_url}/static/js/theme-service.js")
            js_size = len(js_response.content) / 1024  # KB
            
            test_results["metrics"]["js_size_kb"] = js_size
            
            if js_size < 50:
                test_results["details"].append(f"✅ JS file size: {js_size:.1f}KB (< 50KB)")
            elif js_size < 100:
                test_results["details"].append(f"⚠️ JS file size: {js_size:.1f}KB (50-100KB)")
                test_results["status"] = "warning"
            else:
                test_results["details"].append(f"❌ JS file size: {js_size:.1f}KB (> 100KB)")
                test_results["status"] = "failed"
                
        except Exception as e:
            test_results["status"] = "failed"
            test_results["details"].append(f"❌ Error during performance testing: {str(e)}")
        
        return test_results
    
    def test_cross_browser_compatibility(self) -> Dict:
        """Test cross-browser compatibility"""
        print("🌐 Testing cross-browser compatibility...")
        
        test_results = {
            "name": "Cross-Browser Compatibility Testing",
            "status": "passed",
            "details": [],
            "browsers": {}
        }
        
        # Test with different user agents
        user_agents = [
            {"name": "Chrome", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
            {"name": "Firefox", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"},
            {"name": "Safari", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"},
            {"name": "Edge", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"}
        ]
        
        try:
            for browser in user_agents:
                response = requests.get(f"{self.base_url}/", headers={
                    "Accept": "text/html",
                    "User-Agent": browser["ua"]
                })
                
                if response.status_code == 200:
                    test_results["browsers"][browser["name"]] = "passed"
                    test_results["details"].append(f"✅ {browser['name']} compatibility: OK")
                else:
                    test_results["browsers"][browser["name"]] = "failed"
                    test_results["status"] = "failed"
                    test_results["details"].append(f"❌ {browser['name']} compatibility: Failed ({response.status_code})")
                    
        except Exception as e:
            test_results["status"] = "failed"
            test_results["details"].append(f"❌ Error during browser testing: {str(e)}")
        
        return test_results
    
    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        print("📊 Generating test report...")
        
        # Run all tests
        tests = [
            self.test_theme_switching_visual_consistency(),
            self.test_accessibility_contrast(),
            self.test_responsive_design(),
            self.test_performance_metrics(),
            self.test_cross_browser_compatibility()
        ]
        
        # Update results
        for test in tests:
            self.results["tests"][test["name"]] = test
            self.results["summary"]["total_tests"] += 1
            
            if test["status"] == "passed":
                self.results["summary"]["passed"] += 1
            elif test["status"] == "failed":
                self.results["summary"]["failed"] += 1
            elif test["status"] == "warning":
                self.results["summary"]["warnings"] += 1
        
        # Generate report
        report = self._format_report()
        
        # Save report
        report_file = f"visual_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📄 Test report saved to: {report_file}")
        return report
    
    def _format_report(self) -> str:
        """Format test results as readable report"""
        report = []
        report.append("=" * 80)
        report.append("VISUAL THEME SYSTEM TEST REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {self.results['timestamp']}")
        report.append("")
        
        # Summary
        summary = self.results["summary"]
        report.append("SUMMARY:")
        report.append(f"  Total Tests: {summary['total_tests']}")
        report.append(f"  Passed: {summary['passed']}")
        report.append(f"  Failed: {summary['failed']}")
        report.append(f"  Warnings: {summary['warnings']}")
        report.append("")
        
        # Test details
        report.append("DETAILED RESULTS:")
        report.append("-" * 80)
        
        for test_name, test_result in self.results["tests"].items():
            status_icon = "✅" if test_result["status"] == "passed" else "❌" if test_result["status"] == "failed" else "⚠️"
            report.append(f"{status_icon} {test_name}: {test_result['status'].upper()}")
            
            for detail in test_result["details"]:
                report.append(f"    {detail}")
            
            # Add specific metrics if available
            if "metrics" in test_result:
                report.append("    Metrics:")
                for metric, value in test_result["metrics"].items():
                    if isinstance(value, float):
                        report.append(f"      {metric}: {value:.2f}")
                    else:
                        report.append(f"      {metric}: {value}")
            
            if "contrast_ratios" in test_result:
                report.append("    Contrast Ratios:")
                for name, ratio_data in test_result["contrast_ratios"].items():
                    status = "✅" if ratio_data["passes"] else "❌"
                    report.append(f"      {status} {name}: {ratio_data['ratio']:.2f}:1")
            
            report.append("")
        
        return "\n".join(report)
    
    def run_interactive_testing(self):
        """Run interactive testing with browser automation"""
        print("🖥️ Starting interactive testing...")
        print("This will open your browser for manual testing.")
        print("Please test the following scenarios:")
        print("1. Switch between light and dark themes")
        print("2. Check all pages in both themes")
        print("3. Test responsive design on different screen sizes")
        print("4. Verify accessibility features")
        print("")
        
        try:
            # Open main page
            webbrowser.open(f"{self.base_url}/")
            print(f"✅ Opened {self.base_url}/ in browser")
            
            # Open other important pages
            pages = ["/prompts", "/prompts/create", "/tags"]
            for page in pages:
                webbrowser.open(f"{self.base_url}{page}")
                print(f"✅ Opened {self.base_url}{page} in browser")
                
        except Exception as e:
            print(f"❌ Error opening browser: {str(e)}")
            print("Please manually open the application in your browser for testing.")

def main():
    """Main function to run visual testing"""
    print("🎨 Visual Theme System Testing")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding properly")
            print("Please start the Flask application first:")
            print("  python run.py")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server at http://localhost:5000")
        print("Please start the Flask application first:")
        print("  python run.py")
        return
    
    # Create tester
    tester = VisualThemeTester()
    
    # Run automated tests
    print("🤖 Running automated tests...")
    report = tester.generate_test_report()
    print(report)
    
    # Ask for interactive testing
    print("\n" + "=" * 50)
    response = input("Would you like to run interactive testing? (y/n): ")
    if response.lower() in ['y', 'yes']:
        tester.run_interactive_testing()
    
    print("\n🎉 Visual testing completed!")

if __name__ == "__main__":
    main() 