# 🎤 Arabic Voice Agent - وكيل الصوت العربي

AI voice agent for dental appointment booking with Arabic male voice and local appointment system.

---

## ✅ Features

- **Male Arabic Voice** - Abu Salem (Kuwaiti) from ElevenLabs
- **Arabic Conversation** - Full Arabic speech & text
- **Local Appointments** - No Zapier, saves to JSON
- **5 Booking Tools** - Book, check, view, cancel, confirm

---

## 🚀 Quick Start

### 1. Start the Agent
```bash
cd /var/www/avatar/avatary
source venv/bin/activate
python agent.py dev
```

### 2. Open LiveKit Playground
https://agents-playground.livekit.io/

**Credentials:**
```
URL: wss://tavus-agent-project-i82x78jc.livekit.cloud
API Key: APIJL8zayDiwTwV
API Secret: fYtfW6HKKiaqxAcEhmRR4OTjZcyJbfWov4Bi9ezUvfFA
```

### 3. Talk in Arabic
Say: **"السلام عليكم"**

Then: **"أريد حجز موعد"**

---

## 🎤 Quick Test Phrases

```arabic
السلام عليكم                    # Greeting
أريد حجز موعد                   # Book appointment
ما هي المواعيد المتاحة؟         # Check available times
عرض مواعيدي                     # View my appointments
ما هي الخدمات المتوفرة؟         # Ask about services
```

See **docs/testing.md** for full conversation examples.

---

## 📂 Project Structure

```
avatary/
├── agent.py                     ⭐ MAIN AGENT FILE
├── prompts.py                   📝 Arabic instructions
├── local_mcp_server.py          🔧 Booking system
├── local_mcp_integration.py     🔗 Integration
├── appointments.json            💾 Data storage
├── requirements.txt             📦 Dependencies
├── .env                         ⚙️  Configuration
│
├── docs/                        📚 DOCUMENTATION
│   ├── testing.md              🧪 Test guide
│   └── arabic.md               🇸🇦 Arabic reference
│
└── Utilities:
    ├── close_conversations.py  🧹 Cleanup
    └── agent_old_backup.py     💾 Old version (backup)
```

---

## 🔧 Configuration

### Change Voice
Edit `.env`:
```bash
# Abu Salem (Kuwaiti) - Current
ELEVENLABS_VOICE_ID=G1QUjBCuRBbLbAmYlTgl

# Anas (Modern Standard Arabic)
ELEVENLABS_VOICE_ID=R6nda3uM038xEEKi7GFl
```

### Add Video Avatar (Optional)
Edit `.env`:
```bash
AVATAR_PROVIDER=tavus    # Video with Tavus
AVATAR_PROVIDER=hedra    # Cheaper video
AVATAR_PROVIDER=audio    # Audio only (current)
```

---

## 📊 Check Appointments

```bash
cat appointments.json
```

Example:
```json
{
  "id": "APT0001",
  "patient_name": "محمد أحمد",
  "phone": "+966501234567",
  "service": "تنظيف",
  "date": "2025-11-10",
  "time": "10:00"
}
```

---

## 🐛 Troubleshooting

### Agent Won't Start?
```bash
pip install -r requirements.txt
python agent.py dev
```

### Voice is Female?
Check terminal output shows:
```
✅ تم تكوين الصوت الذكري بنجاح
```

### Not Responding?
1. Check terminal: `🚀 اتصال جديد!`
2. Allow microphone in browser
3. Speak clearly in Arabic

---

## 📚 Documentation

- **docs/testing.md** - Full test guide with conversations
- **docs/arabic.md** - Arabic numbers, dates, phrases

---

## 💡 Next Steps

### Add Database
```bash
pip install sqlalchemy psycopg2-binary
# Edit local_mcp_server.py to use PostgreSQL
```

### Add Video
Uncomment Tavus/Hedra code in agent.py

### Add More Tools
Edit local_mcp_server.py to add new functions

---

**🚀 Start Testing:**
```bash
python agent.py dev
```

Say: **السلام عليكم** 🇸🇦
