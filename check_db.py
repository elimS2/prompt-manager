#!/usr/bin/env python3
"""
Check database tables and content.
"""
import sqlite3
import os

db_path = "prompt_manager.db"

if os.path.exists(db_path):
    print(f"✅ Database file exists: {db_path}")
    print(f"   Size: {os.path.getsize(db_path)} bytes")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\n📊 Tables in database:")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"   - {table_name}: {count} records")
    
    conn.close()
else:
    print(f"❌ Database file not found: {db_path}")