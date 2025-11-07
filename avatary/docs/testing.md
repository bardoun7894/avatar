# Testing Guide - دليل الاختبار

## Quick Test Phrases

### 1. Greeting
```
السلام عليكم
```

### 2. Book Appointment
```
أريد حجز موعد
```

Answer the questions:
- **Service:** `تنظيف` (cleaning), `فحص` (checkup), `حشوة` (filling)
- **Name:** Your name in Arabic
- **Phone:** Say slowly: `صفر خمسة صفر واحد اثنين ثلاثة...`
- **Email:** `your@email.com`
- **Date:** `عشرة نوفمبر` (November 10)
- **Time:** `العاشرة صباحاً` (10 AM)

### 3. Check Available Times
```
ما هي المواعيد المتاحة؟
```

### 4. View Appointments
```
عرض مواعيدي
```

### 5. Ask About Services
```
ما هي الخدمات المتوفرة؟
```

---

## Full Conversation Example

```
You: السلام عليكم
Agent: وعليكم السلام، أهلاً بك في عيادة بريمير دينتال...

You: أريد حجز موعد
Agent: تمام، ما نوع الخدمة؟

You: تنظيف
Agent: ممتاز، ما اسمك؟

You: محمد أحمد
Agent: رقم الهاتف؟

You: صفر خمسة صفر واحد اثنين ثلاثة أربعة خمسة ستة سبعة
Agent: البريد الإلكتروني؟

You: mohammad@email.com
Agent: التاريخ المناسب؟

You: عشرة نوفمبر
Agent: الوقت؟

You: العاشرة صباحاً
Agent: تم الحجز بنجاح! رقم الموعد: APT0001
```

---

## Tips

### Speak Clearly
- Say numbers slowly: `صفر... خمسة... صفر...`
- Pause between words
- If not understood, repeat

### Check Results
Terminal should show:
```
🚀 اتصال جديد!
✅ الوكيل جاهز!
```

Check appointments:
```bash
cat appointments.json
```

---

## Troubleshooting

### Not Understanding?
1. Speak slower
2. Use simpler phrases
3. Check microphone is working
4. Check terminal for errors

### Voice Wrong Gender?
Check terminal for:
```
✅ تم تكوين الصوت الذكري بنجاح
```

### Agent Not Joining?
1. Make sure agent is running
2. Check credentials in playground
3. Check terminal shows "registered worker"
