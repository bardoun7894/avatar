#!/usr/bin/env python3
"""
Clean up old dental clinic appointments from database
Since we've transitioned from dental clinic to Ornina AI services company
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(supabase_url, supabase_key)

print("🧹 Cleaning up old dental appointments...")
print("=" * 60)

# Get current appointments
try:
    response = supabase.table('appointments').select("*").execute()
    appointments = response.data

    print(f"\n📋 Found {len(appointments)} old dental appointments:")
    for apt in appointments:
        print(f"   • {apt['id']}: {apt['patient_name']} - {apt['service']} ({apt['date']} {apt['time']})")

    # Ask for confirmation
    print("\n⚠️  These are old dental clinic appointments and no longer relevant for Ornina.")
    print("Options:")
    print("1. Delete all old appointments")
    print("2. Keep them for reference (do nothing)")
    print("3. Archive them to a backup file")

    choice = input("\nEnter your choice (1/2/3): ").strip()

    if choice == "1":
        # Delete all
        print("\n🗑️  Deleting all old appointments...")
        response = supabase.table('appointments').delete().neq('id', '').execute()
        print(f"✅ Deleted {len(appointments)} appointments")

    elif choice == "3":
        # Archive to file
        import json
        from datetime import datetime

        backup_file = f"appointments_dental_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(appointments, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Archived {len(appointments)} appointments to {backup_file}")

        # Ask if should delete after backup
        delete_after = input("Delete appointments from database after backup? (y/n): ").strip().lower()
        if delete_after == 'y':
            response = supabase.table('appointments').delete().neq('id', '').execute()
            print(f"✅ Deleted {len(appointments)} appointments from database")
        else:
            print("✅ Kept appointments in database")
    else:
        print("\n✅ Kept appointments in database for reference")

    print("\n" + "=" * 60)
    print("🎯 Next steps for appointments:")
    print("   • In Phase 4, we'll create 'consultations' table for Ornina")
    print("   • Consultations will replace appointments for AI services")
    print("   • See PHASED_IMPLEMENTATION.md for details")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
