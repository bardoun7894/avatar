#!/usr/bin/env python3
"""
Consultation Manager - Handle consultation bookings for Ornina
Manages scheduling of consultation meetings with customers
"""
import os
from datetime import datetime, time
from typing import Dict, List
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class ConsultationManager:
    def __init__(self):
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_ANON_KEY")
        self.supabase: Client = create_client(supabase_url, supabase_key)

        # Business hours: 9 AM - 6 PM
        self.business_hours = {
            "start": time(9, 0),
            "end": time(18, 0)
        }

    def schedule_consultation(
        self,
        customer_name: str,
        phone: str,
        service_type: str,
        consultation_date: str,
        consultation_time: str,
        email: str = None,
        company_name: str = None,
        notes: str = None,
        meeting_type: str = "online"
    ) -> Dict:
        """Schedule a consultation meeting"""
        try:
            # Get next consultation ID
            response = self.supabase.table('consultations')\
                .select("consultation_id")\
                .order("consultation_id", desc=True)\
                .limit(1)\
                .execute()

            if response.data and len(response.data) > 0:
                last_id = response.data[0]['consultation_id']
                num = int(last_id.replace('CON', '')) + 1
                consultation_id = f"CON{num:04d}"
            else:
                consultation_id = "CON0001"

            consultation = {
                "consultation_id": consultation_id,
                "customer_name": customer_name,
                "phone": phone,
                "email": email or "",
                "company_name": company_name or "",
                "service_type": service_type,
                "consultation_date": consultation_date,
                "consultation_time": consultation_time,
                "duration_minutes": 30,
                "meeting_type": meeting_type,
                "notes": notes or "",
                "status": "scheduled",
                "created_at": datetime.now().isoformat()
            }

            # Save consultation
            response = self.supabase.table('consultations').insert(consultation).execute()

            if response.data:
                print(f"✅ Consultation scheduled: {consultation_id} - {customer_name} on {consultation_date} at {consultation_time}")
                return response.data[0]

            return consultation

        except Exception as e:
            print(f"⚠️  Error scheduling consultation: {e}")
            return None

    def get_available_slots(self, date: str) -> List[str]:
        """Get available consultation time slots for a specific date"""
        try:
            # All possible slots (every 30 minutes from 9 AM to 6 PM)
            all_slots = []
            current_time = time(9, 0)
            end_time = time(18, 0)

            while current_time < end_time:
                all_slots.append(current_time.strftime("%H:%M"))
                # Add 30 minutes
                hour = current_time.hour
                minute = current_time.minute + 30
                if minute >= 60:
                    hour += 1
                    minute = 0
                current_time = time(hour, minute)

            # Get booked slots for this date
            response = self.supabase.table('consultations')\
                .select("consultation_time")\
                .eq("consultation_date", date)\
                .neq("status", "cancelled")\
                .execute()

            booked_slots = [cons["consultation_time"] for cons in response.data] if response.data else []

            # Return available slots
            available = [slot for slot in all_slots if slot not in booked_slots]
            return available

        except Exception as e:
            print(f"⚠️  Error getting available slots: {e}")
            return all_slots  # Return all slots if error

    def get_consultations_by_phone(self, phone: str) -> List[Dict]:
        """Get all consultations for a customer"""
        try:
            response = self.supabase.table('consultations')\
                .select("*")\
                .eq("phone", phone)\
                .order("consultation_date", desc=False)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️  Error fetching consultations: {e}")
            return []

    def cancel_consultation(self, consultation_id: str) -> bool:
        """Cancel a consultation"""
        try:
            response = self.supabase.table('consultations')\
                .update({"status": "cancelled"})\
                .eq("consultation_id", consultation_id)\
                .execute()
            return response.data is not None and len(response.data) > 0
        except Exception as e:
            print(f"⚠️  Error cancelling consultation: {e}")
            return False

    def get_upcoming_consultations(self, limit: int = 10) -> List[Dict]:
        """Get upcoming consultations"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            response = self.supabase.table('consultations')\
                .select("*")\
                .gte("consultation_date", today)\
                .eq("status", "scheduled")\
                .order("consultation_date", desc=False)\
                .limit(limit)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️  Error fetching upcoming consultations: {e}")
            return []

# Global instance
consultation_manager = ConsultationManager()

if __name__ == "__main__":
    # Test
    print("🧪 Testing consultation manager...")

    # Test scheduling
    consultation = consultation_manager.schedule_consultation(
        customer_name="فاطمة علي",
        phone="+963992345678",
        email="fatima@company.com",
        company_name="شركة التقنية",
        service_type="Film Production",
        consultation_date="2025-11-15",
        consultation_time="14:00",
        notes="مهتمة بإنتاج فيلم قصير"
    )

    print(f"✅ Consultation created: {consultation}")

    # Test available slots
    available = consultation_manager.get_available_slots("2025-11-15")
    print(f"✅ Available slots on 2025-11-15: {len(available)} slots")
    print(f"   First 5: {available[:5]}")
