# roomFi-matchmaking
 matchmaking engine for the roomfi app

# Licensing Notice

This project is private and currently **not licensed for reuse**.
Do not copy, distribute, or modify the contents without written permission.

# 🏗️ RoomiFi Backend – Development Progress (June 29, 2025)

🎯 **Goal:**
Develop a FastAPI-based backend connected to Supabase for matchmaking between roommate groups and properties, including a financial staking model to unlock access.

---

## ✅ Current Stack

| Component        | Technology            |
|------------------|------------------------|
| Backend API      | FastAPI                |
| ORM              | SQLAlchemy (async)     |
| Database         | Supabase (PostgreSQL)  |
| Driver           | `asyncpg`              |
| Notebook         | Jupyter (for DB init)  |
| Environment Mgmt | `.env` + `python-dotenv` |
| Project Layout   | Modular `src/` + `notebooks/` structure |

---

## 📁 Project Structure (simplified)

```
roomfi-matchmaking/
├── src/
│   ├── db/
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── property.py
│   │   │   ├── match.py
│   │   │   ├── group.py              # ✅ NEW
│   │   │   ├── group_match.py        # ✅ NEW
│   │   │   ├── stake.py              # ✅ NEW
│   │   ├── schemas/
│   │   └── session.py
│   └── ...
├── notebooks/
│   └── init_db.ipynb                 # ✅ Updated with new model imports
├── .env
├── requirements.txt
└── README.md
```

---

## 📦 Models Implemented

### 🧍 `User` – individual renter

Includes identity, preferences, and lifestyle tags.

### 🏘️ `RoomieGroup` – group of users forming a co-renting party
```sql
id, members (array of user_ids), status, created_at
```

### 🧮 `GroupMatch` – links a group to a property with a match score
```sql
id, group_id, property_id, match_score, status, created_at
```

### 💸 `Stake` – payment tracking for access unlocking
```sql
id, user_id, group_id, amount_mxn, confirmed, confirmed_at, txn_id
```

### 🏠 `Property` – available rental units
Updated with:
```sql
preferred_tenants (JSON)
```

---

## 🔧 Database Initialization

- Notebook: `notebooks/init_db.ipynb`
- Imports all new models
- Creates all tables via SQLAlchemy’s `Base.metadata.create_all`

---

## ✅ Commit Reference

These architectural changes were introduced in commit:

```txt
SHA: [INSERT_COMMIT_SHA_HERE]
```

---

## 🧪 Status

| Feature                      | Status     |
|------------------------------|------------|
| Supabase connection          | ✅ Working |
| Tables created               | ✅ Yes     |
| Matchable group modeling     | ✅ Added   |
| Staking/payment tracking     | ✅ Added   |
| Tenant preference filtering  | ✅ Added   |
| API endpoints                | 🔜 Next    |
| Matchmaking scoring logic    | 🔜 Soon    |

---

## 🔜 Next Steps

1. Scaffold `/users` and `/match/find` endpoints
2. Define JSON response shape for group+property recommendations
3. Stub payment service or Juno webhook logic
4. Add chat unlock API gated by stake confirmation

---

## 🧠 Collaboration Notes

- To reset DB schema: run `notebooks/init_db.ipynb`
- `.env` must contain `DATABASE_URL` with asyncpg
- Access to Supabase and deposits/transactions are currently mocked