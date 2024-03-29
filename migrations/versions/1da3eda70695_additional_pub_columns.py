"""additional pub columns

Revision ID: 1da3eda70695
Revises: 05bc6d703cb1
Create Date: 2020-04-05 23:30:42.731586

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1da3eda70695'
down_revision = '05bc6d703cb1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('additional_publication_columns',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('data', sa.String(length=2048), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['publication.id'], name='publication_id_fk'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('additional_publication_columns')
    # ### end Alembic commands ###
