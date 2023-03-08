"""
add category user
"""

from yoyo import step

__depends__ = {'pet_20230106_01_5Uk7F-purhases'}

steps = [
    step(
        """
            ALTER TABLE categories
                ADD COLUMN user_id INTEGER REFERENCES users (id) ON DELETE CASCADE
            ;
        """,
        """
            ALTER TABLE categories
                DROP COLUMN user_id
            ;
        """
    ),
]
