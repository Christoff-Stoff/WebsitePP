"""Device Data table

Revision ID: 8709282ec60a
Revises: 16c29172c58c
Create Date: 2023-02-27 13:25:12.598328

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8709282ec60a'
down_revision = '16c29172c58c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('device__data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('serial', sa.String(length=50), nullable=False))
        batch_op.add_column(sa.Column('date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('device_serial', sa.String(length=50), nullable=True))
        batch_op.drop_index('ix_device__data_timestamp')
        batch_op.create_index(batch_op.f('ix_device__data_date'), ['date'], unique=False)
        batch_op.drop_constraint('device__data_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'device', ['device_serial'], ['serial'])
        batch_op.drop_column('timestamp')
        batch_op.drop_column('device_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('device__data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('device_id', mysql.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('timestamp', mysql.DATETIME(), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('device__data_ibfk_1', 'device', ['device_id'], ['id'])
        batch_op.drop_index(batch_op.f('ix_device__data_date'))
        batch_op.create_index('ix_device__data_timestamp', ['timestamp'], unique=False)
        batch_op.drop_column('device_serial')
        batch_op.drop_column('date')
        batch_op.drop_column('serial')

    # ### end Alembic commands ###
