"""
add budget
"""

from yoyo import step

__depends__ = {'pet_20230305_01_xAJq9-adds-invite-tokens'}

steps = [
    step(
        """
            ALTER TABLE categories
                ADD COLUMN month_budget INTEGER DEFAULT 0
            ;
        """,
        """
            ALTER TABLE categories
                DROP COLUMN month_budget
            ;
        """
    ),
]
