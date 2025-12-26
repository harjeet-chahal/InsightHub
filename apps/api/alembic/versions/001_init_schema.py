"""init_schema

Revision ID: 001_init_schema
Revises: 
Create Date: 2024-03-25 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '001_init_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Workspaces
    op.create_table('workspaces',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Sources
    op.create_table('sources',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('filename', sa.String(), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ),
    )
    op.create_index(op.f('ix_sources_workspace_id'), 'sources', ['workspace_id'], unique=False)

    # Documents
    op.create_table('documents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('source_id', sa.String(), nullable=False),
        sa.Column('doc_type', sa.String(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ),
    )
    op.create_index(op.f('ix_documents_source_id'), 'documents', ['source_id'], unique=False)

    # Chunks
    op.create_table('chunks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(384), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    )
    op.create_index(op.f('ix_chunks_document_id'), 'chunks', ['document_id'], unique=False)
    # Vector index using ivfflat
    # Note: lists=100 is a placeholder, strictly for larger datasets we need more.
    # We use IF NOT EXISTS to avoid errors if rerunning.
    # op.execute("CREATE INDEX IF NOT EXISTS ix_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)")
    # Using HNSW or just standard GIN is also an option, but for pgvector and simple start we can skip complex index creation or use just a basic one if needed.
    # For now, we will create it:
    op.execute("CREATE INDEX ix_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)")


    # Insights
    op.create_table('insights',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('kind', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ),
    )
    op.create_index(op.f('ix_insights_workspace_id'), 'insights', ['workspace_id'], unique=False)

    # Scorecards
    op.create_table('scorecards',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ),
    )
    op.create_index(op.f('ix_scorecards_workspace_id'), 'scorecards', ['workspace_id'], unique=False)

    # Scorecard Results
    op.create_table('scorecard_results',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('scorecard_id', sa.String(), nullable=False),
        sa.Column('brand', sa.String(), nullable=False),
        sa.Column('results', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['scorecard_id'], ['scorecards.id'], ),
    )
    op.create_index(op.f('ix_scorecard_results_scorecard_id'), 'scorecard_results', ['scorecard_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_scorecard_results_scorecard_id'), table_name='scorecard_results')
    op.drop_table('scorecard_results')
    op.drop_index(op.f('ix_scorecards_workspace_id'), table_name='scorecards')
    op.drop_table('scorecards')
    op.drop_index(op.f('ix_insights_workspace_id'), table_name='insights')
    op.drop_table('insights')
    op.drop_index('ix_chunks_embedding', table_name='chunks')
    op.drop_index(op.f('ix_chunks_document_id'), table_name='chunks')
    op.drop_table('chunks')
    op.drop_index(op.f('ix_documents_source_id'), table_name='documents')
    op.drop_table('documents')
    op.drop_index(op.f('ix_sources_workspace_id'), table_name='sources')
    op.drop_table('sources')
    op.drop_table('workspaces')
