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
