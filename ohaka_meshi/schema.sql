CREATE TABLE IF NOT EXISTS entries (
    id                   INTEGER PRIMARY KEY,
    dish_name            TEXT    NOT NULL,
    is_eating_out        INTEGER NOT NULL DEFAULT 0,
    restaurant_name      TEXT,
    location             TEXT,
    reference_url        TEXT,
    screenshot_filename  TEXT,
    comment              TEXT,
    eaten_date           TEXT    NOT NULL,
    created_at           TEXT    NOT NULL,
    updated_at           TEXT    NOT NULL,
    deleted_at           TEXT
);

CREATE INDEX IF NOT EXISTS idx_entries_eaten_date ON entries(eaten_date DESC);
