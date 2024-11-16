"""Add start_time to Exam and status to Result

Revision ID: fccd49d39099
Revises: c49a2f10d15f
Create Date: 2024-11-16 02:48:21.792706

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fccd49d39099'
down_revision = 'c49a2f10d15f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('exam_registrations', schema=None) as batch_op:
        batch_op.drop_column('attempted')

    with op.batch_alter_table('exams', schema=None) as batch_op:
        batch_op.add_column(sa.Column('start_time', sa.Time(), nullable=True))
        batch_op.drop_column('time')
        batch_op.drop_column('results_published')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('exams', schema=None) as batch_op:
        batch_op.add_column(sa.Column('results_published', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('time', sa.TIME(), nullable=True))
        batch_op.drop_column('start_time')

    with op.batch_alter_table('exam_registrations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('attempted', sa.BOOLEAN(), nullable=True))

    # ### end Alembic commands ###