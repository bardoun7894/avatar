#!/usr/bin/env python3
"""
Check existing tables in Supabase database
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")

print("🔍 Checking Supabase Database...")
print("=" * 60)
print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "Key: NOT SET")
print("=" * 60)

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Try to query the information_schema to get all tables
    # Since Supabase uses PostgreSQL, we can query metadata

    # First, let's try to list all accessible tables by trying common ones
    common_tables = [
        'appointments', 'agents', 'users', 'messages',
        'conversations', 'patients', 'bookings', 'schedule'
    ]

    print("\n📋 Checking for common tables:\n")
    existing_tables = []

    for table in common_tables:
        try:
            response = supabase.table(table).select("*").limit(1).execute()
            print(f"✅ {table} - EXISTS (found {len(response.data)} rows in sample)")
            existing_tables.append(table)

            # Show column info by looking at first row
            if response.data and len(response.data) > 0:
                columns = list(response.data[0].keys())
                print(f"   Columns: {', '.join(columns)}")
            else:
                # Try to get schema info by doing an empty select
                response2 = supabase.table(table).select("*").limit(0).execute()
                print(f"   Table is empty")

        except Exception as e:
            if "PGRST205" in str(e) or "Could not find the table" in str(e):
                print(f"❌ {table} - NOT FOUND")
            else:
                print(f"⚠️  {table} - ERROR: {e}")

    print("\n" + "=" * 60)
    print(f"\n✅ Found {len(existing_tables)} existing tables:")
    for table in existing_tables:
        print(f"   • {table}")

    # Try to get actual table data for each existing table
    if existing_tables:
        print("\n📊 Table Data Preview:\n")
        for table in existing_tables:
            try:
                response = supabase.table(table).select("*").limit(3).execute()
                print(f"\n{table} ({len(response.data)} rows shown):")
                print("-" * 60)
                if response.data:
                    import json
                    for row in response.data:
                        print(json.dumps(row, indent=2, ensure_ascii=False))
                else:
                    print("  (empty table)")
            except Exception as e:
                print(f"  Error: {e}")

except Exception as e:
    print(f"\n❌ Error connecting to Supabase: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
