# Copyright 2018 Seth Michael Larson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Add user and build"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3925dcddd963'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('commits',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('hexsha', sa.String(), nullable=False),
    sa.Column('ref', sa.String(), nullable=False),
    sa.Column('author_remote_id', sa.String(), nullable=True),
    sa.Column('author_name', sa.String(), nullable=False),
    sa.Column('author_email', sa.String(), nullable=False),
    sa.Column('author_committed_at', sa.DateTime(), nullable=False),
    sa.Column('message', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_commits_author_committed_at'), 'commits', ['author_committed_at'], unique=False)
    op.create_index(op.f('ix_commits_hexsha'), 'commits', ['hexsha'], unique=False)
    op.create_table('jobs',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'running', 'success', 'failure', 'error', name='status'), nullable=False),
    sa.Column('compute_units', sa.SmallInteger(), nullable=False),
    sa.Column('config', postgresql.JSON(none_as_null=True, astext_type=sa.Text()), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jobs_status'), 'jobs', ['status'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('email', sa.String(length=96), nullable=False),
    sa.Column('password', sa.String(length=60), nullable=False),
    sa.Column('email_verified', sa.Boolean(), default=False),
    sa.Column('email_verify_code', sa.String(length=32), nullable=True),
    sa.Column('email_verify_expires', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('builds',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'running', 'success', 'failure', 'error', name='status'), nullable=False),
    sa.Column('commit_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['commit_id'], ['commits.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_builds_status'), 'builds', ['status'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_builds_status'), table_name='builds')
    op.drop_table('builds')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_jobs_status'), table_name='jobs')
    op.drop_table('jobs')
    op.drop_index(op.f('ix_commits_hexsha'), table_name='commits')
    op.drop_index(op.f('ix_commits_author_committed_at'), table_name='commits')
    op.drop_table('commits')
    # ### end Alembic commands ###
