ALTER TABLE landlord_profile
ADD COLUMN num_properties integer DEFAULT 0;

UPDATE landlord_profile
SET num_properties = sub.property_count
FROM (
  SELECT owner_user_id, COUNT(*) AS property_count
  FROM properties
  GROUP BY owner_user_id
) AS sub
WHERE landlord_profile.user_id = sub.owner_user_id;

## 📬 `POST /db/new/user`

Creates a new user profile linked to a Supabase `auth.users` account.

### 🔐 Authentication
The `user_id` should come from the Supabase Auth session. Do **not** generate it manually on the frontend.

---

### 📥 Request Body

**Content-Type:** `application/json`

| Field               | Type      | Required | Description |
|--------------------|-----------|----------|-------------|
| `user_id`           | `string (UUID)` | ✅ | Supabase Auth user ID |
| `first_name`        | `string`  | ✅        | User’s first name |
| `last_name`         | `string`  | ✅        | User’s last name |
| `gender`            | `string`  | ❌        | Optional gender |
| `age`               | `integer` | ❌        | Optional age |
| `budget_min`        | `float`   | ❌        | Minimum monthly budget |
| `budget_max`        | `float`   | ❌        | Maximum monthly budget |
| `location_preference` | `string` | ❌       | Desired city |
| `lifestyle_tags`    | `array`   | ❌        | E.g. `["non_smoker", "early_bird"]` |
| `roomie_preferences`| `object`  | ❌        | JSON with roommate preferences |
| `bio`               | `string`  | ❌        | User bio |
| `profile_image_url` | `string`  | ❌        | Optional avatar URL |

---

### 🧪 Example

```json
{
  "user_id": "2f850ed7-8138-4c7f-aaf4-cd4ba2b5c930",
  "first_name": "Andrea",
  "last_name": "López",
  "gender": "female",
  "age": 24,
  "budget_min": 4000,
  "budget_max": 6000,
  "location_preference": "Monterrey",
  "lifestyle_tags": ["early_bird", "non_smoker"],
  "roomie_preferences": {
    "gender": "any",
    "pets": "no"
  },
  "bio": "Me gusta la tranquilidad y los espacios limpios.",
  "profile_image_url": "https://example.com/avatar.png"
}

### ✅ Success Response

Status: 200 OK

{
  "message": "User profile created",
  "user_id": "2f850ed7-8138-4c7f-aaf4-cd4ba2b5c930"
}

======= UPDATES

03/08/2025 add email col


--- Auditing matches table
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'landlord_profile'
  AND table_schema = 'public';

ALTER TABLE landlord_profile
ADD COLUMN email VARCHAR;

UPDATE landlord_profile
SET email = 
  LOWER(
    REGEXP_REPLACE(
      REGEXP_REPLACE(full_name, '\s+', '.', 'g'),  -- replace spaces with dots
      '[^a-zA-Z0-9.@]', '', 'g'                     -- remove non-alphanumeric characters except dot/@
    )
  ) || '@example.com'
WHERE email IS NULL;

fullname -> firstname, lastname
ALTER TABLE landlord_profile
ADD COLUMN first_name VARCHAR,
ADD COLUMN last_name VARCHAR;

UPDATE landlord_profile
SET 
  first_name = split_part(full_name, ' ', 1),
  last_name = split_part(full_name, ' ', array_length(string_to_array(full_name, ' '), 1));

ALTER TABLE landlord_profile
DROP COLUMN full_name;

ADD CLABE

ALTER TABLE landlord_profile ADD COLUMN clabe VARCHAR;
