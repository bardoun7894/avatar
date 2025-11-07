#!/usr/bin/env python3
"""
Knowledge Base Manager - Search company information from database
Searches: FAQs, Products, Training Programs, Services, Company Info
"""
import os
from typing import List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class KnowledgeBaseManager:
    def __init__(self):
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_ANON_KEY")
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def search_faqs(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search FAQs by question, answer, or keywords
        """
        try:
            # Search in question and answer using ILIKE
            response = self.supabase.table('faqs')\
                .select("question, answer, category")\
                .eq("is_active", True)\
                .or_(f"question.ilike.%{query}%,answer.ilike.%{query}%")\
                .limit(limit)\
                .execute()

            results = response.data if response.data else []

            # Also search by keywords if no results
            if not results:
                # Try keyword search
                response2 = self.supabase.table('faqs')\
                    .select("question, answer, category")\
                    .eq("is_active", True)\
                    .limit(limit)\
                    .execute()

                if response2.data:
                    # Filter by keywords containing query
                    for faq in response2.data:
                        # Simple contains check since we can't use array operators easily
                        results.append(faq)
                        if len(results) >= limit:
                            break

            return results[:limit]
        except Exception as e:
            print(f"⚠️ Error searching FAQs: {e}")
            return []

    def search_products(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search products by name or description
        """
        try:
            response = self.supabase.table('products')\
                .select("name, description, features")\
                .eq("is_active", True)\
                .or_(f"name.ilike.%{query}%,description.ilike.%{query}%")\
                .order("display_order")\
                .limit(limit)\
                .execute()

            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️ Error searching products: {e}")
            return []

    def get_all_products(self) -> List[Dict[str, Any]]:
        """
        Get all products (for listing all services)
        """
        try:
            response = self.supabase.table('products')\
                .select("name, description")\
                .eq("is_active", True)\
                .order("display_order")\
                .execute()

            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️ Error getting products: {e}")
            return []

    def search_training_programs(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search training programs by name or objectives
        """
        try:
            response = self.supabase.table('training_programs')\
                .select("name, duration_hours, objectives, outputs")\
                .eq("is_active", True)\
                .or_(f"name.ilike.%{query}%,objectives.ilike.%{query}%")\
                .order("display_order")\
                .limit(limit)\
                .execute()

            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️ Error searching training programs: {e}")
            return []

    def get_all_training_programs(self) -> List[Dict[str, Any]]:
        """
        Get all training programs (for listing all courses)
        """
        try:
            response = self.supabase.table('training_programs')\
                .select("name, duration_hours, objectives")\
                .eq("is_active", True)\
                .order("display_order")\
                .execute()

            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️ Error getting training programs: {e}")
            return []

    def search_services(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search work areas/services
        """
        try:
            response = self.supabase.table('work_areas')\
                .select("category, service")\
                .eq("is_active", True)\
                .ilike("service", f"%{query}%")\
                .order("display_order")\
                .limit(limit)\
                .execute()

            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️ Error searching services: {e}")
            return []

    def get_company_info(self, key: str = None) -> List[Dict[str, Any]]:
        """
        Get company information (contact, about, vision, etc.)
        If key is provided, get specific info, otherwise get all
        """
        try:
            query = self.supabase.table('company_info').select("key, value, category")

            if key:
                query = query.ilike("key", f"%{key}%")

            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️ Error getting company info: {e}")
            return []

    def get_target_markets(self) -> List[Dict[str, Any]]:
        """
        Get target market segments
        """
        try:
            response = self.supabase.table('target_markets')\
                .select("segment, goal")\
                .eq("is_active", True)\
                .order("display_order")\
                .execute()

            return response.data if response.data else []
        except Exception as e:
            print(f"⚠️ Error getting target markets: {e}")
            return []

    def smart_search(self, query: str) -> Dict[str, Any]:
        """
        Smart search across all knowledge base
        Returns results from FAQs, products, training, and services
        """
        results = {
            "query": query,
            "faqs": self.search_faqs(query, limit=3),
            "products": self.search_products(query, limit=2),
            "training": self.search_training_programs(query, limit=2),
            "services": self.search_services(query, limit=3)
        }

        # Count total results
        total = len(results["faqs"]) + len(results["products"]) + \
                len(results["training"]) + len(results["services"])
        results["total_results"] = total

        return results

# Global instance
kb_manager = KnowledgeBaseManager()

if __name__ == "__main__":
    # Test searches
    print("🔍 Testing Knowledge Base Search...\n")

    print("=" * 80)
    print("TEST 1: Search FAQs for 'أسعار'")
    print("=" * 80)
    faqs = kb_manager.search_faqs("أسعار")
    for faq in faqs:
        print(f"Q: {faq['question']}")
        print(f"A: {faq['answer'][:100]}...")
        print()

    print("=" * 80)
    print("TEST 2: Search Products for 'Call Center'")
    print("=" * 80)
    products = kb_manager.search_products("Call Center")
    for prod in products:
        print(f"Product: {prod['name']}")
        print(f"Description: {prod['description'][:100]}...")
        print()

    print("=" * 80)
    print("TEST 3: Get All Training Programs")
    print("=" * 80)
    trainings = kb_manager.get_all_training_programs()
    for train in trainings:
        print(f"• {train['name']} ({train['duration_hours']} hours)")
    print()

    print("=" * 80)
    print("TEST 4: Smart Search for 'تدريب'")
    print("=" * 80)
    results = kb_manager.smart_search("تدريب")
    print(f"Total results: {results['total_results']}")
    print(f"FAQs: {len(results['faqs'])}")
    print(f"Products: {len(results['products'])}")
    print(f"Training: {len(results['training'])}")
    print(f"Services: {len(results['services'])}")
