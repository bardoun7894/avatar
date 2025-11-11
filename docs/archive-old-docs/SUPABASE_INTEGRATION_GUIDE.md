# Supabase Integration Guide for Call Center

**Status**: ✅ **READY FOR INTEGRATION**
**Current Storage**: Mock (in-memory)
**Database**: Supabase configured in .env
**Upgrade Path**: REST API or supabase-py library

---

## Current Configuration

### Credentials in .env
```env
SUPABASE_URL=https://uzzejiaxyvuhcfcvjyiv.supabase.co
SUPABASE_KEY=eyJhbGc...
SUPABASE_ANON_KEY=eyJhbGc...
DATABASE_URL=postgresql://...
```

### Mock Storage Status
- ✅ Customers stored in memory during session
- ✅ Tickets stored in memory during session
- ✅ Data persists while server is running
- ❌ Data lost on server restart

---

## How to Enable Real Database

### Option 1: Using REST API (Recommended)
**No new dependencies needed** - Uses Python's built-in `urllib`

Steps:
1. Update `crm_system.py` database methods (lines 449-508)
2. Replace mock methods with REST API calls
3. Use headers: `Authorization: Bearer {SUPABASE_KEY}`
4. Example endpoints:
   - POST `/rest/v1/customers` - Create customer
   - GET `/rest/v1/customers?phone=eq.{phone}` - Query by phone
   - POST `/rest/v1/tickets` - Create ticket
   - PATCH `/rest/v1/tickets?ticket_id=eq.{id}` - Update ticket

### Option 2: Using supabase-py Library
**Requires installation** - Async support

Steps:
1. Install: `pip install supabase`
2. Update imports in `crm_system.py`
3. Initialize: `self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)`
4. Use `.from_()` method for queries

### Option 3: Using SQL Directly
**For power users** - Direct PostgreSQL connection

```python
DATABASE_URL=postgresql://...
```

---

## Database Tables Required

### customers
```sql
CREATE TABLE customers (
  customer_id UUID PRIMARY KEY,
  name VARCHAR,
  phone VARCHAR UNIQUE,
  email VARCHAR,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### tickets
```sql
CREATE TABLE tickets (
  ticket_id VARCHAR PRIMARY KEY,
  customer_name VARCHAR,
  customer_phone VARCHAR,
  customer_email VARCHAR,
  subject VARCHAR,
  description TEXT,
  call_id VARCHAR,
  department VARCHAR,
  priority VARCHAR,
  status VARCHAR,
  assigned_to VARCHAR,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  assigned_at TIMESTAMP,
  resolved_at TIMESTAMP
);
```

### ticket_changes (for audit trail)
```sql
CREATE TABLE ticket_changes (
  id SERIAL PRIMARY KEY,
  ticket_id VARCHAR,
  old_status VARCHAR,
  new_status VARCHAR,
  changed_by VARCHAR,
  change_reason VARCHAR,
  changed_at TIMESTAMP
);
```

---

## Testing Database Connection

### Test REST API
```bash
curl -H "Authorization: Bearer $SUPABASE_KEY" \
  https://uzzejiaxyvuhcfcvjyiv.supabase.co/rest/v1/customers
```

### Test SQL Connection
```bash
psql postgresql://...@aws-1-eu-central-1.pooler.supabase.com:6543/postgres
```

---

## Migration Path

1. **Phase 1** (Current): Mock storage ✅
   - Testing and development
   - No external dependencies
   - Perfect for CI/CD testing

2. **Phase 2** (Next): REST API integration
   - Production-ready
   - Uses built-in urllib
   - Data persists in Supabase

3. **Phase 3** (Future): Full ORM
   - SQLAlchemy integration
   - Advanced querying
   - Full schema validation

---

## Key Files to Update

### `/var/www/avatar /callCenter/crm_system.py`
Lines 449-508: Database operation methods

Current structure:
```python
async def _insert_customer_in_db(self, customer):
    # Currently returns True without doing anything
    return True  # Replace with real API call
```

New structure:
```python
async def _insert_customer_in_db(self, customer):
    url = f"{SUPABASE_URL}/rest/v1/customers"
    headers = {"Authorization": f"Bearer {SUPABASE_KEY}"}
    data = {
        "customer_id": customer.customer_id,
        "name": customer.name,
        ...
    }
    # Make HTTP POST request
```

---

## Implementation Timeline

- **Now**: Mock storage working (development/testing)
- **Week 1**: Integrate REST API
- **Week 2**: Full database testing
- **Week 3**: Production deployment

---

## Support

For REST API docs:
- https://supabase.com/docs/guides/api/rest/overview

For PostgreSQL docs:
- https://www.postgresql.org/docs/

For Call Center architecture:
- See /var/www/avatar /MIGRATION_COMPLETE.md
- See /var/www/avatar /PRODUCTION_DEPLOYMENT.md

---

**Ready to integrate?** The infrastructure is already in place. Just implement the REST API calls!
