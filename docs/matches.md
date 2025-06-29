DROP TABLE IF EXISTS matches CASCADE;

--- Auditing matches table
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'matches'
  AND table_schema = 'public';

-- RLS ENABLED?
SELECT relrowsecurity FROM pg_class WHERE relname = 'matches';

--- RLS policy
CREATE POLICY "Users can view and insert their own matches"
  ON matches
  FOR ALL
  USING (auth.uid() = user_id);
---
CREATE POLICY "Users insert own matches" ON matches
FOR INSERT WITH CHECK (auth.uid() = user_id);

--FK constraint
-- Recommended for data integrity:
ALTER TABLE matches
ADD CONSTRAINT fk_match_user
FOREIGN KEY (user_id) REFERENCES auth.users(id);

ALTER TABLE matches
ADD CONSTRAINT fk_matched_user
FOREIGN KEY (matched_user_id) REFERENCES auth.users(id);

ALTER TABLE matches
ADD CONSTRAINT fk_matched_property
FOREIGN KEY (matched_property_id) REFERENCES properties(id);

-- ENUM for status
CREATE TYPE match_status_enum AS ENUM ('pending', 'matched', 'rejected', 'expired');

ALTER TABLE matches
ALTER COLUMN status TYPE match_status_enum
USING status::match_status_enum;
ALTER TYPE match_status_enum ADD VALUE 'expired';

SELECT unnest(enum_range(NULL::match_status_enum));

-- Foreign Keys
ALTER TABLE matches
  ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES auth.users(id),
  ADD CONSTRAINT fk_matched_user FOREIGN KEY (matched_user_id) REFERENCES auth.users(id),
  ADD CONSTRAINT fk_property FOREIGN KEY (matched_property_id) REFERENCES properties(id);

-- Optional: prevent duplicate matches
ALTER TABLE matches
  ADD CONSTRAINT unique_user_match UNIQUE (user_id, matched_user_id, matched_property_id);

CREATE INDEX idx_matches_user_id ON matches(user_id);
CREATE INDEX idx_matches_matched_user_id ON matches(matched_user_id);
CREATE INDEX idx_matches_matched_property_id ON matches(matched_property_id);
CREATE INDEX idx_matches_status ON matches(status);

ALTER TABLE matches
ALTER COLUMN status SET NOT NULL,
ALTER COLUMN status SET DEFAULT 'pending';


CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = now();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_updated_at
BEFORE UPDATE ON matches
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

ALTER TABLE matches ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_can_access_own_matches
ON matches
FOR SELECT USING (
  auth.uid() = user_id
);