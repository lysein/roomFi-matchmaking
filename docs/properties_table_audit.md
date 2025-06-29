# ✅ `properties` Table — Full Schema & RLS Audit Log

## 1. 🛠 Table Definition (via SQLAlchemy / SQL)

```sql
CREATE TABLE public.properties (
    id SERIAL PRIMARY KEY,
    owner_user_id UUID NOT NULL,
    address VARCHAR,
    location VARCHAR,
    price DOUBLE PRECISION,
    amenities JSON,
    num_rooms INTEGER,
    bathrooms INTEGER,
    available_from TIMESTAMP,
    available_to TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ
);
```

---

## 2. 🔗 Foreign Key Constraint

```sql
ALTER TABLE public.properties
ADD CONSTRAINT fk_owner_user
FOREIGN KEY (owner_user_id)
REFERENCES auth.users(id);
```

- Ensures referential integrity with `auth.users`

---

## 3. 🔐 Enable Row-Level Security (RLS)

```sql
ALTER TABLE public.properties ENABLE ROW LEVEL SECURITY;
```

- Activates RLS enforcement

---

## 4. 📜 RLS Policy: “Users can access and modify their own properties”

```sql
CREATE POLICY "Users can access and modify their own properties"
ON public.properties
FOR ALL
TO public
USING (auth.uid() = owner_user_id);
```

- Restricts access to rows based on ownership

---

## 5. ✅ Validations Performed

| Validation Check                                         | Status | Notes |
|----------------------------------------------------------|--------|-------|
| Table exists in schema `public`                          | ✅     | Confirmed via Supabase SQL Explorer |
| Column `owner_user_id` is UUID                           | ✅     | Required for FK to `auth.users`     |
| Foreign key `fk_owner_user` to `auth.users(id)` exists   | ✅     | Manually verified                   |
| RLS is enabled (`relrowsecurity = true`)                 | ✅     | Confirmed via `pg_class` query      |
| RLS policy is defined for role `public`                  | ✅     | Applies to all authenticated users  |
| RLS condition: `auth.uid() = owner_user_id`              | ✅     | Matches best practice               |
| `created_at` & `updated_at` timestamps are present       | ✅     | For audit trails                    |
| No nullable user reference (owner_user_id is required)   | ✅     | Enforced by `nullable = false`      |
| Policy allows secure client-only filtering               | ✅     | No server bypass risk               |

---

## 6. 🔁 Version Control Note

Make sure this audit log is tracked in Git under:

```bash
git add docs/schema/properties_table_audit.md
git commit -m "Audit log and RLS policy for properties table"
```