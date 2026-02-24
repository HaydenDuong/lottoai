-- LottoAI Database Initialization Script --
-- This file runs automatically when PostgreSQL container starts for the first time --

-- Create Users table --
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255),         -- NULL for OAuth users
    oauth_provider VARCHAR(50),         -- 'google', 'facebook', etc.
    oauth_id VARCHAR(255),              -- OAuth provider's user ID
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster lookups --
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_oauth ON users(oauth_provider, oauth_id) WHERE oauth_provider IS NOT NULL;

-- Create user_numbers table --
CREATE TABLE IF NOT EXISTS user_numbers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id)                    -- optional link to a user account
        ON DELETE CASCADE,                                  -- if the user is deleted, their records are deleted as well
    user_number VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create composite unique index: same user account (except anonymous uploads) can't upload same number twice --
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_number_combo
    ON user_numbers(user_id, user_number)
    WHERE user_id IS NOT NULL;

-- Index for faster lookups --
CREATE INDEX IF NOT EXISTS idx_user_numbers_user_id ON user_numbers(user_id);
CREATE INDEX IF NOT EXISTS idx_user_numbers_number ON user_numbers(user_number);

-- Create winning_numbers table --
CREATE TABLE IF NOT EXISTS winning_numbers (
    id SERIAL PRIMARY KEY,
    draw_date DATE NOT NULL,
    region VARCHAR(30),

    -- Prize tier columns --
    -- Single winning number (stored as VARCHAR) --
    prize_8 VARCHAR(10),
    prize_7 VARCHAR(10),
    prize_5 VARCHAR(10),
    prize_2 VARCHAR(10),
    prize_1 VARCHAR(10),
    jp_consolation VARCHAR(10),
    jp VARCHAR(10),

    -- Multiple winning numbers (stored as TEXT array) --
    prize_6 TEXT[],
    prize_4 TEXT[],
    prize_3 TEXT[],
    
    -- DEFAULT = defines a fallback value that 
    -- will automatically be used if no explicit value is provided during INSERT
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Creat index for faster lookups --
CREATE INDEX IF NOT EXISTS idx_draw_date ON winning_numbers(draw_date);

-- Insert sample winning numbers --
INSERT INTO winning_numbers (
    draw_date,
    region,
    prize_8,
    prize_7,
    prize_6,
    prize_5,
    prize_4,
    prize_3,
    prize_2,
    prize_1,
    jp_consolation,
    jp
)
VALUES (
    '2025-05-12',
    'hcm',
    '80',
    '180',
    ARRAY['9515', '2694', '3761'],
    '3180',
    ARRAY['49987', '82917', '40694', '27333', '21970', '78694', '90430'],
    ARRAY['86565', '72963'],
    '08341',
    '66322',
    '32673',
    '493180'
)
ON CONFLICT DO NOTHING;

-- Log Initialization --
-- DO = lets a block of procedural code run directly in SQL
-- "BEGIN ... END" marks the body of the program
-- "RAISE NOTICE" = Python "print()" / JS "console.log()"
DO $$
BEGIN
    RAISE NOTICE 'LottoAI database initialized successfully!';
    RAISE NOTICE 'Tables created: users, winning_numbers, user_numbers';
END $$;