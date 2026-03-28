-- Webinar 4: Weather data — staging + DWH + state

CREATE TABLE IF NOT EXISTS staging.weather_raw (
    id              SERIAL PRIMARY KEY,
    noted_date      DATE NOT NULL,
    temp            NUMERIC(6,2) NOT NULL,
    direction       VARCHAR(10) NOT NULL,
    loaded_at       TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stg_weather_date ON staging.weather_raw(noted_date);

CREATE TABLE IF NOT EXISTS dwh.weather (
    id              SERIAL PRIMARY KEY,
    noted_date      DATE NOT NULL,
    temp            NUMERIC(6,2) NOT NULL,
    direction       VARCHAR(10) NOT NULL,
    loaded_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (noted_date, temp, direction)
);

CREATE INDEX IF NOT EXISTS idx_dwh_weather_date ON dwh.weather(noted_date);

CREATE TABLE IF NOT EXISTS staging.load_state (
    table_name      VARCHAR(128) PRIMARY KEY,
    last_loaded_date DATE,
    updated_at       TIMESTAMP NOT NULL DEFAULT NOW()
);
