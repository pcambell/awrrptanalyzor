"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-10-02 21:30:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create awr_reports table
    op.create_table(
        'awr_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=512), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('upload_time', sa.DateTime(), nullable=True),
        sa.Column('oracle_version', sa.String(length=50), nullable=True),
        sa.Column('db_name', sa.String(length=100), nullable=True),
        sa.Column('instance_name', sa.String(length=100), nullable=True),
        sa.Column('host_name', sa.String(length=100), nullable=True),
        sa.Column('snapshot_begin', sa.DateTime(), nullable=True),
        sa.Column('snapshot_end', sa.DateTime(), nullable=True),
        sa.Column('snapshot_interval', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'parsing', 'parsed', 'failed', name='reportstatus'), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_awr_reports_db_name'), 'awr_reports', ['db_name'], unique=False)
    op.create_index(op.f('ix_awr_reports_id'), 'awr_reports', ['id'], unique=False)
    op.create_index(op.f('ix_awr_reports_snapshot_begin'), 'awr_reports', ['snapshot_begin'], unique=False)
    op.create_index(op.f('ix_awr_reports_status'), 'awr_reports', ['status'], unique=False)

    # Create performance_metrics table
    op.create_table(
        'performance_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('metric_category', sa.String(length=50), nullable=False),
        sa.Column('metric_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['report_id'], ['awr_reports.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_performance_metrics_id'), 'performance_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_performance_metrics_metric_category'), 'performance_metrics', ['metric_category'], unique=False)
    op.create_index(op.f('ix_performance_metrics_report_id'), 'performance_metrics', ['report_id'], unique=False)
    op.create_index('ix_performance_metrics_data', 'performance_metrics', ['metric_data'], unique=False, postgresql_using='gin')

    # Create diagnostic_results table
    op.create_table(
        'diagnostic_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('rule_id', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.Enum('critical', 'high', 'medium', 'low', name='severity'), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('issue_title', sa.String(length=255), nullable=False),
        sa.Column('issue_description', sa.Text(), nullable=False),
        sa.Column('recommendation', sa.Text(), nullable=False),
        sa.Column('metric_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['report_id'], ['awr_reports.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diagnostic_results_id'), 'diagnostic_results', ['id'], unique=False)
    op.create_index(op.f('ix_diagnostic_results_report_id'), 'diagnostic_results', ['report_id'], unique=False)
    op.create_index(op.f('ix_diagnostic_results_severity'), 'diagnostic_results', ['severity'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_diagnostic_results_severity'), table_name='diagnostic_results')
    op.drop_index(op.f('ix_diagnostic_results_report_id'), table_name='diagnostic_results')
    op.drop_index(op.f('ix_diagnostic_results_id'), table_name='diagnostic_results')
    op.drop_table('diagnostic_results')

    op.drop_index('ix_performance_metrics_data', table_name='performance_metrics')
    op.drop_index(op.f('ix_performance_metrics_report_id'), table_name='performance_metrics')
    op.drop_index(op.f('ix_performance_metrics_metric_category'), table_name='performance_metrics')
    op.drop_index(op.f('ix_performance_metrics_id'), table_name='performance_metrics')
    op.drop_table('performance_metrics')

    op.drop_index(op.f('ix_awr_reports_status'), table_name='awr_reports')
    op.drop_index(op.f('ix_awr_reports_snapshot_begin'), table_name='awr_reports')
    op.drop_index(op.f('ix_awr_reports_id'), table_name='awr_reports')
    op.drop_index(op.f('ix_awr_reports_db_name'), table_name='awr_reports')
    op.drop_table('awr_reports')

    sa.Enum(name='severity').drop(op.get_bind())
    sa.Enum(name='reportstatus').drop(op.get_bind())
