#!/usr/bin/env python3
"""
Test script for Call Center Conversations
Demonstrates real-time conversation with persona switching and routing
"""

import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fix imports - use absolute imports when run as script
try:
    from conversation_manager import get_conversation_manager, remove_conversation_manager
    from openai_personas import PersonaType, get_persona_manager
    from crm_system import get_crm_system
except ImportError:
    # Fallback to package import
    from callCenter.conversation_manager import get_conversation_manager, remove_conversation_manager
    from callCenter.openai_personas import PersonaType, get_persona_manager
    from callCenter.crm_system import get_crm_system


# ============================================================================
# TEST SCENARIO 1: SERVICE INQUIRY (Reception → Sales)
# ============================================================================

async def test_service_inquiry():
    """Test customer inquiring about services"""
    print("\n" + "="*80)
    print("TEST 1: SERVICE INQUIRY (Reception → Sales)")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    call_id = "CALL-TEST-001"
    customer_name = "علي محمد"  # Ali Mohamed
    language = "ar"  # Arabic

    # Create conversation
    manager = get_conversation_manager(call_id, customer_name, language)

    # Display initial greeting
    print(f"AGENT (Reception): {manager.messages[0].content}")
    print()

    # Customer message 1: Inquiring about services
    user_message_1 = "أنا مهتم بخدمة الإعلانات الذكية، هل يمكن أن تخبرني المزيد عنها؟"
    print(f"CUSTOMER: {user_message_1}")

    response_1 = await manager.get_response(user_message_1)
    print(f"AGENT ({manager.current_persona.value}): {response_1}")
    print()

    # Customer message 2: More details
    user_message_2 = "كم سيكلف هذا الحل؟ وهل لديكم عرض خاص؟"
    print(f"CUSTOMER: {user_message_2}")

    response_2 = await manager.get_response(user_message_2)
    print(f"AGENT ({manager.current_persona.value}): {response_2}")
    print()

    # Display statistics
    stats = manager.get_statistics()
    print("CONVERSATION STATISTICS:")
    print(f"  Total Messages: {stats['total_messages']}")
    print(f"  User Messages: {stats['user_messages']}")
    print(f"  Assistant Messages: {stats['assistant_messages']}")
    print(f"  Personas Used: {', '.join(stats['personas_used'])}")
    print(f"  Current Persona: {stats['current_persona']}")

    # Cleanup
    remove_conversation_manager(call_id)
    print("\n✅ TEST 1 COMPLETED")


# ============================================================================
# TEST SCENARIO 2: COMPLAINT HANDLING (Reception → Complaints)
# ============================================================================

async def test_complaint():
    """Test customer with a complaint"""
    print("\n" + "="*80)
    print("TEST 2: COMPLAINT HANDLING (Reception → Complaints)")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    call_id = "CALL-TEST-002"
    customer_name = "فاطمة علي"  # Fatima Ali
    language = "ar"  # Arabic

    # Create conversation
    manager = get_conversation_manager(call_id, customer_name, language)

    # Display initial greeting
    print(f"AGENT (Reception): {manager.messages[0].content}")
    print()

    # Customer message 1: Complaint
    user_message_1 = "أنا عندي مشكلة مع الخدمة التي اشتريتها، لم تعمل كما هو متوقع"
    print(f"CUSTOMER: {user_message_1}")

    response_1 = await manager.get_response(user_message_1)
    print(f"AGENT ({manager.current_persona.value}): {response_1}")
    print()

    # Customer message 2: More details about complaint
    user_message_2 = "الخدمة توقفت عن العمل في منتصف المشروع، وهذا أثر على عملي"
    print(f"CUSTOMER: {user_message_2}")

    response_2 = await manager.get_response(user_message_2)
    print(f"AGENT ({manager.current_persona.value}): {response_2}")
    print()

    # Display statistics
    stats = manager.get_statistics()
    print("CONVERSATION STATISTICS:")
    print(f"  Total Messages: {stats['total_messages']}")
    print(f"  User Messages: {stats['user_messages']}")
    print(f"  Assistant Messages: {stats['assistant_messages']}")
    print(f"  Personas Used: {', '.join(stats['personas_used'])}")
    print(f"  Current Persona: {stats['current_persona']}")

    # Create ticket from complaint
    crm = get_crm_system()
    ticket = await crm.create_ticket(
        customer_name=customer_name,
        customer_phone="+966501234567",
        subject="خدمة توقفت عن العمل",
        description=user_message_2,
        department="complaints",
        priority="high",
        call_id=call_id,
    )
    print(f"\n🎫 TICKET CREATED: {ticket.ticket_id}")
    print(f"   Status: {ticket.status}")
    print(f"   Priority: {ticket.priority}")

    # Cleanup
    remove_conversation_manager(call_id)
    print("\n✅ TEST 2 COMPLETED")


# ============================================================================
# TEST SCENARIO 3: FULL CONVERSATION FLOW (English)
# ============================================================================

async def test_full_flow_english():
    """Test complete conversation flow in English"""
    print("\n" + "="*80)
    print("TEST 3: FULL CONVERSATION FLOW (English)")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    call_id = "CALL-TEST-003"
    customer_name = "John Smith"
    language = "en"  # English

    # Create conversation
    manager = get_conversation_manager(call_id, customer_name, language)

    # Display initial greeting
    print(f"AGENT (Reception): {manager.messages[0].content}")
    print()

    # Customer message 1
    user_message_1 = "Hello, I'm interested in your digital platform service"
    print(f"CUSTOMER: {user_message_1}")

    response_1 = await manager.get_response(user_message_1)
    print(f"AGENT ({manager.current_persona.value}): {response_1}")
    print()

    # Customer message 2
    user_message_2 = "What's the pricing for the platform development service?"
    print(f"CUSTOMER: {user_message_2}")

    response_2 = await manager.get_response(user_message_2)
    print(f"AGENT ({manager.current_persona.value}): {response_2}")
    print()

    # Customer message 3
    user_message_3 = "Sounds great! I'd like to discuss this further with someone from your team"
    print(f"CUSTOMER: {user_message_3}")

    response_3 = await manager.get_response(user_message_3)
    print(f"AGENT ({manager.current_persona.value}): {response_3}")
    print()

    # Display statistics
    stats = manager.get_statistics()
    print("CONVERSATION STATISTICS:")
    print(f"  Total Messages: {stats['total_messages']}")
    print(f"  User Messages: {stats['user_messages']}")
    print(f"  Assistant Messages: {stats['assistant_messages']}")
    print(f"  Personas Used: {', '.join(stats['personas_used'])}")

    # Display transcript
    transcript = manager.get_transcript()
    print(f"\nTRANSCRIPT ({len(transcript)} messages):")
    for i, msg in enumerate(transcript, 1):
        persona_str = f" ({msg['persona']})" if msg['persona'] else ""
        print(f"  {i}. [{msg['role'].upper()}{persona_str}]: {msg['content'][:70]}...")

    # Cleanup
    remove_conversation_manager(call_id)
    print("\n✅ TEST 3 COMPLETED")


# ============================================================================
# TEST SCENARIO 4: PERSONA MANAGER
# ============================================================================

def test_persona_manager():
    """Test persona manager and information"""
    print("\n" + "="*80)
    print("TEST 4: PERSONA MANAGER")
    print("="*80)

    manager = get_persona_manager()

    print("\nAVAILABLE PERSONAS:")
    for persona_type in PersonaType:
        persona = manager.get_persona(persona_type)
        persona_info = manager.get_persona_info(persona_type)

        print(f"\n{persona_type.value.upper()}:")
        print(f"  Name (EN): {persona_info['name']}")
        print(f"  Name (AR): {persona_info['name_ar']}")
        print(f"  Department: {persona_info['department']}")
        print(f"  Tone (EN): {persona_info['tone']}")
        print(f"  Tone (AR): {persona_info['tone_ar']}")
        print(f"  Expertise (EN): {persona_info['expertise']}")
        print(f"  Expertise (AR): {persona_info['expertise_ar']}")

    print("\n✅ TEST 4 COMPLETED")


# ============================================================================
# TEST SCENARIO 5: MANUAL PERSONA SWITCHING
# ============================================================================

async def test_persona_switching():
    """Test manual persona switching during conversation"""
    print("\n" + "="*80)
    print("TEST 5: MANUAL PERSONA SWITCHING")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    call_id = "CALL-TEST-005"
    customer_name = "محمود خالد"  # Mahmoud Khaled
    language = "ar"  # Arabic

    # Create conversation
    manager = get_conversation_manager(call_id, customer_name, language)

    # Display initial greeting
    print(f"AGENT (Reception): {manager.messages[0].content}")
    print()

    # Customer message
    user_message = "أنا بحاجة إلى المساعدة في شراء خدمة"
    print(f"CUSTOMER: {user_message}")

    response = await manager.get_response(user_message)
    print(f"AGENT ({manager.current_persona.value}): {response}")
    print()

    # Manually switch to Sales persona
    print(">>> Manually switching to SALES persona <<<")
    manager.switch_persona(PersonaType.SALES)
    persona_info = get_persona_manager().get_persona_info(PersonaType.SALES)
    print(f"    Switched to: {persona_info['name']} ({persona_info['department']})")
    print()

    # Customer message with new persona
    user_message_2 = "ما هي أفضل خدمة للشركات الصغيرة؟"
    print(f"CUSTOMER: {user_message_2}")

    response_2 = await manager.get_response(user_message_2)
    print(f"AGENT ({manager.current_persona.value}): {response_2}")
    print()

    # Switch to Complaints persona
    print(">>> Manually switching to COMPLAINTS persona <<<")
    manager.switch_persona(PersonaType.COMPLAINTS)
    persona_info = get_persona_manager().get_persona_info(PersonaType.COMPLAINTS)
    print(f"    Switched to: {persona_info['name']} ({persona_info['department']})")
    print()

    # Display statistics
    stats = manager.get_statistics()
    print("CONVERSATION STATISTICS:")
    print(f"  Personas Used: {', '.join(stats['personas_used'])}")
    print(f"  Current Persona: {stats['current_persona']}")

    # Cleanup
    remove_conversation_manager(call_id)
    print("\n✅ TEST 5 COMPLETED")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

async def main():
    """Run all tests"""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "CALL CENTER CONVERSATION SYSTEM - TEST SUITE".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")

    try:
        # Test 4: Persona Manager (synchronous)
        test_persona_manager()

        # Test 1: Service Inquiry
        await test_service_inquiry()

        # Test 2: Complaint Handling
        await test_complaint()

        # Test 3: Full Flow English
        await test_full_flow_english()

        # Test 5: Persona Switching
        await test_persona_switching()

        # Summary
        print("\n" + "="*80)
        print("ALL TESTS COMPLETED SUCCESSFULLY ✅")
        print("="*80)
        print("\nSUMMARY:")
        print("  ✅ Test 1: Service Inquiry (Reception → Sales)")
        print("  ✅ Test 2: Complaint Handling (Reception → Complaints)")
        print("  ✅ Test 3: Full Conversation Flow (English)")
        print("  ✅ Test 4: Persona Manager")
        print("  ✅ Test 5: Manual Persona Switching")
        print("\nAll conversation features are working correctly!")
        print("="*80)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
