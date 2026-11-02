-- Run this file after creating the phonebook_db database.
CREATE TABLE IF NOT EXISTS contacts (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    phone VARCHAR(30) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_contacts_first_name
    ON contacts (first_name);

CREATE INDEX IF NOT EXISTS idx_contacts_phone
    ON contacts (phone);
