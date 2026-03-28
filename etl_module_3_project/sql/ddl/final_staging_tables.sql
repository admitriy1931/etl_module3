-- Final Project: Staging tables (column names match Python DataFrames)

CREATE TABLE IF NOT EXISTS staging.sessions (
    session_id      VARCHAR(64) PRIMARY KEY,
    user_id         VARCHAR(64) NOT NULL,
    start_time      TIMESTAMP,
    end_time        TIMESTAMP,
    device          VARCHAR(64),
    loaded_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS staging.session_pages (
    id              SERIAL PRIMARY KEY,
    session_id      VARCHAR(64) NOT NULL,
    page_url        VARCHAR(512),
    page_order      INT
);

CREATE TABLE IF NOT EXISTS staging.session_actions (
    id              SERIAL PRIMARY KEY,
    session_id      VARCHAR(64) NOT NULL,
    action_name     VARCHAR(128),
    action_order    INT
);

CREATE TABLE IF NOT EXISTS staging.events (
    event_id        VARCHAR(64) PRIMARY KEY,
    event_timestamp TIMESTAMP,
    event_type      VARCHAR(64),
    details         TEXT,
    loaded_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS staging.tickets (
    ticket_id       VARCHAR(64) PRIMARY KEY,
    user_id         VARCHAR(64) NOT NULL,
    status          VARCHAR(32),
    issue_type      VARCHAR(64),
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP,
    loaded_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS staging.ticket_messages (
    id              SERIAL PRIMARY KEY,
    ticket_id       VARCHAR(64) NOT NULL,
    sender          VARCHAR(32),
    message         TEXT,
    msg_timestamp   TIMESTAMP,
    msg_order       INT
);

CREATE TABLE IF NOT EXISTS staging.recommendations (
    user_id         VARCHAR(64) PRIMARY KEY,
    last_updated    TIMESTAMP,
    loaded_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS staging.recommendation_products (
    id              SERIAL PRIMARY KEY,
    user_id         VARCHAR(64) NOT NULL,
    product_id      VARCHAR(64),
    product_order   INT
);

CREATE TABLE IF NOT EXISTS staging.moderation_reviews (
    review_id       VARCHAR(64) PRIMARY KEY,
    user_id         VARCHAR(64) NOT NULL,
    product_id      VARCHAR(64),
    review_text     TEXT,
    rating          SMALLINT,
    moderation_status VARCHAR(32),
    submitted_at    TIMESTAMP,
    loaded_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS staging.moderation_flags (
    id              SERIAL PRIMARY KEY,
    review_id       VARCHAR(64) NOT NULL,
    flag_name       VARCHAR(128)
);

-- Staging indexes
CREATE INDEX IF NOT EXISTS idx_stg_sessions_user  ON staging.sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_stg_events_type    ON staging.events(event_type);
CREATE INDEX IF NOT EXISTS idx_stg_tickets_status ON staging.tickets(status);
