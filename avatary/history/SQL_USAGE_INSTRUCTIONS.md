# 📋 SQL File Usage Instructions

## 🎯 File: `create_ornina_complete_database.sql`

This SQL file will **DROP and RECREATE** all knowledge base tables with fresh data from Avatar.xlsx.

---

## 🔄 What It Does

### When You Run This SQL:

1. **Drops existing tables** (if they exist):
   ```sql
   DROP TABLE IF EXISTS company_info CASCADE;
   DROP TABLE IF EXISTS work_areas CASCADE;
   DROP TABLE IF EXISTS target_markets CASCADE;
   DROP TABLE IF EXISTS products CASCADE;
   DROP TABLE IF EXISTS training_programs CASCADE;
   DROP TABLE IF EXISTS faqs CASCADE;
   ```

2. **Creates fresh tables** with proper structure

3. **Inserts all data** from Avatar.xlsx (56+ records)

4. **Result**: Clean database with latest data

---

## ✅ Safe to Run Multiple Times

**You can run this SQL as many times as you want!**

- First time: Creates tables + inserts data
- Second time: Drops old tables → Creates new → Inserts fresh data
- Third time: Same behavior - always fresh data

**No duplicates, no errors, no problems!**

---

## 🚀 How to Run

### In Supabase Dashboard:

1. Open https://supabase.com
2. Go to your project
3. Click **SQL Editor** in left sidebar
4. Click **New Query**
5. Copy entire content of `create_ornina_complete_database.sql`
6. Paste into editor
7. Click **Run** (or press Ctrl+Enter)
8. Wait for completion (~5-10 seconds)

### Expected Output:
```
✅ DROP TABLE IF EXISTS (x6)
✅ CREATE TABLE (x6)
✅ CREATE INDEX (x11)
✅ ALTER TABLE (x6)
✅ CREATE POLICY (x6)
✅ GRANT (x12)
✅ INSERT INTO (x56+)
```

---

## 📊 Verification

After running, verify the data:

```sql
SELECT 'company_info' as table_name, count(*) as rows FROM company_info
UNION ALL
SELECT 'work_areas', count(*) FROM work_areas
UNION ALL
SELECT 'target_markets', count(*) FROM target_markets
UNION ALL
SELECT 'products', count(*) FROM products
UNION ALL
SELECT 'training_programs', count(*) FROM training_programs
UNION ALL
SELECT 'faqs', count(*) FROM faqs
ORDER BY table_name;
```

**Expected Result:**
```
table_name          | rows
--------------------|------
company_info        | 6
faqs                | 4
products            | 6
target_markets      | 6
training_programs   | 6
work_areas          | 28
```

**Total: 56 rows**

---

## ⚠️ Important Notes

### What Gets DELETED:
- ✅ Knowledge base tables (company_info, work_areas, target_markets, products, training_programs, faqs)
- ✅ All data in these tables

### What is SAFE (NOT affected):
- ✅ `users` table - User contact info
- ✅ `messages` table - Conversation history
- ✅ `inquiries` table - Customer inquiries (if exists)
- ✅ `consultations` table - Bookings (if exists)
- ✅ `training_registrations` table - Signups (if exists)

**Only knowledge base tables are replaced!**

---

## 🔄 When to Run This

### Run when:
1. **First time setup** - Creating database structure
2. **Updating company info** - After editing Avatar.xlsx
3. **Adding new products/services** - After updating Excel
4. **Fixing data issues** - To reset to clean state

### Don't need to run when:
- Adding users (auto-saved by agent)
- Saving conversations (auto-saved by agent)
- Adding customer inquiries (handled by tools)
- Registering for training (handled by tools)

---

## 📝 Example Scenarios

### Scenario 1: First Time Setup
```
Status: No tables exist yet
Action: Run SQL
Result: Creates 6 tables with 56 records ✅
```

### Scenario 2: Updating Product Info
```
Status: Tables already exist with old data
Action: Edit Avatar.xlsx → Run SQL
Result: Drops old tables → Creates new → Fresh data ✅
```

### Scenario 3: Accidentally Run Twice
```
Status: Just ran it successfully
Action: Run SQL again by mistake
Result: Drops → Recreates → Same data (no problem) ✅
```

### Scenario 4: Want to Update FAQ Only
```
Status: Tables exist
Action: Edit SQL → Change FAQ section → Run
Result: All tables replaced (FAQs updated) ✅
```

---

## 🎯 Quick Reference

| Action | Command | Safe? |
|--------|---------|-------|
| **Create database first time** | Run full SQL | ✅ Yes |
| **Update all data** | Run full SQL | ✅ Yes |
| **Run twice by mistake** | (Already ran) | ✅ Yes - no problem |
| **Add new product** | Edit Excel → Run SQL | ✅ Yes |
| **Fix wrong data** | Edit SQL → Run | ✅ Yes |
| **Delete everything** | (Don't run SQL) | ✅ Safe - users/messages not affected |

---

## 🐛 Troubleshooting

### Error: "relation already exists"
**Cause:** Table exists and can't be dropped
**Fix:** Check if you have dependencies, or run:
```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
```
Then run the SQL again.

### Error: "permission denied"
**Cause:** User doesn't have drop/create permissions
**Fix:** Make sure you're logged in as admin in Supabase

### No data showing after run
**Cause:** SQL ran but insert failed silently
**Fix:** Check Supabase logs for errors
- Look for single quote issues in Arabic text
- Check for array format problems

### Want to keep old data
**Option 1:** Backup first:
```sql
-- Backup products
CREATE TABLE products_backup AS SELECT * FROM products;
```

**Option 2:** Don't run this SQL - update tables manually:
```sql
UPDATE products SET name = 'new name' WHERE id = 1;
```

---

## ✅ Summary

**`create_ornina_complete_database.sql`** is:
- ✅ Safe to run multiple times
- ✅ Replaces knowledge base tables only
- ✅ Doesn't affect users/messages/conversations
- ✅ Always gives fresh data from Avatar.xlsx
- ✅ No duplicates possible
- ✅ Self-contained (no manual steps needed)

**Just run it and you're done!** 🚀
