# roomFi-matchmaking
 matchmaking engine for the roomfie app

# Licensing Notice

This project is private and currently **not licensed for reuse**.
Do not copy, distribute, or modify the contents without written permission.

# 🏗️ RoomiFi Backend – Development Progress (June 29, 2025)

🎯 **Goal:**
Develop a FastAPI-based backend connected to Supabase for matchmaking between roommates and apartments.

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
│   │   ├── models/         # SQLAlchemy models (User, Property, Match)
│   │   ├── schemas/        # Pydantic schemas (UserCreate, PropertyOut, etc.)
│   │   └── session.py      # Async DB engine and get_db() helper
│   └── ...
├── notebooks/
│   └── init_db.ipynb       # Creates tables in Supabase via async SQLAlchemy
├── .env                    # DATABASE_URL with asyncpg
├── requirements.txt
└── README.md
```

---

## 📦 Models Implemented

### 🧍 `User`

Includes full identity fields and roomie preferences:

```sql
id, first_name, middle_name, last_name_1, last_name_2, email,
gender, age, lgbtq, budget_min, budget_max, location_preference,
lifestyle_tags (JSON), roomie_preferences (JSON), created_at
```

Roomie preferences now support:

- property_type
- move_in_range (start/end)
- pet_friendly
- lgbtq_only
- amenities, amenidad_extras
- parking

### 🏠 `Property`

```sql
id, owner_id (FK), address, location, price, property_type,
num_rooms, bathrooms, deposit_months, contract_length_months,
amenities (JSON), amenidad_extras (JSON), parking (bool),
security_features (JSON), available_from, available_to, created_at
```

### 🤝 `Match`

```sql
id, user_id, matched_user_id (nullable), matched_property_id (nullable),
score, status, created_at
```

---

## 📘 Schemas Implemented

- `UserBase`, `UserCreate`, `UserOut`
- `RoomiePreferences`, `MoveInRange`
- `PropertyBase`, `PropertyCreate`, `PropertyOut`
- `MatchBase`, `MatchCreate`, `MatchOut`

All schemas are located in: `src/db/schemas/`

---

## 🔧 Database Initialization

- Notebook: `notebooks/init_db.ipynb`
- Loads `.env` and connects to Supabase via `postgresql+asyncpg://...`
- Creates all tables from SQLAlchemy `Base.metadata.create_all(...)`

---

## 🧪 Status

| Feature                 | Status     |
|-------------------------|------------|
| Supabase connection     | ✅ Working |
| Tables created          | ✅ Yes     |
| Models + Schemas        | ✅ Done    |
| Roomie preferences model| ✅ Done    |
| API endpoints           | 🔜 Next    |
| Matchmaking logic       | 🔜 Soon    |

---

## 🔜 Next Steps

1. Scaffold `/users` endpoints (create, read)
2. Add `/properties` and `/match` endpoints
3. Build matchmaking logic into `src/services/matchmaking.py`

---

## 🧠 Collaboration Notes

- Run `notebooks/init_db.ipynb` to recreate or inspect the schema
- Use `.env` to configure your local environment
- Supabase handles DB + optional RLS + auth if needed
- Ask for connection string access if joining the team