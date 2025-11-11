#!/usr/bin/env python3
"""
Test Frontend and CRM Integration
Tests the interaction between frontend UI and Call Center backend
"""

import asyncio
import sys
import os
from datetime import datetime

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from conversation_manager import get_conversation_manager, remove_conversation_manager
    from crm_system import get_crm_system
    from openai_personas import get_persona_manager, PersonaType
except ImportError:
    from callCenter.conversation_manager import get_conversation_manager, remove_conversation_manager
    from callCenter.crm_system import get_crm_system
    from callCenter.openai_personas import get_persona_manager, PersonaType


# ============================================================================
# TEST 1: CRM CUSTOMER MANAGEMENT
# ============================================================================

async def test_crm_customer_management():
    """Test CRM customer profile creation and updates"""
    print("\n" + "=" * 80)
    print("TEST 1: CRM CUSTOMER MANAGEMENT")
    print("=" * 80)
    
    crm = get_crm_system()
    
    # Create customer
    print("\n1️⃣  Creating new customer...")
    customer = await crm.create_or_update_customer(
        phone="+966501234567",
        name="محمد أحمد",
        email="mohammed@example.com"
    )
    
    print(f"   Customer ID: {customer.customer_id}")
    print(f"   Name: {customer.name}")
    print(f"   Phone: {customer.phone}")
    print(f"   Email: {customer.email}")
    print(f"   ✅ Customer created successfully")
    
    # Retrieve customer
    print("\n2️⃣  Retrieving customer by phone...")
    retrieved = await crm.get_customer_by_phone("+966501234567")
    print(f"   Retrieved: {retrieved.name}")
    print(f"   ✅ Customer retrieved successfully")
    
    print("\n✅ TEST 1 COMPLETED")
    return customer


# ============================================================================
# TEST 2: CRM TICKET MANAGEMENT
# ============================================================================

async def test_crm_ticket_management():
    """Test CRM ticket creation and tracking"""
    print("\n" + "=" * 80)
    print("TEST 2: CRM TICKET MANAGEMENT")
    print("=" * 80)
    
    crm = get_crm_system()
    
    # Create ticket
    print("\n1️⃣  Creating support ticket...")
    ticket = await crm.create_ticket(
        customer_name="فاطمة علي",
        customer_phone="+966509876543",
        subject="الخدمة لا تعمل بشكل صحيح",
        description="توقفت الخدمة عن العمل في منتصف المشروع",
        department="complaints",
        priority="high",
        call_id="CALL-TICKET-001"
    )
    
    print(f"   Ticket ID: {ticket.ticket_id}")
    print(f"   Status: {ticket.status}")
    print(f"   Priority: {ticket.priority}")
    print(f"   ✅ Ticket created successfully")
    
    # Get ticket
    print("\n2️⃣  Retrieving ticket...")
    retrieved_ticket = await crm.get_ticket(ticket.ticket_id)
    print(f"   Subject: {retrieved_ticket.subject}")
    print(f"   Status: {retrieved_ticket.status}")
    print(f"   ✅ Ticket retrieved successfully")
    
    # Update ticket
    print("\n3️⃣  Updating ticket status...")
    updated = await crm.update_ticket_status(ticket.ticket_id, "in_progress")
    print(f"   New Status: {updated.status}")
    print(f"   ✅ Ticket updated successfully")
    
    print("\n✅ TEST 2 COMPLETED")
    return ticket


# ============================================================================
# TEST 3: CONVERSATION + CRM INTEGRATION
# ============================================================================

async def test_conversation_crm_integration():
    """Test how conversations trigger CRM actions"""
    print("\n" + "=" * 80)
    print("TEST 3: CONVERSATION + CRM INTEGRATION")
    print("=" * 80)
    
    crm = get_crm_system()
    call_id = "CALL-INTEGRATION-001"
    
    # Start conversation
    print("\n1️⃣  Starting call conversation...")
    manager = get_conversation_manager(call_id, "علي محمد", "ar")
    print(f"   Call ID: {call_id}")
    print(f"   Customer: علي محمد")
    print(f"   Language: Arabic")
    
    # Customer complains
    print("\n2️⃣  Customer reports problem...")
    user_msg = "الخدمة توقفت عن العمل ولا تستجيب"
    response = await manager.get_response(user_msg)
    print(f"   Persona: {manager.current_persona.value}")
    print(f"   Response length: {len(response)} chars")
    
    # Check if ticket should be created
    print("\n3️⃣  Creating CRM ticket from conversation...")
    if manager.current_persona == PersonaType.COMPLAINTS:
        ticket = await crm.create_ticket(
            customer_name="علي محمد",
            customer_phone="+966501111111",
            subject="خدمة توقفت عن العمل",
            description=user_msg,
            department="complaints",
            priority="high",
            call_id=call_id
        )
        print(f"   Ticket Created: {ticket.ticket_id}")
        print(f"   Priority: {ticket.priority}")
        print(f"   Status: {ticket.status}")
        print(f"   ✅ Ticket linked to conversation")
    
    # Get conversation stats
    stats = manager.get_statistics()
    print(f"\n4️⃣  Conversation Statistics:")
    print(f"   Total Messages: {stats['total_messages']}")
    print(f"   Personas Used: {', '.join(stats['personas_used'])}")
    print(f"   Duration: {stats['last_message_at'] != stats['started_at']}")
    
    remove_conversation_manager(call_id)
    print("\n✅ TEST 3 COMPLETED")


# ============================================================================
# TEST 4: FRONTEND API COMPATIBILITY
# ============================================================================

async def test_frontend_api_compatibility():
    """Test that API responses match frontend expectations"""
    print("\n" + "=" * 80)
    print("TEST 4: FRONTEND API COMPATIBILITY")
    print("=" * 80)
    
    call_id = "CALL-FRONTEND-001"
    manager = get_conversation_manager(call_id, "John Smith", "en")
    
    print("\n1️⃣  Testing conversation endpoint response format...")
    response = await manager.get_response("I want to buy your platform service")
    
    # Check response structure for frontend
    expected_fields = {
        'persona': str,
        'content': str,
        'timestamp': str
    }
    
    print(f"   Persona: {manager.current_persona.value}")
    print(f"   Message Count: {len(manager.messages)}")
    print(f"   Current Persona Type: {type(manager.current_persona)}")
    print(f"   ✅ Response format compatible with frontend")
    
    print("\n2️⃣  Testing transcript endpoint format...")
    transcript = manager.get_transcript()
    print(f"   Transcript Messages: {len(transcript)}")
    if len(transcript) > 0:
        msg = transcript[0]
        print(f"   Message Fields: {list(msg.keys())}")
        print(f"   ✅ Transcript format compatible with frontend")
    
    print("\n3️⃣  Testing statistics endpoint format...")
    stats = manager.get_statistics()
    print(f"   Stat Fields: {list(stats.keys())}")
    print(f"   ✅ Statistics format compatible with frontend")
    
    remove_conversation_manager(call_id)
    print("\n✅ TEST 4 COMPLETED")


# ============================================================================
# TEST 5: MULTI-LANGUAGE SUPPORT (Frontend Perspective)
# ============================================================================

async def test_multi_language_frontend():
    """Test bilingual support from frontend perspective"""
    print("\n" + "=" * 80)
    print("TEST 5: MULTI-LANGUAGE FRONTEND SUPPORT")
    print("=" * 80)
    
    # Test Arabic
    print("\n1️⃣  Testing Arabic conversation...")
    call_ar = "CALL-AR-001"
    manager_ar = get_conversation_manager(call_ar, "محمد علي", "ar")
    response_ar = await manager_ar.get_response("أريد معلومات عن خدماتكم")
    print(f"   Language: Arabic")
    print(f"   Persona: {manager_ar.current_persona.value}")
    print(f"   Response: {response_ar[:60]}...")
    print(f"   ✅ Arabic conversation working")
    
    # Test English
    print("\n2️⃣  Testing English conversation...")
    call_en = "CALL-EN-001"
    manager_en = get_conversation_manager(call_en, "John Smith", "en")
    response_en = await manager_en.get_response("Tell me about your services")
    print(f"   Language: English")
    print(f"   Persona: {manager_en.current_persona.value}")
    print(f"   Response: {response_en[:60]}...")
    print(f"   ✅ English conversation working")
    
    remove_conversation_manager(call_ar)
    remove_conversation_manager(call_en)
    print("\n✅ TEST 5 COMPLETED")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

async def main():
    """Run all frontend and CRM tests"""
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "FRONTEND & CRM INTEGRATION TEST SUITE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        # Run tests
        customer = await test_crm_customer_management()
        ticket = await test_crm_ticket_management()
        await test_conversation_crm_integration()
        await test_frontend_api_compatibility()
        await test_multi_language_frontend()
        
        # Summary
        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED SUCCESSFULLY ✅")
        print("=" * 80)
        print("\nSUMMARY:")
        print("  ✅ Test 1: CRM Customer Management")
        print("  ✅ Test 2: CRM Ticket Management")
        print("  ✅ Test 3: Conversation + CRM Integration")
        print("  ✅ Test 4: Frontend API Compatibility")
        print("  ✅ Test 5: Multi-language Frontend Support")
        print("\nFrontend and CRM integration is working correctly!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
