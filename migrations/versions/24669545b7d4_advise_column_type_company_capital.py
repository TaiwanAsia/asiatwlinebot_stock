"""advise column type: company.capital

Revision ID: 24669545b7d4
Revises: 63c15efd1eba
Create Date: 2023-03-07 18:27:33.058084

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '24669545b7d4'
down_revision = '63c15efd1eba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('company', schema=None) as batch_op:
        batch_op.alter_column('capital',
               existing_type=mysql.INTEGER(display_width=11),
               type_=sa.String(length=30),
               existing_nullable=False,
               existing_server_default=sa.text("'0'"))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('company', schema=None) as batch_op:
        batch_op.alter_column('capital',
               existing_type=sa.String(length=30),
               type_=mysql.INTEGER(display_width=11),
               existing_nullable=False,
               existing_server_default=sa.text("'0'"))

    # ### end Alembic commands ###
