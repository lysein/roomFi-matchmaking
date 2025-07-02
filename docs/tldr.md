## 🏡 RoomFi Backend — API Overview

A minimal REST API to manage RoomFi’s roommate-property matchmaking system. Built with FastAPI and Supabase.

---

### 👤 Users (Roomies)

* **`POST /db/new/user`**
  Create a new user profile (roomie).
  Required: `user_id`, `first_name`, `budget_min/max`, `preferences`, etc.

* **`GET /get/user`**
  Retrieve an existing user profile by `user_id`.

---

### 🧑‍💼 Landlords

* **`POST /db/new/landlord`**
  Create a new landlord profile.
  Required: `user_id`, optional `bio`, `preferred_locations`, etc.

* **`GET /get/landlord`**
  Fetch a landlord profile by `user_id`.

* **`GET /get/landlord/properties`**
  Get all properties owned by a specific landlord.

---

### 🏠 Properties

* **`POST /db/new/property`**
  Create a new rental property listing.
  Requires `owner_user_id`, address, price, amenities, etc.
  🔒 Strict schema — no extra keys allowed.

* **`GET /get/property`**
  Retrieve a property by ID or filter (likely via query param).

---

### 💘 Matchmaking

* **`POST /matchmaking/match/top`**
  Run a match between a user profile and the top property matches.
  Takes user preferences and returns ranked matches.

---

Let me know if you want to generate:

* A full OpenAPI doc (`.json` or `.yaml`)
* A test-ready Postman collection export
* Swagger tag groupings or route descriptions

You're almost production-ready. 🔥
