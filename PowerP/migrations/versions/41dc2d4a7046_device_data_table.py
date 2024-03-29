"""Device Data table

Revision ID: 41dc2d4a7046
Revises: 8709282ec60a
Create Date: 2023-02-27 13:30:04.943513

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '41dc2d4a7046'
down_revision = '8709282ec60a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('device__data', schema=None) as batch_op:
        batch_op.drop_index('ix_device__data_date')
        batch_op.create_index(batch_op.f('ix_device__data_timestamp'), ['timestamp'], unique=False)
        batch_op.drop_column('device_id')
        batch_op.drop_column('date')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('device__data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date', mysql.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column('device_id', mysql.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_index(batch_op.f('ix_device__data_timestamp'))
        batch_op.create_index('ix_device__data_date', ['date'], unique=False)

    # ### end Alembic commands ###
