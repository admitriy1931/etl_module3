-- Final Project: DWH tables (column names match postgres_load.py promote SQL)

CREATE TABLE IF NOT EXISTS dwh.sessions (
    session_id      VARCHAR(64) PRIMARY KEY,
    user_id         VARCHAR(64) NOT NULL,
    start_time      TIMESTAMP,
    end_time        TIMESTAMP,
    device          VARCHAR(64),
    loaded_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dwh.session_pages (
    id              SERIAL PRIMARY KEY,
    session_id      VARCHAR(64) NOT NULL REFERENCES dwh.sessions(session_id) ON DELETE CASCADE,
    page_url        VARCHAR(512),
    page_order      INT
);

CREATE TABLE IF NOT EXISTS dwh.session_actions (
    id              SERIAL PRIMARY KEY,
    session_id      VARCHAR(64) NOT NULL REFERENCES dwh.sessions(session_id) ON DELETE CASCADE,
    action_name     VARCHAR(128),
    action_order    INT
);

CREATE TABLE IF NOT EXISTS dwh.events (
    event_id        VARCHAR(64) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    event_type      VARCHAR(64),
    details         TEXT,
    loaded_at       TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (event_id, event_timestamp)
);

CREATE TABLE IF NOT EXISTS dwh.tickets (
    ticket_id       VARCHAR(64) PRIMARY KEY,
    user_id         VARCHAR(64) NOT NULL,
    status          VARCHAR(32),
    issue_type      VARCHAR(64),
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP,
    loaded_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dwh.ticket_messages (
    id              SERIAL PRIMARY KEY,
    ticket_id       VARCHAR(64) NOT NULL REFERENCES dwh.tickets(ticket_id) ON DELETE CASCADE,
    sender          VARCHAR(32),
    message         TEXT,
    msg_timestamp   TIMESTAMP,
    msg_order       INT
);

CREATE TABLE IF NOT EXISTS dwh.recommendations (
    user_id         VARCHAR(64) PRIMARY KEY,
    last_updated    TIMESTAMP,
    loaded_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dwh.recommendation_products (
    id              SERIAL PRIMARY KEY,
    user_id         VARCHAR(64) NOT NULL REFERENCES dwh.recommendations(user_id) ON DELETE CASCADE,
    product_id      VARCHAR(64),
    product_order   INT
);

CREATE TABLE IF NOT EXISTS dwh.moderation_reviews (
    review_id       VARCHAR(64) PRIMARY KEY,
    user_id         VARCHAR(64) NOT NULL,
    product_id      VARCHAR(64),
    review_text     TEXT,
    rating          SMALLINT,
    moderation_status VARCHAR(32),
    submitted_at    TIMESTAMP,
    loaded_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dwh.moderation_flags (
    id              SERIAL PRIMARY KEY,
    review_id       VARCHAR(64) NOT NULL REFERENCES dwh.moderation_reviews(review_id) ON DELETE CASCADE,
    flag_name       VARCHAR(128)
);

-- DWH indexes
CREATE INDEX IF NOT EXISTS idx_dwh_sessions_user      ON dwh.sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_dwh_sessions_start      ON dwh.sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_dwh_events_ts           ON dwh.events(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_dwh_events_type         ON dwh.events(event_type);
CREATE INDEX IF NOT EXISTS idx_dwh_tickets_user        ON dwh.tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_dwh_tickets_status      ON dwh.tickets(status);
CREATE INDEX IF NOT EXISTS idx_dwh_tickets_created     ON dwh.tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_dwh_moderation_status   ON dwh.moderation_reviews(moderation_status);
CREATE INDEX IF NOT EXISTS idx_dwh_moderation_submitted ON dwh.moderation_reviews(submitted_at);
