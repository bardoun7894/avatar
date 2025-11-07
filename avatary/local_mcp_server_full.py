#!/usr/bin/env python3
"""
Ornina MCP Server - Local Tools for AI Services Company
Provides tools for inquiry management, consultation booking, and training registration
"""
import json
from datetime import datetime
from typing import Any, Dict, List
import os
from pathlib import Path
from dotenv import load_dotenv

# Import managers
from inquiry_manager import inquiry_manager
from consultation_manager import consultation_manager
from training_manager import training_manager
from users_manager import users_manager

# Load environment variables
load_dotenv()

# MCP Tool Definitions for Ornina
TOOLS = [
    {
        "name": "save_inquiry",
        "description": "حفظ استفسار عميل عن خدمات الشركة - Save customer inquiry about company services",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_name": {
                    "type": "string",
                    "description": "اسم العميل الكامل - Full customer name"
                },
                "phone": {
                    "type": "string",
                    "description": "رقم هاتف العميل - Customer's phone number"
                },
                "service_interest": {
                    "type": "string",
                    "description": "الخدمة المهتم بها - Service of interest",
                    "enum": [
                        "AI Call Center",
                        "Film Production",
                        "Smart Advertising",
                        "Animation 2D/3D",
                        "Website Development",
                        "Digital Platform",
                        "General Inquiry"
                    ]
                },
                "email": {
                    "type": "string",
                    "description": "البريد الإلكتروني (اختياري) - Email address (optional)"
                },
                "company_name": {
                    "type": "string",
                    "description": "اسم الشركة للعملاء B2B (اختياري) - Company name for B2B customers (optional)"
                },
                "message": {
                    "type": "string",
                    "description": "رسالة أو سؤال العميل - Customer message or question"
                },
                "budget_range": {
                    "type": "string",
                    "description": "الميزانية التقريبية (اختياري) - Approximate budget (optional)",
                    "enum": ["صغير", "متوسط", "كبير", "غير محدد"]
                },
                "timeline": {
                    "type": "string",
                    "description": "الجدول الزمني المتوقع (اختياري) - Expected timeline (optional)"
                }
            },
            "required": ["customer_name", "phone", "service_interest"]
        }
    },
    {
        "name": "schedule_consultation",
        "description": "حجز موعد استشارة مع فريق المبيعات - Schedule a consultation meeting with sales team",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_name": {
                    "type": "string",
                    "description": "اسم العميل - Customer name"
                },
                "phone": {
                    "type": "string",
                    "description": "رقم الهاتف - Phone number"
                },
                "service_type": {
                    "type": "string",
                    "description": "نوع الخدمة للمناقشة - Service to discuss",
                    "enum": [
                        "AI Call Center",
                        "Film Production",
                        "Smart Advertising",
                        "Animation 2D/3D",
                        "Website Development",
                        "Digital Platform",
                        "Partnership",
                        "General"
                    ]
                },
                "consultation_date": {
                    "type": "string",
                    "description": "تاريخ الاستشارة (YYYY-MM-DD) - Consultation date"
                },
                "consultation_time": {
                    "type": "string",
                    "description": "وقت الاستشارة (HH:MM بصيغة 24 ساعة) - Consultation time (24-hour format)"
                },
                "email": {
                    "type": "string",
                    "description": "البريد الإلكتروني (اختياري) - Email (optional)"
                },
                "company_name": {
                    "type": "string",
                    "description": "اسم الشركة (اختياري) - Company name (optional)"
                },
                "notes": {
                    "type": "string",
                    "description": "ملاحظات إضافية (اختياري) - Additional notes (optional)"
                }
            },
            "required": ["customer_name", "phone", "service_type", "consultation_date", "consultation_time"]
        }
    },
    {
        "name": "check_consultation_slots",
        "description": "التحقق من المواعيد المتاحة للاستشارات - Check available consultation time slots",
        "inputSchema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "التاريخ المطلوب (YYYY-MM-DD) - Desired date"
                }
            },
            "required": ["date"]
        }
    },
    {
        "name": "register_training_interest",
        "description": "تسجيل اهتمام طالب ببرنامج تدريبي - Register student interest in training program",
        "inputSchema": {
            "type": "object",
            "properties": {
                "student_name": {
                    "type": "string",
                    "description": "اسم الطالب - Student name"
                },
                "phone": {
                    "type": "string",
                    "description": "رقم الهاتف - Phone number"
                },
                "program_name": {
                    "type": "string",
                    "description": "اسم البرنامج التدريبي - Training program name",
                    "enum": [
                        "التسويق الرقمي بالذكاء الاصطناعي",
                        "إنتاج الأفلام بالذكاء الاصطناعي",
                        "تصميم UI/UX بالذكاء الاصطناعي",
                        "توليد الأكواد بالذكاء الاصطناعي",
                        "تصميم الأزياء بالذكاء الاصطناعي",
                        "تصميم وبرمجة المواقع بالذكاء الاصطناعي"
                    ]
                },
                "email": {
                    "type": "string",
                    "description": "البريد الإلكتروني (اختياري) - Email (optional)"
                },
                "experience_level": {
                    "type": "string",
                    "description": "مستوى الخبرة - Experience level",
                    "enum": ["beginner", "intermediate", "advanced"]
                },
                "preferred_start_date": {
                    "type": "string",
                    "description": "تاريخ البدء المفضل (اختياري) - Preferred start date (optional)"
                },
                "notes": {
                    "type": "string",
                    "description": "ملاحظات (اختياري) - Notes (optional)"
                }
            },
            "required": ["student_name", "phone", "program_name"]
        }
    },
    {
        "name": "get_training_programs",
        "description": "الحصول على قائمة البرامج التدريبية المتاحة - Get list of available training programs",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_program_details",
        "description": "الحصول على تفاصيل برنامج تدريبي معين - Get details of a specific training program",
        "inputSchema": {
            "type": "object",
            "properties": {
                "program_name": {
                    "type": "string",
                    "description": "اسم البرنامج - Program name"
                }
            },
            "required": ["program_name"]
        }
    }
]

# Tool execution functions
def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool and return results"""

    if tool_name == "save_inquiry":
        try:
            # Save user first
            users_manager.save_user(
                name=arguments["customer_name"],
                phone=arguments["phone"],
                email=arguments.get("email", "")
            )

            # Save inquiry
            inquiry = inquiry_manager.save_inquiry(
                customer_name=arguments["customer_name"],
                phone=arguments["phone"],
                service_interest=arguments["service_interest"],
                email=arguments.get("email"),
                company_name=arguments.get("company_name"),
                message=arguments.get("message"),
                budget_range=arguments.get("budget_range"),
                timeline=arguments.get("timeline"),
                inquiry_type="service"
            )

            if inquiry:
                return {
                    "success": True,
                    "inquiry": inquiry,
                    "message": f"تم حفظ استفسارك بنجاح! سيتواصل معك فريقنا قريباً."
                }
            return {"success": False, "error": "فشل حفظ الاستفسار"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    elif tool_name == "schedule_consultation":
        try:
            # Save user first
            users_manager.save_user(
                name=arguments["customer_name"],
                phone=arguments["phone"],
                email=arguments.get("email", "")
            )

            # Schedule consultation
            consultation = consultation_manager.schedule_consultation(
                customer_name=arguments["customer_name"],
                phone=arguments["phone"],
                service_type=arguments["service_type"],
                consultation_date=arguments["consultation_date"],
                consultation_time=arguments["consultation_time"],
                email=arguments.get("email"),
                company_name=arguments.get("company_name"),
                notes=arguments.get("notes")
            )

            if consultation:
                return {
                    "success": True,
                    "consultation": consultation,
                    "message": f"تم حجز موعد الاستشارة بنجاح! يوم {consultation['consultation_date']} الساعة {consultation['consultation_time']}"
                }
            return {"success": False, "error": "فشل حجز الاستشارة"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    elif tool_name == "check_consultation_slots":
        try:
            date = arguments["date"]
            slots = consultation_manager.get_available_slots(date)
            return {
                "success": True,
                "date": date,
                "available_slots": slots,
                "count": len(slots),
                "message": f"المواعيد المتاحة في {date}: {len(slots)} موعد"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif tool_name == "register_training_interest":
        try:
            # Save user first
            users_manager.save_user(
                name=arguments["student_name"],
                phone=arguments["phone"],
                email=arguments.get("email", "")
            )

            # Register training interest
            registration = training_manager.register_interest(
                student_name=arguments["student_name"],
                phone=arguments["phone"],
                program_name=arguments["program_name"],
                email=arguments.get("email"),
                experience_level=arguments.get("experience_level", "beginner"),
                preferred_start_date=arguments.get("preferred_start_date"),
                notes=arguments.get("notes")
            )

            if registration:
                return {
                    "success": True,
                    "registration": registration,
                    "message": f"تم تسجيل اهتمامك ببرنامج {arguments['program_name']} بنجاح! سنتواصل معك قريباً."
                }
            return {"success": False, "error": "فشل تسجيل الاهتمام"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    elif tool_name == "get_training_programs":
        try:
            programs = training_manager.list_available_programs()
            programs_info = []
            for p in programs:
                info = training_manager.get_program_info(p)
                programs_info.append(info)

            return {
                "success": True,
                "programs": programs_info,
                "count": len(programs_info),
                "message": f"لدينا {len(programs_info)} برامج تدريبية متاحة"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif tool_name == "get_program_details":
        try:
            program_name = arguments["program_name"]
            info = training_manager.get_program_info(program_name)

            if info:
                return {
                    "success": True,
                    "program": info,
                    "message": f"تفاصيل برنامج {program_name}"
                }
            return {"success": False, "error": "البرنامج غير موجود"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    else:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}

# Export for use in agent
def get_local_tools():
    """Get list of available tools"""
    return TOOLS

def call_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call a tool and return result"""
    return execute_tool(tool_name, arguments)

if __name__ == "__main__":
    print("🏢 Ornina MCP Server - AI Services Company Tools")
    print("=" * 60)
    print("\n📋 Available Tools:\n")
    for i, tool in enumerate(TOOLS, 1):
        print(f"{i}. {tool['name']}")
        print(f"   {tool['description']}")
    print("\n" + "=" * 60)

    # Test save inquiry
    print("\n🧪 Testing inquiry saving...")
    result = execute_tool("save_inquiry", {
        "customer_name": "أحمد محمد",
        "phone": "+963991234567",
        "email": "ahmad@example.com",
        "service_interest": "AI Call Center",
        "message": "أريد معرفة المزيد عن Call Center بالذكاء الاصطناعي",
        "budget_range": "متوسط"
    })
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n✅ Ornina MCP Server is ready!")
