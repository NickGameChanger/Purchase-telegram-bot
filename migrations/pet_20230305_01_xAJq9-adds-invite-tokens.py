"""
adds-invite_tokens
"""

from yoyo import step

__depends__ = {'pet_20230303_01_oR29y-add-category-user'}

steps = [
    step(
        """
            CREATE TABLE invite_tokens(
                id SERIAL PRIMARY KEY,
                team_id INTEGER REFERENCES teams (id) ON DELETE CASCADE,
                token TEXT,
                created_at TIMESTAMP DEFAULT now()
            );
        """,
        """
            DROP TABLE invite_tokens;
        """
    ),
]
