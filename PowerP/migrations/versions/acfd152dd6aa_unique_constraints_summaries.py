"""Unique Constraints Summaries

Revision ID: acfd152dd6aa
Revises: 41dc2d4a7046
Create Date: 2023-02-28 09:23:51.040131

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acfd152dd6aa'
down_revision = '41dc2d4a7046'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('daily__summary', schema=None) as batch_op:
        batch_op.create_unique_constraint('idx_device_date', ['device_id', 'date'])

    with op.batch_alter_table('hourly__summary', schema=None) as batch_op:
        batch_op.create_unique_constraint('idx_device_date', ['device_id', 'date'])

    with op.batch_alter_table('monthly__summary', schema=None) as batch_op:
        batch_op.create_unique_constraint('idx_device_date', ['device_id', 'month', 'year'])

    with op.batch_alter_table('yearly__summary', schema=None) as batch_op:
        batch_op.create_unique_constraint('idx_device_date', ['device_id', 'year'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('yearly__summary', schema=None) as batch_op:
        batch_op.drop_constraint('idx_device_date', type_='unique')

    with op.batch_alter_table('monthly__summary', schema=None) as batch_op:
        batch_op.drop_constraint('idx_device_date', type_='unique')

    with op.batch_alter_table('hourly__summary', schema=None) as batch_op:
        batch_op.drop_constraint('idx_device_date', type_='unique')

    with op.batch_alter_table('daily__summary', schema=None) as batch_op:
        batch_op.drop_constraint('idx_device_date', type_='unique')

    # ### end Alembic commands ###