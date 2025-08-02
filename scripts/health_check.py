#!/usr/bin/env python3
"""
Health check script for monitoring Prompt Manager application.
Can be used with monitoring systems like Nagios, Zabbix, or cron jobs.
"""
import sys
import requests
import argparse
from datetime import datetime


def check_health(url, timeout=5):
    """Check application health status.
    
    Args:
        url: Base URL of the application
        timeout: Request timeout in seconds
        
    Returns:
        tuple: (is_healthy, message, details)
    """
    health_url = f"{url.rstrip('/')}/api/health"
    
    try:
        response = requests.get(health_url, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                return True, "Application is healthy", data
            else:
                return False, f"Application unhealthy: {data.get('status')}", data
        else:
            return False, f"HTTP {response.status_code}", None
            
    except requests.exceptions.Timeout:
        return False, "Request timeout", None
    except requests.exceptions.ConnectionError:
        return False, "Connection failed", None
    except Exception as e:
        return False, f"Error: {str(e)}", None


def check_database(url, timeout=5):
    """Check database connectivity via API.
    
    Args:
        url: Base URL of the application
        timeout: Request timeout in seconds
        
    Returns:
        tuple: (is_healthy, message)
    """
    # Try to fetch prompts - this will fail if DB is down
    api_url = f"{url.rstrip('/')}/api/prompts?per_page=1"
    
    try:
        response = requests.get(api_url, timeout=timeout)
        
        if response.status_code == 200:
            return True, "Database connection OK"
        else:
            return False, f"Database check failed: HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Database check error: {str(e)}"


def main():
    """Main function for health check script."""
    parser = argparse.ArgumentParser(description='Health check for Prompt Manager')
    parser.add_argument('--url', default='http://localhost:5001', 
                        help='Application URL (default: http://localhost:5001)')
    parser.add_argument('--timeout', type=int, default=5,
                        help='Request timeout in seconds (default: 5)')
    parser.add_argument('--check-db', action='store_true',
                        help='Also check database connectivity')
    parser.add_argument('--nagios', action='store_true',
                        help='Output in Nagios plugin format')
    
    args = parser.parse_args()
    
    # Check application health
    is_healthy, message, details = check_health(args.url, args.timeout)
    
    # Check database if requested
    db_healthy = True
    db_message = ""
    if args.check_db:
        db_healthy, db_message = check_database(args.url, args.timeout)
    
    # Overall health
    overall_healthy = is_healthy and db_healthy
    
    # Output format
    if args.nagios:
        # Nagios plugin format
        if overall_healthy:
            print(f"OK - {message}")
            if args.check_db:
                print(f"Database: {db_message}")
            sys.exit(0)  # OK
        else:
            print(f"CRITICAL - {message}")
            if args.check_db:
                print(f"Database: {db_message}")
            sys.exit(2)  # CRITICAL
    else:
        # Regular format
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] Health Check Results:")
        print(f"  Application: {'✓' if is_healthy else '✗'} {message}")
        
        if details:
            print(f"  Version: {details.get('version', 'unknown')}")
            print(f"  Service: {details.get('service', 'unknown')}")
        
        if args.check_db:
            print(f"  Database: {'✓' if db_healthy else '✗'} {db_message}")
        
        print(f"  Overall: {'HEALTHY' if overall_healthy else 'UNHEALTHY'}")
        
        sys.exit(0 if overall_healthy else 1)


if __name__ == '__main__':
    main()