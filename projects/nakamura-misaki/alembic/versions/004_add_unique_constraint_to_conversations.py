"""Add unique constraint to conversations table

Revision ID: 004_add_unique_constraint_to_conversations
Revises: 003_add_slack_users_table
Create Date: 2025-10-24 13:30:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "004_add_unique_constraint_to_conversations"
down_revision = "003_add_slack_users_table"
branch_labels = None
depends_on = None


def upgrade():
    """
    Add UNIQUE constraint to conversations table to prevent duplicate
    conversations for the same user and channel combination.

    This fixes the MultipleResultsFound error that occurred when multiple
    conversations existed for the same user_id + channel_id.
    """
    # Delete any existing duplicates (keep the oldest conversation)
    # This is a safety measure in case duplicates exist at migration time
    op.execute("""
        DELETE FROM conversations a
        USING conversations b
        WHERE a.conversation_id > b.conversation_id
        AND a.user_id = b.user_id
        AND a.channel_id = b.channel_id
    """)

    # Add UNIQUE constraint to prevent future duplicates
    op.create_unique_constraint("uq_conversations_user_channel", "conversations", ["user_id", "channel_id"])


def downgrade():
    """Remove the unique constraint"""
    op.drop_constraint("uq_conversations_user_channel", "conversations", type_="unique")
