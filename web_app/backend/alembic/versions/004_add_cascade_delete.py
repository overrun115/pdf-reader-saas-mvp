"""Add cascade delete to foreign keys

Revision ID: 004
Revises: 003
Create Date: 2024-07-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # For SQLite, we need to recreate the table with the new foreign key constraint
    # This is because SQLite doesn't support ALTER TABLE to modify foreign keys
    
    # Check if we're using SQLite
    bind = op.get_bind()
    if bind.dialect.name == 'sqlite':
        # For SQLite, we can't modify foreign keys directly
        # The cascade delete will be handled at the ORM level
        print("SQLite detected - cascade delete will be handled at ORM level")
        pass
    else:
        # For other databases like PostgreSQL, MySQL, etc.
        with op.batch_alter_table('editable_table_data', schema=None) as batch_op:
            # Drop existing foreign key constraint
            batch_op.drop_constraint('fk_editable_table_data_file_id', type_='foreignkey')
            
            # Add new foreign key constraint with CASCADE delete
            batch_op.create_foreign_key(
                'fk_editable_table_data_file_id',
                'processed_files',
                ['file_id'],
                ['id'],
                ondelete='CASCADE'
            )


def downgrade():
    # Check if we're using SQLite
    bind = op.get_bind()
    if bind.dialect.name == 'sqlite':
        # For SQLite, no changes needed
        print("SQLite detected - no changes needed for downgrade")
        pass
    else:
        # For other databases, revert the foreign key constraint
        with op.batch_alter_table('editable_table_data', schema=None) as batch_op:
            # Drop the CASCADE foreign key constraint
            batch_op.drop_constraint('fk_editable_table_data_file_id', type_='foreignkey')
            
            # Add back the original foreign key constraint without CASCADE
            batch_op.create_foreign_key(
                'fk_editable_table_data_file_id',
                'processed_files',
                ['file_id'],
                ['id']
            )