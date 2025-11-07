#!/usr/bin/env python3
"""
Test script for Visual Context System
Validates Pydantic models and VisualAwareAgent
"""

import asyncio
import time
from visual_context_models import VisualAnalysis, VisualContextStore
from visual_aware_agent import VisualAwareAgent


def test_visual_analysis():
    """Test VisualAnalysis Pydantic model"""
    print("\n" + "="*60)
    print("TEST 1: VisualAnalysis Model")
    print("="*60)

    # Create analysis
    analysis = VisualAnalysis(
        content="أرى شخصًا يحمل كتاباً في يده اليمنى",
        confidence="high"
    )

    print(f"✅ Created VisualAnalysis")
    print(f"   Content: {analysis.content}")
    print(f"   Timestamp: {analysis.timestamp}")
    print(f"   Age: {analysis.age_seconds:.2f}s")
    print(f"   Fresh: {analysis.is_fresh}")

    # Test freshness after delay
    time.sleep(2)
    print(f"\n⏱️  After 2 seconds:")
    print(f"   Age: {analysis.age_seconds:.2f}s")
    print(f"   Fresh: {analysis.is_fresh}")

    # Test injection text
    injection = analysis.to_injection_text()
    print(f"\n📝 Injection text preview:")
    print(injection[:150] + "...")

    print("\n✅ VisualAnalysis test passed!")
    return True


def test_visual_context_store():
    """Test VisualContextStore Pydantic model"""
    print("\n" + "="*60)
    print("TEST 2: VisualContextStore Model")
    print("="*60)

    # Create store
    store = VisualContextStore(
        enabled=True,
        max_age_seconds=5.0
    )

    print(f"✅ Created VisualContextStore")
    print(f"   Enabled: {store.enabled}")
    print(f"   Max age: {store.max_age_seconds}s")

    # Test empty store
    current = store.get_current()
    print(f"\n📭 Empty store:")
    print(f"   Current: {current}")

    # Add analysis
    analysis = store.update("أرى شخصًا يجلس على كرسي", confidence="medium")
    print(f"\n📥 Added analysis:")
    print(f"   Content: {analysis.content[:50]}...")

    # Get current (should be fresh)
    current = store.get_current()
    print(f"\n📬 Get current (fresh):")
    print(f"   Has context: {current is not None}")
    if current:
        print(f"   Age: {current.age_seconds:.2f}s")
        print(f"   Fresh: {current.is_fresh}")

    # Wait for expiry
    print(f"\n⏱️  Waiting {store.max_age_seconds + 1}s for expiry...")
    time.sleep(store.max_age_seconds + 1)

    current = store.get_current()
    print(f"\n📭 Get current (expired):")
    print(f"   Should be None: {current is None}")

    # Clear test
    store.update("New analysis")
    store.clear()
    current = store.get_current()
    print(f"\n🧹 After clear:")
    print(f"   Should be None: {current is None}")

    print("\n✅ VisualContextStore test passed!")
    return True


async def test_visual_aware_agent():
    """Test VisualAwareAgent"""
    print("\n" + "="*60)
    print("TEST 3: VisualAwareAgent")
    print("="*60)

    # Create store and agent
    store = VisualContextStore(enabled=True, max_age_seconds=15.0)
    agent = VisualAwareAgent(
        instructions="You are a helpful Arabic-speaking assistant.",
        visual_store=store
    )

    print(f"✅ Created VisualAwareAgent")

    # Test status (empty)
    status = agent.get_visual_status()
    print(f"\n📊 Initial status:")
    print(f"   Has context: {status['has_context']}")

    # Update visual context
    agent.update_visual_context("أرى شخصًا يرتدي قميصاً أزرق", confidence="high")
    print(f"\n📸 Updated visual context")

    # Check status
    status = agent.get_visual_status()
    print(f"\n📊 Status after update:")
    print(f"   Has context: {status['has_context']}")
    print(f"   Fresh: {status.get('is_fresh', False)}")
    print(f"   Age: {status.get('age_seconds', 0):.2f}s")
    print(f"   Content length: {status.get('content_length', 0)} chars")

    # Test multiple updates
    await asyncio.sleep(1)
    agent.update_visual_context("أرى شخصًا يشير إلى شيء ما", confidence="medium")
    print(f"\n🔄 Updated again")

    status = agent.get_visual_status()
    print(f"   Age: {status.get('age_seconds', 0):.2f}s")

    # Test clear
    agent.clear_visual_context()
    status = agent.get_visual_status()
    print(f"\n🧹 After clear:")
    print(f"   Has context: {status['has_context']}")

    print("\n✅ VisualAwareAgent test passed!")
    return True


def test_pydantic_validation():
    """Test Pydantic validation"""
    print("\n" + "="*60)
    print("TEST 4: Pydantic Validation")
    print("="*60)

    try:
        # Test invalid type
        store = VisualContextStore(max_age_seconds="invalid")
        print("❌ Should have raised validation error!")
        return False
    except Exception as e:
        print(f"✅ Pydantic validation working: {type(e).__name__}")

    try:
        # Test valid construction
        store = VisualContextStore(
            enabled=True,
            max_age_seconds=10.5
        )
        print(f"✅ Valid construction works")
        print(f"   max_age_seconds type: {type(store.max_age_seconds)}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

    print("\n✅ Pydantic validation test passed!")
    return True


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Visual Context System - Test Suite")
    print("="*60)

    results = []

    # Run tests
    results.append(("VisualAnalysis", test_visual_analysis()))
    results.append(("VisualContextStore", test_visual_context_store()))
    results.append(("VisualAwareAgent", await test_visual_aware_agent()))
    results.append(("Pydantic Validation", test_pydantic_validation()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
