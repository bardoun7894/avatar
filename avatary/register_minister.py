#!/usr/bin/env python3
"""
Register a minister in the face recognition system
Usage: python3 register_minister.py
"""

import sys
import os
from pathlib import Path

# Add the avatary directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from insightface_recognition import face_recognizer


def register_minister(image_path: str, name: str, phone: str, email: str = None) -> bool:
    """Register a minister from an image file"""
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            print(f"❌ File not found: {image_path}")
            return False

        # Read image
        print(f"📷 Loading image: {image_path}")
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        print(f"📝 Registering: {name}")
        print(f"   Phone: {phone}")
        if email:
            print(f"   Email: {email}")

        # Register the person
        success = face_recognizer.register_person(
            image_bytes=image_bytes,
            user_name=name,
            phone=phone,
            email=email
        )

        if success:
            print(f"✅ Successfully registered {name}!")
        else:
            print(f"❌ Failed to register {name}")

        return success

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def list_registered_people():
    """List all registered people"""
    print("\n📋 Registered People:")
    print("-" * 50)

    people = face_recognizer.get_registered_people()

    if not people:
        print("No people registered yet")
        return

    for person in people:
        print(f"Name:     {person['name']}")
        print(f"Phone:    {person['phone']}")
        print(f"Email:    {person.get('email', 'N/A')}")
        print(f"Last seen: {person['last_seen']}")
        print("-" * 50)


if __name__ == "__main__":
    # Register Tarik Mardini
    image_path = "../public/images/ministers/tarik_mardini.jpg"

    print("="*50)
    print("🤖 Face Recognition Registration System")
    print("="*50)

    # Register the minister
    success = register_minister(
        image_path=image_path,
        name="طارق مارديني",  # Arabic name
        phone="+966-operations-tarik",  # You can customize this
        email=None  # Add if available
    )

    if success:
        # List all registered people
        list_registered_people()

        print("\n✅ Registration complete!")
        print("\nTo test recognition:")
        print("  1. Run the agent: livekit-agents dev")
        print("  2. When Tarik appears on camera, the avatar will greet him by name!")
    else:
        print("\n❌ Registration failed")
        sys.exit(1)
