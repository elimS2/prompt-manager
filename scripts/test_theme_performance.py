#!/usr/bin/env python3
"""
Theme System Performance Testing Script
Tests the performance impact of the theme system on page load times
"""

import time
import requests
import statistics
from urllib.parse import urljoin
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.config import TestingConfig


class ThemePerformanceTester:
    """Performance tester for theme system"""
    
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.results = {}
        
    def test_page_load_time(self, endpoint, iterations=10):
        """Test page load time for a specific endpoint"""
        times = []
        
        print(f"Testing {endpoint}...")
        
        for i in range(iterations):
            try:
                start_time = time.time()
                response = requests.get(urljoin(self.base_url, endpoint))
                load_time = time.time() - start_time
                
                if response.status_code == 200:
                    times.append(load_time)
                    print(f"  Iteration {i+1}: {load_time:.3f}s")
                else:
                    print(f"  Iteration {i+1}: Failed (Status {response.status_code})")
                    
            except requests.RequestException as e:
                print(f"  Iteration {i+1}: Error - {e}")
                
            # Small delay between requests
            time.sleep(0.1)
        
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0
            
            self.results[endpoint] = {
                'iterations': len(times),
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'std_dev': std_dev,
                'times': times
            }
            
            print(f"  Results: Avg={avg_time:.3f}s, Min={min_time:.3f}s, Max={max_time:.3f}s, StdDev={std_dev:.3f}s")
        else:
            print(f"  No successful measurements for {endpoint}")
            
        return times
    
    def test_theme_switch_performance(self, iterations=5):
        """Test theme switching performance using JavaScript simulation"""
        print("Testing theme switching performance...")
        
        # This would require browser automation for full testing
        # For now, we simulate by testing the theme service script load time
        times = []
        
        for i in range(iterations):
            try:
                start_time = time.time()
                response = requests.get(urljoin(self.base_url, '/'))
                load_time = time.time() - start_time
                
                if response.status_code == 200:
                    # Check if theme service script is present
                    if 'theme-service.js' in response.text:
                        times.append(load_time)
                        print(f"  Iteration {i+1}: {load_time:.3f}s (theme service loaded)")
                    else:
                        print(f"  Iteration {i+1}: {load_time:.3f}s (theme service not found)")
                        
            except requests.RequestException as e:
                print(f"  Iteration {i+1}: Error - {e}")
                
            time.sleep(0.1)
        
        if times:
            avg_time = statistics.mean(times)
            print(f"  Theme service load time: Avg={avg_time:.3f}s")
            
        return times
    
    def test_css_load_performance(self):
        """Test CSS file load performance"""
        print("Testing CSS load performance...")
        
        try:
            start_time = time.time()
            response = requests.get(urljoin(self.base_url, '/static/css/style.css'))
            load_time = time.time() - start_time
            
            if response.status_code == 200:
                file_size = len(response.content)
                print(f"  CSS file size: {file_size:,} bytes")
                print(f"  Load time: {load_time:.3f}s")
                print(f"  Transfer rate: {file_size / load_time / 1024:.1f} KB/s")
                
                return load_time, file_size
            else:
                print(f"  Failed to load CSS (Status {response.status_code})")
                return None, None
                
        except requests.RequestException as e:
            print(f"  Error loading CSS: {e}")
            return None, None
    
    def test_js_load_performance(self):
        """Test JavaScript file load performance"""
        print("Testing JavaScript load performance...")
        
        try:
            start_time = time.time()
            response = requests.get(urljoin(self.base_url, '/static/js/theme-service.js'))
            load_time = time.time() - start_time
            
            if response.status_code == 200:
                file_size = len(response.content)
                print(f"  JS file size: {file_size:,} bytes")
                print(f"  Load time: {load_time:.3f}s")
                print(f"  Transfer rate: {file_size / load_time / 1024:.1f} KB/s")
                
                return load_time, file_size
            else:
                print(f"  Failed to load JS (Status {response.status_code})")
                return None, None
                
        except requests.RequestException as e:
            print(f"  Error loading JS: {e}")
            return None, None
    
    def run_comprehensive_test(self):
        """Run comprehensive performance test suite"""
        print("=== Theme System Performance Test Suite ===")
        print()
        
        # Test main pages
        pages = ['/', '/prompts', '/prompts/create', '/prompts/tags']
        
        for page in pages:
            self.test_page_load_time(page, iterations=5)
            print()
        
        # Test theme switching
        self.test_theme_switch_performance()
        print()
        
        # Test static assets
        self.test_css_load_performance()
        print()
        
        self.test_js_load_performance()
        print()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate performance test report"""
        print("=== Performance Test Report ===")
        print()
        
        # Page load times
        print("Page Load Times:")
        for endpoint, data in self.results.items():
            print(f"  {endpoint}:")
            print(f"    Average: {data['avg_time']:.3f}s")
            print(f"    Range: {data['min_time']:.3f}s - {data['max_time']:.3f}s")
            print(f"    Standard Deviation: {data['std_dev']:.3f}s")
            print()
        
        # Performance thresholds
        print("Performance Thresholds:")
        print("  ✅ Good: < 0.5s")
        print("  ⚠️  Acceptable: 0.5s - 1.0s")
        print("  ❌ Poor: > 1.0s")
        print()
        
        # Recommendations
        print("Recommendations:")
        for endpoint, data in self.results.items():
            if data['avg_time'] < 0.5:
                print(f"  ✅ {endpoint}: Excellent performance")
            elif data['avg_time'] < 1.0:
                print(f"  ⚠️  {endpoint}: Acceptable performance, consider optimization")
            else:
                print(f"  ❌ {endpoint}: Poor performance, requires optimization")
        
        print()
        
        # Save results to file
        with open('theme_performance_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print("Results saved to theme_performance_results.json")


class LocalThemeTester:
    """Local testing using Flask test client"""
    
    def __init__(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        
    def test_local_performance(self):
        """Test performance using local Flask test client"""
        print("=== Local Theme System Performance Test ===")
        print()
        
        # Test main page load
        start_time = time.time()
        response = self.client.get('/')
        load_time = time.time() - start_time
        
        print(f"Main page load time: {load_time:.3f}s")
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            
            # Check for theme components
            theme_components = [
                'theme-bg', 'theme-text', 'theme-toggle', 'theme-service.js',
                'style.css', 'aria-label', 'skip-link'
            ]
            
            print("\nTheme Components Check:")
            for component in theme_components:
                if component in html:
                    print(f"  ✅ {component}: Present")
                else:
                    print(f"  ❌ {component}: Missing")
            
            # Check file sizes
            print("\nStatic Asset Sizes:")
            
            # CSS file
            css_response = self.client.get('/static/css/style.css')
            if css_response.status_code == 200:
                css_size = len(css_response.data)
                print(f"  CSS: {css_size:,} bytes")
            
            # JS file
            js_response = self.client.get('/static/js/theme-service.js')
            if js_response.status_code == 200:
                js_size = len(js_response.data)
                print(f"  JS: {js_size:,} bytes")
            
            total_size = css_size + js_size
            print(f"  Total theme assets: {total_size:,} bytes")
            
            # Performance assessment
            print(f"\nPerformance Assessment:")
            if load_time < 0.1:
                print(f"  ✅ Excellent: {load_time:.3f}s")
            elif load_time < 0.5:
                print(f"  ✅ Good: {load_time:.3f}s")
            elif load_time < 1.0:
                print(f"  ⚠️  Acceptable: {load_time:.3f}s")
            else:
                print(f"  ❌ Poor: {load_time:.3f}s")
                
        else:
            print(f"Failed to load main page (Status {response.status_code})")


def main():
    """Main function to run performance tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Theme System Performance Tester')
    parser.add_argument('--mode', choices=['local', 'remote'], default='local',
                       help='Test mode: local (Flask test client) or remote (HTTP requests)')
    parser.add_argument('--url', default='http://localhost:5000',
                       help='Base URL for remote testing')
    
    args = parser.parse_args()
    
    if args.mode == 'local':
        tester = LocalThemeTester()
        tester.test_local_performance()
    else:
        tester = ThemePerformanceTester(args.url)
        tester.run_comprehensive_test()


if __name__ == '__main__':
    main() 