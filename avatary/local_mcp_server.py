#!/usr/bin/env python3
"""
PHASE 1.5: MCP Server with Knowledge Base Search
Agent can search database for FAQs, products, training, services
"""
from typing import Any, Dict, List
import json
from knowledge_base_manager import kb_manager

# Define search tools
TOOLS = [
    {
        "name": "search_knowledge_base",
        "description": "ابحث في قاعدة المعرفة عن معلومات عن الشركة، الخدمات، المنتجات، التدريبات. استخدم هذه الأداة عندما لا تجد الإجابة في معلوماتك المباشرة. Search the knowledge base for company info, services, products, training when you don't have the answer directly.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "سؤال المستخدم أو الكلمات المفتاحية للبحث - User's question or keywords to search"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_all_products",
        "description": "⚠️ لا تستخدم! الخدمات موجودة في التعليمات. استخدم فقط للتفاصيل الإضافية غير الموجودة. DO NOT USE - Services are already in your instructions. Only use for additional details NOT in instructions (like prices, specific features).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_all_training_programs",
        "description": "⚠️ لا تستخدم! التدريبات موجودة في التعليمات. استخدم فقط للتفاصيل الإضافية غير الموجودة. DO NOT USE - Training programs are already in your instructions. Only use for additional details NOT in instructions (like schedules, registration).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_company_contact",
        "description": "⚠️ لا تستخدم! معلومات الاتصال موجودة في التعليمات. DO NOT USE - Contact info is already in your instructions.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

def get_local_tools():
    """Return available knowledge base search tools"""
    return TOOLS

def call_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute knowledge base search tools"""
    try:
        if tool_name == "search_knowledge_base":
            query = arguments.get("query", "")
            if not query:
                return {"success": False, "error": "Query is required"}

            # Smart search across all knowledge base
            results = kb_manager.smart_search(query)

            if results["total_results"] == 0:
                return {
                    "success": True,
                    "message": "لم أجد نتائج مباشرة في قاعدة المعرفة. No direct results found in knowledge base.",
                    "results": []
                }

            # Format results
            formatted_results = []

            # Add FAQs
            for faq in results["faqs"]:
                formatted_results.append({
                    "type": "FAQ",
                    "question": faq["question"],
                    "answer": faq["answer"]
                })

            # Add products
            for prod in results["products"]:
                formatted_results.append({
                    "type": "منتج/Product",
                    "name": prod["name"],
                    "description": prod["description"],
                    "features": prod.get("features", [])[:3]  # First 3 features
                })

            # Add training
            for train in results["training"]:
                formatted_results.append({
                    "type": "تدريب/Training",
                    "name": train["name"],
                    "duration": f"{train['duration_hours']} ساعة",
                    "objectives": train.get("objectives", "")[:150]  # First 150 chars
                })

            # Add services
            for svc in results["services"]:
                formatted_results.append({
                    "type": "خدمة/Service",
                    "category": svc["category"],
                    "service": svc["service"]
                })

            return {
                "success": True,
                "total_results": results["total_results"],
                "results": formatted_results,
                "message": f"وجدت {results['total_results']} نتيجة. Found {results['total_results']} results."
            }

        elif tool_name == "get_all_products":
            products = kb_manager.get_all_products()

            if not products:
                return {
                    "success": False,
                    "error": "لا توجد منتجات في قاعدة البيانات. No products in database."
                }

            return {
                "success": True,
                "count": len(products),
                "products": [{"name": p["name"], "description": p["description"][:200]} for p in products],
                "message": f"لدينا {len(products)} منتجات/خدمات. We have {len(products)} products/services."
            }

        elif tool_name == "get_all_training_programs":
            trainings = kb_manager.get_all_training_programs()

            if not trainings:
                return {
                    "success": False,
                    "error": "لا توجد تدريبات في قاعدة البيانات. No training programs in database."
                }

            return {
                "success": True,
                "count": len(trainings),
                "programs": [
                    {
                        "name": t["name"],
                        "duration_hours": t["duration_hours"],
                        "objectives": t.get("objectives", "")[:150]
                    } for t in trainings
                ],
                "message": f"لدينا {len(trainings)} برامج تدريبية. We have {len(trainings)} training programs."
            }

        elif tool_name == "get_company_contact":
            contact_info = kb_manager.get_company_info()

            if not contact_info:
                return {
                    "success": False,
                    "error": "لا توجد معلومات اتصال. No contact info available."
                }

            # Organize by category
            contact = {}
            about = {}
            for info in contact_info:
                if info["category"] == "contact":
                    contact[info["key"]] = info["value"]
                elif info["category"] == "about":
                    about[info["key"]] = info["value"]

            return {
                "success": True,
                "contact": contact,
                "about": about,
                "message": "معلومات الشركة. Company information."
            }

        else:
            return {
                "success": False,
                "error": f"أداة غير معروفة: {tool_name}. Unknown tool: {tool_name}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"خطأ في تنفيذ الأداة: {str(e)}. Tool execution error: {str(e)}"
        }

if __name__ == "__main__":
    print("📋 PHASE 1.5 MCP Server - Knowledge Base Search Active")
    print("=" * 60)
    print(f"Available tools: {len(TOOLS)}")
    for tool in TOOLS:
        print(f"  ✅ {tool['name']}: {tool['description'][:60]}...")
    print("=" * 60)

    # Test searches
    print("\n🧪 Testing search_knowledge_base:")
    result = call_tool("search_knowledge_base", {"query": "أسعار"})
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n🧪 Testing get_all_products:")
    result = call_tool("get_all_products", {})
    print(f"Found {result.get('count', 0)} products")

    print("\n🧪 Testing get_company_contact:")
    result = call_tool("get_company_contact", {})
    print(json.dumps(result, ensure_ascii=False, indent=2))
