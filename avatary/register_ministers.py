#!/usr/bin/env python3
"""
Register ministers from public/images/ministers directory
Automatically reads images and registers them in face recognition system
"""

import os
import re
from pathlib import Path
from insightface_recognition import face_recognizer

def clean_filename(filename: str) -> str:
    """
    Extract clean name from filename
    Example: "mohamed_bardouni_1.png" -> "Mohamed Bardouni"
    """
    # Remove extension
    name = Path(filename).stem

    # Remove numbers at the end (like _1, _2, etc)
    name = re.sub(r'_\d+$', '', name)

    # Replace underscores with spaces
    name = name.replace('_', ' ')

    # Capitalize each word
    name = ' '.join(word.capitalize() for word in name.split())

    return name

def register_ministers_from_directory(directory: str = "/var/www/avatar /public/images/ministers"):
    """
    Register all ministers from the images directory
    """
    print(f"📁 Reading images from: {directory}\n")

    if not os.path.exists(directory):
        print(f"❌ Directory not found: {directory}")
        return

    # Get all image files
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
        image_files.extend(Path(directory).glob(ext))

    if not image_files:
        print("❌ No images found in directory")
        return

    print(f"Found {len(image_files)} images\n")

    # Group images by person name
    people = {}
    for img_path in image_files:
        person_name = clean_filename(img_path.name)

        if person_name not in people:
            people[person_name] = []

        people[person_name].append(img_path)

    print(f"Found {len(people)} unique people:\n")
    for name, images in people.items():
        print(f"  - {name}: {len(images)} image(s)")

    print("\n" + "="*60)
    print("Starting registration...")
    print("="*60 + "\n")

    # Register each person (using their first image)
    success_count = 0
    failed_count = 0

    for person_name, images in people.items():
        # Use the first image for registration
        image_path = images[0]

        print(f"\n📸 Registering: {person_name}")
        print(f"   Image: {image_path.name}")

        try:
            # Read image bytes
            with open(image_path, 'rb') as f:
                image_bytes = f.read()

            # Generate phone number from name (simplified for now)
            # You can update this with actual phone numbers later
            phone = f"+966{hash(person_name) % 1000000000:09d}"

            # Register person
            success = face_recognizer.register_person(
                image_bytes=image_bytes,
                user_name=person_name,
                phone=phone,
                email=None
            )

            if success:
                print(f"   ✅ Registered successfully!")
                print(f"   Phone: {phone}")
                success_count += 1

                # If there are multiple images, note them
                if len(images) > 1:
                    print(f"   ℹ️  Person has {len(images)} images total")
                    for img in images[1:]:
                        print(f"      - {img.name}")
            else:
                print(f"   ❌ Registration failed")
                failed_count += 1

        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed_count += 1

    print("\n" + "="*60)
    print("Registration Complete!")
    print("="*60)
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📊 Total: {len(people)}")

    print("\n📋 Registered people:")
    registered = face_recognizer.get_registered_people()
    for person in registered:
        print(f"  - {person['name']} ({person['phone']})")

def list_registered_people():
    """List all currently registered people"""
    print("\n" + "="*60)
    print("Currently Registered People")
    print("="*60 + "\n")

    people = face_recognizer.get_registered_people()

    if not people:
        print("No one registered yet.")
        return

    for i, person in enumerate(people, 1):
        print(f"{i}. {person['name']}")
        print(f"   Phone: {person['phone']}")
        if person.get('email'):
            print(f"   Email: {person['email']}")
        if person.get('last_seen'):
            print(f"   Last seen: {person['last_seen']}")
        print()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎯 Minister Face Recognition Registration")
    print("="*60 + "\n")

    # Register all ministers
    register_ministers_from_directory()

    print("\n" + "="*60)
    print("✅ All done! Ministers are now registered.")
    print("="*60)
    print("\nThe avatar will now recognize them by name when they appear on camera! 🎉")
