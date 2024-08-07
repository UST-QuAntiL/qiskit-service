"""empty message

Revision ID: e551728398ab
Revises: 13d46ba5b86f
Create Date: 2024-07-10 09:29:15.216667

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e551728398ab'
down_revision = '13d46ba5b86f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'result', 'generated__circuit', ['generated_circuit_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'result', type_='foreignkey')
    # ### end Alembic commands ###
