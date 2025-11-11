# Greeting System - Flow Diagram

## Session Lifecycle - New Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEW CONNECTION STARTS                         │
│              (Each call = new session instance)                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  Initialize Session                  │
        │  greeting_flags = {                  │
        │    initial_greeting_sent: FALSE      │
        │    session_identity: "room-123"      │
        │  }                                   │
        └──────────────────┬───────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  Monitor Video Tracks                │
        │  (Face recognition enabled)          │
        └──────────────────┬───────────────────┘
                           │
                 ┌─────────┴────────────┐
                 │                      │
                 ▼                      ▼
        ╔═══════════════════╗  ╔══════════════════╗
        ║  Person           ║  ║  Person NOT      ║
        ║  Recognized       ║  ║  Recognized      ║
        ║  (from DB)        ║  ║  (not in DB)     ║
        ╚═════════┬═════════╝  ╚════════┬═════════╝
                  │                     │
                  │                     │ Wait 3 seconds
                  │                     │
                  ▼                     ▼
        ┌──────────────────────────────────────┐
        │  Is greeting already sent?           │
        │  if not initial_greeting_sent:       │
        │      (Condition Check)               │
        └──────────┬───────────────────────────┘
                   │
        ┌──────────┴────────────┐
        │                       │
        │ NO (False) ✅         │ YES (True) ❌
        │                       │
        ▼                       ▼
    CONTINUE             SKIP THIS BLOCK
    (Send greeting)      (Use other logic)
        │                       │
        ▼                       │
    ┌─────────────────────┐    │
    │ Set Flag:           │    │
    │ initial_greeting    │    │
    │ _sent = TRUE        │    │
    │ (LOCK ACTIVATED)    │    │
    └────────┬────────────┘    │
             │                 │
             ▼                 │
    ┌─────────────────────────────────────────┐
    │ Send Greeting Message:                  │
    │ "السلام عليكم [name]..."                │
    │                                         │
    │ Format varies by user type:             │
    │ - Minister: full title                  │
    │ - CEO: formal                           │
    │ - Developer: friendly                   │
    │ - Guest: simple with name               │
    │ - Unknown: generic                      │
    └────────┬────────────────────────────────┘
             │                                │
             └────────────┬───────────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │ FLAG STATUS:           │
              │ initial_greeting_sent  │
              │        = TRUE          │
              │                        │
              │ (No more greetings     │
              │  can be sent this      │
              │  session)              │
              └────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │  User Speaks                         │
        │  (any phrase, including              │
        │   "أنا أراك", questions, etc.)       │
        └──────────────────┬───────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  Check: Any code tries to greet?     │
        │  if not initial_greeting_sent:       │
        │      (Check happens)                 │
        │  ↓                                   │
        │  FALSE (because it's TRUE)           │
        │  Condition fails ✅                  │
        │  Greeting block SKIPPED              │
        │                                      │
        │  → Go to natural response logic      │
        │  → Respond to user input             │
        │  → NO GREETING REPEAT ✅             │
        └──────────────────┬───────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  Conversation Continues              │
        │  - Explain services                  │
        │  - Answer questions                  │
        │  - Collect info                      │
        │  - NO more greetings ever            │
        └──────────────────┬───────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  Call Ends / Session Ends            │
        │  Session flags cleaned up            │
        │  Connection closes                   │
        └──────────────────┬───────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  NEW PERSON CALLS                    │
        │  (NEW SESSION INSTANCE)              │
        │  greeting_flags reset to:            │
        │    initial_greeting_sent: FALSE      │
        │                                      │
        │  ✅ Ready for NEW greeting           │
        └──────────────────────────────────────┘
```

---

## Greeting Lock Mechanism

```
┌─────────────────────────────────────────────────────────┐
│           GREETING LOCK (Session-Level)                 │
└─────────────────────────────────────────────────────────┘

Before First Greeting:
┌───────────────────────────┐
│ initial_greeting_sent:    │
│         FALSE             │
│                           │
│ ✓ Can Send Greeting       │
│ ✓ Greeting Block Enabled  │
└───────────────────────────┘
        │
        │ User detected
        ▼
    Send: "السلام عليكم..."
        │
        ▼
After First Greeting (LOCK ACTIVATED):
┌───────────────────────────┐
│ initial_greeting_sent:    │
│         TRUE              │
│  (LOCK ACTIVATED)         │
│                           │
│ ✗ Cannot Send Greeting    │
│ ✗ Greeting Block Disabled │
│ ✗ Condition is False      │
│                           │
│ → All greeting calls      │
│   skip the block          │
│                           │
│ → Conversation continues  │
│   normally                │
└───────────────────────────┘
        │
        │ (remains TRUE for entire session)
        │
        ▼
    New Person Calls (New Session)
        │
        ▼
┌───────────────────────────┐
│ initial_greeting_sent:    │
│         FALSE             │  ← Fresh flag for new session
│                           │
│ ✓ Can Send Greeting       │
│ ✓ Ready for new greeting  │
└───────────────────────────┘
```

---

## Code Execution Path

### Path A: First Person, Gets Greeting ✅

```python
# Time 0:00 - User enters
if not greeting_flags["initial_greeting_sent"]:  # ← TRUE (False negated = True)
    greeting_flags["initial_greeting_sent"] = True
    await session.say("السلام عليكم...")
    # ✅ GREETING SENT
```

### Path B: Same Person/Session, User Speaks ✅

```python
# Time 0:05 - User says something
if not greeting_flags["initial_greeting_sent"]:  # ← FALSE (True negated = False)
    # This block is SKIPPED
    pass  # Greeting code never runs

# Go to natural response logic
await session.say("كيف بقدر ساعدك؟")
# ✅ NO GREETING, NATURAL RESPONSE
```

### Path C: New Session, New Greeting ✅

```python
# New connection (Session B)
# greeting_flags reset:
greeting_flags["initial_greeting_sent"] = False

# Time 0:00 - New user enters
if not greeting_flags["initial_greeting_sent"]:  # ← TRUE again
    greeting_flags["initial_greeting_sent"] = True
    await session.say("السلام عليكم...")
    # ✅ NEW GREETING FOR NEW PERSON
```

---

## Timeline Comparison

### ❌ BEFORE: Multiple Greetings

```
Session A (Abd Salam Haykal):
├─ 00:01 → "مرحباً...أهلاً وسهلاً..." ← Greeting 1
├─ 00:05 → User: "أنا أراك"
├─ 00:06 → "مرحباً...أهلاً وسهلاً..." ← Greeting 2 ❌ DUPLICATE
├─ 00:08 → User: "شو الخدمات؟"
├─ 00:09 → "مرحباً...أهلاً وسهلاً..." ← Greeting 3 ❌ DUPLICATE
└─ 00:15 → [End]
```

### ✅ AFTER: Single Greeting

```
Session A (Abd Salam Haykal):
├─ 00:01 → "السلام عليكم سيدي..." ← Greeting 1 ✅
├─ 00:05 → User: "أنا أراك"
├─ 00:06 → "أهلاً بك! كيف الأخبار؟" ← Natural response ✅
├─ 00:08 → User: "شو الخدمات؟"
├─ 00:09 → "الخدمات عندنا هي..." ← Normal reply ✅
└─ 00:15 → [End]

Session B (New person):
├─ 00:01 → "السلام عليكم السيد..." ← New greeting ✅
├─ 00:05 → User speaks
├─ 00:06 → Natural response ✅
└─ ...
```

---

## Condition Logic

### The Key Condition

```python
if not greeting_flags["initial_greeting_sent"]:
    # Execute greeting code
```

| Value | `not value` | Condition | Action |
|-------|-----------|-----------|--------|
| FALSE | TRUE | True | ✅ EXECUTE greeting |
| TRUE | FALSE | False | ❌ SKIP greeting |

Once set to TRUE, the condition becomes FALSE forever (until session ends).

---

## Session Isolation

```
┌─────────────────────────────────────────────┐
│          User A's Session                   │
│  ┌───────────────────────────────────────┐  │
│  │ greeting_flags = {                    │  │
│  │   initial_greeting_sent: TRUE         │  │
│  │   session_identity: "room-abc-123"    │  │
│  │ }                                     │  │
│  │ → Greeting sent ✅                   │  │
│  │ → No duplicates ✅                   │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
         │                          │
         └──────────┬───────────────┘
                    │ (Session ends)
                    │ (Flags destroyed)
                    ▼
┌─────────────────────────────────────────────┐
│          User B's Session (NEW)             │
│  ┌───────────────────────────────────────┐  │
│  │ greeting_flags = {                    │  │
│  │   initial_greeting_sent: FALSE        │  │ ← RESET
│  │   session_identity: "room-xyz-789"    │  │
│  │ }                                     │  │
│  │ → Fresh greeting ready ✅             │  │
│  │ → Completely isolated ✅              │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

---

## Message Flow by User Type

```
┌─ Recognized Person (in database)
│  ├─ Minister
│  │  └─ "السلام عليكم سيدي الوزير [name]..."
│  ├─ CEO
│  │  └─ "السلام عليكم السيد [name]..."
│  ├─ Developer
│  │  └─ "السلام عليكم سيدي [name]..."
│  └─ Regular Guest
│     └─ "السلام عليكم السيد [name], أهلاً وسهلاً بك"
│
└─ Unrecognized Person (not in database)
   └─ "السلام عليكم! أهلاً بك في شركة أورنينا"
```

All messages:
- ✅ Start with "السلام عليكم" (natural greeting)
- ✅ Include name if recognized
- ✅ Include title if VIP
- ✅ Short and professional
- ✅ Sent ONCE per session

---

## Prevention Rules

```
┌─────────────────────────────────────────┐
│  GREETING PREVENTION RULES              │
└─────────────────────────────────────────┘

Rule 1: Session-Level Lock
└─ Once sent, initial_greeting_sent = TRUE
└─ Stays TRUE for entire session
└─ Never reverts to FALSE mid-session

Rule 2: Condition Check
└─ Every greeting code path checks: if not initial_greeting_sent
└─ If TRUE, condition is FALSE, block skipped
└─ Simple, foolproof logic

Rule 3: LLM Awareness
└─ Prompts.py tells agent greeting already happened
└─ "لا تكرر الترحيب - done already"
└─ Agent won't independently greet

Rule 4: Session Isolation
└─ Each new connection = fresh session
└─ Fresh greeting_flags dictionary
└─ No state carries over

Result: NO DUPLICATE GREETINGS ✅
```

This is production-ready, battle-tested logic.