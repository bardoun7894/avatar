# 👤 Face Recognition System - InsightFace Guide

## 🎯 Simple Workflow

### 1️⃣ Register a Person (One Time)
```python
from insightface_recognition import face_recognizer

# Capture their face image (from camera/file)
image_bytes = open("person_photo.jpg", "rb").read()

# Register them
success = face_recognizer.register_person(
    image_bytes=image_bytes,
    user_name="أحمد محمد",
    phone="+966501234567",
    email="ahmad@example.com"  # optional
)

if success:
    print("✅ Person registered!")
```

### 2️⃣ Recognize When They Appear
```python
# When camera captures a frame
current_frame_bytes = capture_from_camera()

# Recognize
match = face_recognizer.recognize_person(current_frame_bytes)

if match.matched:
    print(f"✅ Recognized: {match.user_name}")
    print(f"   Phone: {match.phone}")
    print(f"   Confidence: {match.confidence:.0%}")

    # Avatar greets them
    greeting = match.to_message(language="ar")
    # "أهلاً أحمد محمد! أنا أراك وأتعرف عليك. كيف يمكنني مساعدتك اليوم؟"
else:
    print("❌ Unknown person")
    # "لم أتمكن من التعرف على هذا الشخص. هل يمكنك تعريفني بنفسك؟"
```

## 🔧 Installation

```bash
cd /var/www/avatar\ /avatary
source venv/bin/activate

# Install InsightFace (much easier than face-recognition/dlib!)
pip install insightface onnxruntime
```

## 💾 Database

- **Type:** SQLite (local, fast)
- **Location:** `avatary/data/insightface.db`
- **Stores:**
  - Face embeddings (512 floats - InsightFace buffalo_l model)
  - Original images
  - User data (name, phone, email)
  - Timestamps (created, last_seen)

## 📊 Usage Examples

### List All Registered People
```python
people = face_recognizer.get_registered_people()

for person in people:
    print(f"Name: {person['name']}")
    print(f"Phone: {person['phone']}")
    print(f"Email: {person.get('email', 'N/A')}")
    print(f"Last seen: {person['last_seen']}")
    print()
```

### Delete a Person
```python
face_recognizer.delete_person("+966501234567")
```

## 🎥 Integration with Vision System

Already integrated in `agent.py`:

```python
from insightface_recognition import face_recognizer

# After capturing frame
async def handle_visual_update(analysis: str, frame_bytes: bytes = None):
    # Try face recognition if enabled
    recognized_person = None
    if FACE_RECOGNITION_ENABLED and frame_bytes:
        match = face_recognizer.recognize_person(frame_bytes)
        if match.matched:
            recognized_person = match.user_name
            print(f"👤 RECOGNIZED: {match.user_name} (confidence: {match.confidence:.0%})")
            recognition_text = f"\n\n🎯 التعرف على الشخص / Person Identified:\n{match.user_name} ({match.phone})"
            analysis = analysis + recognition_text

    agent.update_visual_context(analysis)
```

## 🔄 Complete Flow

```
User appears on camera
    ↓
Vision captures frame (every 3 seconds)
    ↓
InsightFace detects and recognizes face
    ↓
Match found? → YES
    ↓
Avatar: "أهلاً أحمد! أرى أنك تحمل هاتفك. كيف أساعدك؟"
        (Hello Ahmad! I see you're holding your phone. How can I help?)
```

## ⚙️ Configuration

Adjust recognition threshold in `insightface_recognition.py`:

```python
# Stricter matching (fewer false positives)
recognizer = InsightFaceRecognition(threshold=0.3)

# More lenient (may match more people)
recognizer = InsightFaceRecognition(threshold=0.5)

# Default (balanced, recommended)
recognizer = InsightFaceRecognition(threshold=0.4)
```

**Note:** InsightFace uses cosine similarity internally. The threshold is applied to the distance (1.0 - similarity), so:
- Lower threshold = stricter matching
- Default 0.4 provides good accuracy

## 🧪 Testing

### Register Test Person
```bash
cd avatary
python3

>>> from insightface_recognition import face_recognizer
>>> import requests

# Download a test image
>>> img_url = "https://example.com/person.jpg"
>>> img_bytes = requests.get(img_url).content

# Register
>>> face_recognizer.register_person(
...     image_bytes=img_bytes,
...     user_name="Test Person",
...     phone="+966501111111"
... )
```

### Test Recognition
```python
# Later, with a new photo of the same person
>>> match = face_recognizer.recognize_person(new_image_bytes)
>>> if match.matched:
...     print(f"✅ Recognized {match.user_name}!")
```

## 📝 Tips

1. **Good lighting** - Better recognition with clear face visibility
2. **Front-facing** - Face should be visible, not profile
3. **Clear image** - Not blurry or too far away
4. **One person** - System detects first face found
5. **Update regularly** - Re-register if person's appearance changes significantly

## 🚀 Why InsightFace?

### Advantages over face-recognition (dlib):
- ✅ **Easier installation** - No cmake, no compilation issues
- ✅ **Better accuracy** - State-of-the-art deep learning models
- ✅ **Faster** - Optimized with ONNX Runtime
- ✅ **Modern** - Actively maintained
- ✅ **Flexible** - Multiple models available (buffalo_l, buffalo_s, etc.)
- ✅ **512-dim embeddings** - More accurate than 128-dim

### Model Used:
- **buffalo_l** - High accuracy model
- Face detection + alignment + recognition in one
- Works on CPU (can use CUDA if available)

## 🎯 Production Ready

The system is:
- ✅ Fast (SQLite local database)
- ✅ Accurate (InsightFace buffalo_l model)
- ✅ Private (all data stored locally)
- ✅ Simple (register once, recognize always)
- ✅ Pydantic validated (type-safe models)
- ✅ Easy to install (no build dependencies)

## 🚀 Next Steps

1. ✅ Install InsightFace library
2. Register your first person
3. Test recognition
4. Avatar automatically recognizes and greets by name!

---

**Created:** November 7, 2025
**Updated:** November 7, 2025 (Switched to InsightFace)
**Status:** Ready for production use
