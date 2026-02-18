-- Runs once on first container start (empty data volume).
-- Database itself is created by POSTGRES_DB env variable.

-- Example table to prove the full stack works end-to-end
CREATE TABLE IF NOT EXISTS items (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Seed row — visible immediately via SELECT after startup
INSERT INTO items (name) VALUES ('hello from init script');
