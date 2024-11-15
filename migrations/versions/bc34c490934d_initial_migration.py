"""Initial migration

Revision ID: bc34c490934d
Revises: 
Create Date: 2024-11-15 19:02:57.122398

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc34c490934d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('mcqs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('exam_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'exams', ['exam_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('mcqs', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('exam_id')

    # ### end Alembic commands ###