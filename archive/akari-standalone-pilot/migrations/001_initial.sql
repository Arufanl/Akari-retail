CREATE TABLE IF NOT EXISTS schema_migrations (
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL
) STRICT;

CREATE TABLE IF NOT EXISTS processed_messages (
  id INTEGER PRIMARY KEY,
  whatsapp_message_id TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL CHECK (status IN ('processing', 'replied', 'failed')),
  received_at TEXT NOT NULL,
  replied_at TEXT,
  error_code TEXT
) STRICT;
