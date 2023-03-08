"""
purchases
"""

from yoyo import step

__depends__ = {}  # type: ignore

steps = [
    step(
        """
            CREATE TABLE teams (
                id SERIAL PRIMARY KEY,
                team_name VARCHAR(100),
                google_sheet_url TEXT

            );
        """,
        """
            DROP TABLE teams;
        """
    ),
    step(
        """
            CREATE TABLE categories (
                id SERIAL PRIMARY KEY,
                category_name VARCHAR(100) UNIQUE

            );
        """,
        """
            DROP TABLE categories;
        """
    ),
    step(
        """
            CREATE EXTENSION IF NOT EXISTS citext;
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                team_id INTEGER REFERENCES teams ON DELETE RESTRICT,
                first_name TEXT,
                last_name TEXT,
                telegram VARCHAR(255),
                source VARCHAR(255),
                email citext UNIQUE,
                telegram_chat_id INTEGER UNIQUE,
                bot_stopped_at DATE DEFAULT NULL,
                registration_completed_at TIMESTAMP DEFAULT now(),
                telegram_bot_stopped_at TIMESTAMP,
                telegram_step TEXT
            );
        """,
        """
            DROP TABLE users;
        """
    ),
    step(
        """
            CREATE TABLE purchases (
                id SERIAL PRIMARY KEY,
                purchase_name VARCHAR (150),
                price INTEGER NOT NULL,
                purchase_date DATE DEFAULT NOW()::date,
                category_id INTEGER REFERENCES categories ON DELETE SET NULL,
                user_id INTEGER REFERENCES users ON DELETE CASCADE,
                created_at TIMESTAMP  DEFAULT NOW()

            );
        """,
        """
            DROP TABLE purchases;
        """
    )
]
