# 🧠 RoomFi Matchmaking Logic

This document explains how RoomFi recommends the top compatible roommates and properties for any user, based on their profile and preferences.

---

## ✅ Purpose

The matchmaking logic provides real-time recommendations by comparing a user's budget, location, and lifestyle tags against all available roommate candidates and property listings.

---

## ⚙️ How It Works

### 1. Input

- `user_id` (UUID): The user to generate recommendations for
- `top_k` (int, optional): Number of top matches to return (default = 5)

---

### 2. Steps

#### a. Fetch User Profile

Retrieve the user's preferences from the `user_profiles` table:

- `budget_min`, `budget_max`
- `location_preference`
- `lifestyle_tags`

---

#### b. Pre-Filter Roommate Candidates

Query `user_profiles` where:

- `user_id` is different from input user
- `location_preference` matches
- Budget ranges overlap

```sql
SELECT * FROM user_profiles
WHERE user_id != :user_id
AND location_preference = :location
AND budget_max >= :budget_min
AND budget_min <= :budget_max;
```

---

#### c. Pre-Filter Properties

Query `properties` where:

- `location` matches user’s location
- `price` within user’s budget range
- `available_from <= NOW()`

```sql
SELECT * FROM properties
WHERE location = :location
AND price BETWEEN :budget_min AND :budget_max
AND available_from <= CURRENT_TIMESTAMP;
```

---

### 3. Scoring Logic

#### a. Roommate Score

For each roommate candidate:

| Component       | Description                                           |
|----------------|-------------------------------------------------------|
| `budget_score` | 1 - relative diff between average budgets             |
| `tag_score`    | Jaccard similarity of lifestyle_tags                  |
| **Total**      | `0.5 * budget_score + 0.5 * tag_score`                |

---

#### b. Property Score

For each property:

| Component         | Description                                             |
|------------------|---------------------------------------------------------|
| `price_score`     | 1 - relative diff between user's avg. budget and price |
| `amenity_score`   | Jaccard similarity between lifestyle_tags and amenities|
| **Total**        | `0.7 * price_score + 0.3 * amenity_score`               |

---

### 4. Return Top K Matches

- Sort all scored roommates and properties
- Return the top K of each

---

## 📦 Output Format

```json
{
  "top_roommate_matches": [
    {"user_id": "abc-123", "score": 0.85}
  ],
  "top_property_matches": [
    {"property_id": 42, "score": 0.91}
  ]
}
```

---

## 🛠️ Future Improvements

- Support match feedback loops and long-term learning
- Cache scores in a `user_property_matches` table
- Use pgvector embeddings for similarity on lifestyle text
- Add filters like room count, pets, availability range

---

## 📎 Tech Stack

- FastAPI
- Supabase (PostgreSQL + REST API)
- Python scoring logic
