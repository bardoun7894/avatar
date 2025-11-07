#!/usr/bin/env python3
"""
Users Manager - Save and manage users in Supabase
"""
import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class UsersManager:
    def __init__(self):
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_ANON_KEY")
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def save_user(self, name: str, phone: str, email: str = None) -> dict:
        """Save or update user in Supabase"""
        try:
            # Check if user exists by phone
            existing = self.supabase.table('users')\
                .select("*")\
                .eq("phone", phone)\
                .execute()

            user_data = {
                "name": name,
                "phone": phone,
                "email": email or "",
                "updated_at": datetime.now().isoformat()
            }

            if existing.data and len(existing.data) > 0:
                # Update existing user
                user_data_update = {
                    **user_data,
                    "last_interaction": datetime.now().isoformat()
                }
                response = self.supabase.table('users')\
                    .update(user_data_update)\
                    .eq("phone", phone)\
                    .execute()
                print(f"✅ Updated user: {name} ({phone})")
                return response.data[0] if response.data else None
            else:
                # Create new user
                user_data["created_at"] = datetime.now().isoformat()
                user_data["last_interaction"] = datetime.now().isoformat()

                response = self.supabase.table('users').insert(user_data).execute()
                print(f"✅ Created new user: {name} ({phone})")
                return response.data[0] if response.data else None

        except Exception as e:
            print(f"⚠️  Error saving user: {e}")
            return None

    def get_user_by_phone(self, phone: str):
        """Get user by phone number"""
        try:
            response = self.supabase.table('users')\
                .select("*")\
                .eq("phone", phone)\
                .execute()
            return response.data[0] if response.data and len(response.data) > 0 else None
        except Exception as e:
            print(f"⚠️  Error fetching user: {e}")
            return None

# Global instance
users_manager = UsersManager()

if __name__ == "__main__":
    # Test
    print("🧪 Testing users manager...")
    user = users_manager.save_user(
        name="أحمد محمد",
        phone="+966501234567",
        email="ahmad@example.com"
    )
    print(f"✅ User saved: {user}")
