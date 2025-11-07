#!/usr/bin/env python3
"""
Inquiry Manager - Handle customer service inquiries for Ornina
Manages customer questions and service requests
"""
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class InquiryManager:
    def __init__(self):
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_ANON_KEY")
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def save_inquiry(
        self,
        customer_name: str,
        phone: str,
        service_interest: str,
        inquiry_type: str = "service",
        email: str = None,
        company_name: str = None,
        message: str = None,
        budget_range: str = None,
        timeline: str = None
    ) -> Dict:
        """Save a customer inquiry to Supabase"""
        try:
            inquiry = {
                "inquiry_id": str(uuid.uuid4()),
                "customer_name": customer_name,
                "phone": phone,
                "email": email or "",
                "company_name": company_name or "",
                "service_interest": service_interest,
                "inquiry_type": inquiry_type,
                "message": message or "",
                "budget_range": budget_range or "",
                "timeline": timeline or "",
                "status": "new",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            # Save inquiry
            response = self.supabase.table('inquiries').insert(inquiry).execute()

            if response.data:
                print(f"✅ Inquiry saved: {customer_name} - {service_interest}")
                return response.data[0]

            return inquiry

        except Exception as e:
            print(f"⚠️  Error saving inquiry: {e}")
            return None

    def get_inquiries_by_phone(self, phone: str) -> List[Dict]:
        """Get all inquiries from a customer"""
        try:
            response = self.supabase.table('inquiries')\
                .select("*")\
                .eq("phone", phone)\
                .order("created_at", desc=True)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️  Error fetching inquiries: {e}")
            return []

    def get_recent_inquiries(self, limit: int = 20) -> List[Dict]:
        """Get recent inquiries"""
        try:
            response = self.supabase.table('inquiries')\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️  Error fetching recent inquiries: {e}")
            return []

    def update_inquiry_status(self, inquiry_id: str, status: str, notes: str = None) -> bool:
        """Update inquiry status"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now().isoformat()
            }
            if notes:
                update_data["notes"] = notes

            response = self.supabase.table('inquiries')\
                .update(update_data)\
                .eq("inquiry_id", inquiry_id)\
                .execute()

            return response.data is not None and len(response.data) > 0
        except Exception as e:
            print(f"⚠️  Error updating inquiry: {e}")
            return False

# Global instance
inquiry_manager = InquiryManager()

if __name__ == "__main__":
    # Test
    print("🧪 Testing inquiry manager...")

    inquiry = inquiry_manager.save_inquiry(
        customer_name="أحمد محمد",
        phone="+963991234567",
        email="ahmad@example.com",
        service_interest="AI Call Center",
        inquiry_type="service",
        message="أريد معرفة المزيد عن خدمة Call Center بالذكاء الاصطناعي",
        budget_range="متوسط",
        timeline="خلال شهرين"
    )

    print(f"✅ Inquiry created: {inquiry}")

    # Test fetching
    inquiries = inquiry_manager.get_inquiries_by_phone("+963991234567")
    print(f"✅ Found {len(inquiries)} inquiries for this customer")
