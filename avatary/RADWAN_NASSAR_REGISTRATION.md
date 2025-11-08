# Radwan Nassar Face Recognition Registration Guide

## Status
✅ **Image Added**: `redouan_nassar.jpg` already present in `/var/www/avatar /public/images/ministers/`
✅ **Greeting Added**: Greeting for Radwan Nassar added to `agent.py`

## Next Steps: Register the Face

The face recognition system needs to process the image and create an embedding. Follow these steps:

### Option 1: Automatic Registration (Recommended)

Run the automated registration script:

```bash
cd "/var/www/avatar /avatary"
python3 register_ministers.py
```

This script will:
1. Scan the `/var/www/avatar /public/images/ministers/` directory
2. Extract the name from the filename (`redouan_nassar.jpg` → `Redouan Nassar`)
3. Extract face embeddings using InsightFace
4. Store the embeddings in the face database
5. Display confirmation of successful registration

### Option 2: Manual Registration

If you need more control over the registration, use Python directly:

```python
from insightface_recognition import face_recognizer

# Read the image
with open('/var/www/avatar /public/images/ministers/redouan_nassar.jpg', 'rb') as f:
    image_bytes = f.read()

# Register the person
success = face_recognizer.register_person(
    image_bytes=image_bytes,
    user_name="Radwan Nassar",  # Will match the greeting in agent.py
    phone="+966501234567",      # Update with actual phone if available
    email="radwan@ornina.com"    # Optional
)

if success:
    print("✅ Radwan Nassar successfully registered!")
else:
    print("❌ Registration failed")
```

## How the System Works

1. **Face Detection**: InsightFace detects faces in the image
2. **Embedding Creation**: Converts the face into a numerical vector (embedding)
3. **Database Storage**: Stores the embedding in SQLite database (`avatary/data/insightface.db`)
4. **Recognition**: When a person appears on camera:
   - Extracts their face embedding
   - Compares against registered embeddings
   - If match found (high similarity), plays the personalized greeting

## Greeting Configuration

The greeting for Radwan Nassar is defined in `agent.py`:

```python
elif "Radwan Nassar" in match.user_name or "رضوان نصار" in match.user_name:
    greeting = "مرحباً السيد رضوان نصار، أهلاً وسهلاً بك في شركة أورنينا للذكاء الاصطناعي. تشرفنا بوجودك."
```

**English Translation**:
"Hello Mr. Radwan Nassar, welcome to Ornina AI company. We are honored by your presence."

## Important Notes

⚠️ **Greeting Behavior**:
- The greeting will be spoken **ONLY on the first appearance**
- After the initial greeting, the avatar will speak normally in conversation
- This prevents repetitive greetings during the same session

🔄 **Re-registration**:
- If you need to update Radwan Nassar's face (e.g., new photo):
  1. Replace `redouan_nassar.jpg` with the new image
  2. Re-run `python3 register_ministers.py`
  3. The system will update the embedding automatically

📊 **Verify Registration**:
```bash
cd "/var/www/avatar /avatary"
python3 register_ministers.py  # Lists all registered people at the end
```

## Troubleshooting

**Issue**: Image not detected / No face found
- **Solution**: Ensure the image is clear with a visible face, good lighting, and appropriate size (200x200px minimum)

**Issue**: Recognition not working
- **Solution**: Re-register using `python3 register_ministers.py`

**Issue**: Wrong greeting being used
- **Solution**: Check that name in filename matches greeting condition in `agent.py`
  - Filename: `redouan_nassar.jpg` → recognized as `Redouan Nassar`
  - Greeting checks: `"Radwan Nassar" in match.user_name or "رضوان نصار" in match.user_name`
  - Note: Both "Radwan" and "رضوان" variations are checked

## File Locations

- **Image**: `/var/www/avatar /public/images/ministers/redouan_nassar.jpg`
- **Database**: `/var/www/avatar /avatary/avatary/data/insightface.db`
- **Registration Script**: `/var/www/avatar /avatary/register_ministers.py`
- **Agent Code**: `/var/www/avatar /avatary/agent.py` (lines 486-487)
- **Face Recognition**: `/var/www/avatar /avatary/insightface_recognition.py`

## Technical Details

### Face Embedding
- **Method**: InsightFace (ArcFace model)
- **Vector Size**: 512-dimensional embedding
- **Similarity Metric**: Cosine distance
- **Match Threshold**: Typically 0.4-0.5 distance (system configurable)

### Database Schema
```sql
CREATE TABLE faces (
    id INTEGER PRIMARY KEY,
    user_name TEXT,           -- "Radwan Nassar"
    phone TEXT UNIQUE,        -- Unique identifier
    email TEXT,              -- Optional
    embedding BLOB,          -- Face embedding (512D vector)
    image BLOB,             -- Original image
    created_at TIMESTAMP,    -- Registration date
    last_seen TIMESTAMP      -- Last recognition time
)
```
