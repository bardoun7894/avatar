#!/usr/bin/env python3
"""
Quick diagnostic to test vision system imports and initialization
"""

import sys
sys.path.insert(0, '.')

print("Testing vision system components...\n")

# Test 1: Import modules
print("1. Testing imports...")
try:
    from visual_aware_agent import VisualAwareAgent
    print("   ✅ VisualAwareAgent imported")
except Exception as e:
    print(f"   ❌ VisualAwareAgent import failed: {e}")
    sys.exit(1)

try:
    from visual_context_models import VisualContextStore, VisualAnalysis
    print("   ✅ VisualContextStore imported")
    print("   ✅ VisualAnalysis imported")
except Exception as e:
    print(f"   ❌ Visual context models import failed: {e}")
    sys.exit(1)

try:
    from vision_processor import VisionProcessor
    print("   ✅ VisionProcessor imported")
except Exception as e:
    print(f"   ❌ VisionProcessor import failed: {e}")
    sys.exit(1)

# Test 2: Create instances
print("\n2. Testing object creation...")
try:
    store = VisualContextStore()
    print(f"   ✅ VisualContextStore created: {store}")
except Exception as e:
    print(f"   ❌ VisualContextStore creation failed: {e}")
    sys.exit(1)

try:
    agent = VisualAwareAgent(
        instructions="Test instructions",
        visual_store=store
    )
    print(f"   ✅ VisualAwareAgent created")
except Exception as e:
    print(f"   ❌ VisualAwareAgent creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test visual context update
print("\n3. Testing visual context operations...")
try:
    analysis = store.update("Test analysis - أرى شخصًا يجلس")
    print(f"   ✅ Visual context updated")
    print(f"      Content: {analysis.content}")
    print(f"      Fresh: {analysis.is_fresh}")
    print(f"      Age: {analysis.age_seconds:.2f}s")
except Exception as e:
    print(f"   ❌ Visual context update failed: {e}")
    sys.exit(1)

try:
    current = store.get_current()
    print(f"   ✅ Got current visual context: {current.content[:50]}...")
except Exception as e:
    print(f"   ❌ Get current failed: {e}")
    sys.exit(1)

# Test 4: Test agent methods
print("\n4. Testing agent visual methods...")
try:
    status = agent.get_visual_status()
    print(f"   ✅ get_visual_status(): {status}")
except Exception as e:
    print(f"   ❌ get_visual_status failed: {e}")
    sys.exit(1)

print("\n✅ ALL TESTS PASSED! Vision system components are working correctly.")
print("\nNow testing if agent.py imports correctly...")

try:
    import agent
    print("✅ agent.py imports successfully!")
except Exception as e:
    print(f"❌ agent.py import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 Vision system is ready to use!")
print("\nNext steps to debug:")
print("1. Connect to http://localhost:3000")
print("2. Grant camera permissions")
print("3. Check browser console for video track publishing")
print("4. Ask avatar: 'ماذا ترى؟' (What do you see?)")
