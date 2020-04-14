"""ExtPbColumns new table

Revision ID: 19d2ace01d83
Revises: 1da3eda70695
Create Date: 2020-04-06 00:17:45.287371

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19d2ace01d83'
down_revision = '1da3eda70695'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ext_pub_column',
    sa.Column('publication_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('data', sa.String(length=2048), nullable=True),
    sa.ForeignKeyConstraint(['publication_id'], ['publication.id'], name='publication_id_fk'),
    sa.PrimaryKeyConstraint('publication_id', 'name')
    )
    op.drop_table('additional_publication_columns')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('additional_publication_columns',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('data', sa.VARCHAR(length=2048), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['publication.id'], name='publication_id_fk'),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('ext_pub_column')
    # ### end Alembic commands ###
