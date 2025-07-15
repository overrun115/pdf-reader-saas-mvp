"""Add Document AI tables

Revision ID: 003_document_ai
Revises: 
Create Date: 2025-07-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_document_ai'
down_revision = None  # Update this with your latest revision
branch_labels = None
depends_on = None


def upgrade():
    # Create document_ai table
    op.create_table('document_ai',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('document_structure', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('total_pages', sa.Integer(), nullable=True),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('export_formats', sa.JSON(), nullable=True),
        sa.Column('last_exported_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_ai_id'), 'document_ai', ['id'], unique=False)

    # Create document_selections table
    op.create_table('document_selections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('selection_name', sa.String(length=255), nullable=False),
        sa.Column('selected_content', sa.JSON(), nullable=True),
        sa.Column('page_numbers', sa.JSON(), nullable=True),
        sa.Column('selection_type', sa.String(length=50), nullable=True),
        sa.Column('bounding_boxes', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['document_ai.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_selections_id'), 'document_selections', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_document_selections_id'), table_name='document_selections')
    op.drop_table('document_selections')
    op.drop_index(op.f('ix_document_ai_id'), table_name='document_ai')
    op.drop_table('document_ai')
