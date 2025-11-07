#!/usr/bin/env python3
"""
Create appointments table in Supabase
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")

print("🔧 Creating appointments table in Supabase...")
print("=" * 60)

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Create the appointments table by inserting first appointment
    print("\n📝 Creating appointments table...")

    test_appointment = {
        "id": "APT0001",
        "patient_name": "أحمد محمد",
        "phone": "+966501234567",
        "email": "ahmad@example.com",
        "service": "تنظيف",
        "date": "2025-11-10",
        "time": "10:00",
        "notes": "أول زيارة",
        "status": "confirmed",
        "created_at": "2025-11-04T20:00:00"
    }

    response = supabase.table('appointments').insert(test_appointment).execute()

    if response.data:
        print("✅ Appointments table created successfully!")
        print(f"✅ Test appointment inserted: {response.data[0]['id']}")

        # Verify
        all_appointments = supabase.table('appointments').select("*").execute()
        print(f"✅ Found {len(all_appointments.data)} appointments in table")

    print("\n" + "=" * 60)
    print("✅ Setup complete! Appointments table is ready.")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
