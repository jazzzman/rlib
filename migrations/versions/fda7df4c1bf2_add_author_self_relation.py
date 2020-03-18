"""add author self-relation

Revision ID: fda7df4c1bf2
Revises: 4b52f1343d67
Create Date: 2020-03-18 20:17:24.354982

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fda7df4c1bf2'
down_revision = '4b52f1343d67'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("author") as batch_op:
        batch_op.add_column(sa.Column('synonym_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('synonym_id_fk', 'author', ['synonym_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("author") as batch_op:
        batch_op.drop_constraint('synonym_id_fk', type_='foreignkey')
        batch_op.drop_column('synonym_id')
    # ### end Alembic commands ###
