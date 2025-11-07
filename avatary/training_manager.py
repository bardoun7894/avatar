#!/usr/bin/env python3
"""
Training Manager - Handle training program registrations for Ornina
Manages student sign-ups for AI training courses
"""
import os
from datetime import datetime
from typing import Dict, List
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Available training programs
TRAINING_PROGRAMS = {
    "التسويق الرقمي بالذكاء الاصطناعي": {
        "duration_hours": 45,
        "topics": "Prompt Engineering، صناعة المحتوى، إدارة السوشيال ميديا، SEO، Chatbots",
        "output": "بناء حملة تسويقية كاملة"
    },
    "إنتاج الأفلام بالذكاء الاصطناعي": {
        "duration_hours": 30,
        "topics": "كتابة السيناريو، تصميم الشخصيات، توليد المشاهد، الأنيميشن",
        "output": "إنتاج فيلم قصير"
    },
    "تصميم UI/UX بالذكاء الاصطناعي": {
        "duration_hours": 30,
        "topics": "تصميم التجربة، الواجهات، Prototyping، الاختبار",
        "output": "مشروع تصميم احترافي"
    },
    "توليد الأكواد بالذكاء الاصطناعي": {
        "duration_hours": 30,
        "topics": "Prompt Engineering للبرمجة، تطوير المواقع، تطبيقات",
        "output": "تطبيق ويب كامل"
    },
    "تصميم الأزياء بالذكاء الاصطناعي": {
        "duration_hours": 10,
        "topics": "توليد التصاميم، الملابس ثلاثية الأبعاد، عروض الأزياء الرقمية",
        "output": "كولكشن أزياء رقمي كامل"
    },
    "تصميم وبرمجة المواقع بالذكاء الاصطناعي": {
        "duration_hours": 30,
        "topics": "Front-end، Back-end، Responsive Design، النشر",
        "output": "موقع ويب جاهز للإطلاق"
    }
}

class TrainingManager:
    def __init__(self):
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_ANON_KEY")
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def register_interest(
        self,
        student_name: str,
        phone: str,
        program_name: str,
        email: str = None,
        preferred_start_date: str = None,
        experience_level: str = "beginner",
        notes: str = None
    ) -> Dict:
        """Register a student's interest in a training program"""
        try:
            # Validate program name
            if program_name not in TRAINING_PROGRAMS:
                print(f"⚠️  Invalid program name: {program_name}")
                return None

            # Get next registration ID
            response = self.supabase.table('training_registrations')\
                .select("registration_id")\
                .order("registration_id", desc=True)\
                .limit(1)\
                .execute()

            if response.data and len(response.data) > 0:
                last_id = response.data[0]['registration_id']
                num = int(last_id.replace('TRN', '')) + 1
                registration_id = f"TRN{num:04d}"
            else:
                registration_id = "TRN0001"

            registration = {
                "registration_id": registration_id,
                "student_name": student_name,
                "phone": phone,
                "email": email or "",
                "program_name": program_name,
                "preferred_start_date": preferred_start_date or "",
                "experience_level": experience_level,
                "payment_status": "pending",
                "registration_status": "interested",
                "notes": notes or "",
                "created_at": datetime.now().isoformat()
            }

            # Save registration
            response = self.supabase.table('training_registrations').insert(registration).execute()

            if response.data:
                print(f"✅ Training registration saved: {registration_id} - {student_name} for {program_name}")
                return response.data[0]

            return registration

        except Exception as e:
            print(f"⚠️  Error registering training interest: {e}")
            return None

    def get_program_info(self, program_name: str) -> Dict:
        """Get detailed information about a training program"""
        if program_name in TRAINING_PROGRAMS:
            return {
                "program_name": program_name,
                **TRAINING_PROGRAMS[program_name]
            }
        return None

    def list_available_programs(self) -> List[str]:
        """List all available training programs"""
        return list(TRAINING_PROGRAMS.keys())

    def get_registrations_by_phone(self, phone: str) -> List[Dict]:
        """Get all training registrations for a student"""
        try:
            response = self.supabase.table('training_registrations')\
                .select("*")\
                .eq("phone", phone)\
                .order("created_at", desc=True)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️  Error fetching registrations: {e}")
            return []

    def update_registration_status(
        self,
        registration_id: str,
        status: str,
        payment_status: str = None
    ) -> bool:
        """Update registration status"""
        try:
            update_data = {"registration_status": status}
            if payment_status:
                update_data["payment_status"] = payment_status

            response = self.supabase.table('training_registrations')\
                .update(update_data)\
                .eq("registration_id", registration_id)\
                .execute()

            return response.data is not None and len(response.data) > 0
        except Exception as e:
            print(f"⚠️  Error updating registration: {e}")
            return False

    def get_recent_registrations(self, limit: int = 20) -> List[Dict]:
        """Get recent training registrations"""
        try:
            response = self.supabase.table('training_registrations')\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️  Error fetching registrations: {e}")
            return []

# Global instance
training_manager = TrainingManager()

if __name__ == "__main__":
    # Test
    print("🧪 Testing training manager...")

    # List programs
    programs = training_manager.list_available_programs()
    print(f"✅ Available programs: {len(programs)}")
    for p in programs:
        print(f"   • {p}")

    # Get program info
    info = training_manager.get_program_info("التسويق الرقمي بالذكاء الاصطناعي")
    print(f"\n✅ Program info:")
    print(f"   Duration: {info['duration_hours']} hours")
    print(f"   Topics: {info['topics']}")

    # Register student
    registration = training_manager.register_interest(
        student_name="محمد خالد",
        phone="+963993456789",
        email="mohamed@gmail.com",
        program_name="التسويق الرقمي بالذكاء الاصطناعي",
        experience_level="beginner",
        notes="مهتم بالبدء قريباً"
    )

    print(f"\n✅ Registration created: {registration}")
