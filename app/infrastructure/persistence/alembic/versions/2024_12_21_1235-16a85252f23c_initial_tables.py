"""initial tables

Revision ID: 16a85252f23c
Revises:
Create Date: 2024-12-21 12:35:40.764294

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "16a85252f23c"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum("EARLY", "ACTIVE", "TRANSITION", "PUSHING", "COMPLETE", name="labour_phase").create(
        op.get_bind()
    )
    sa.Enum("EMAIL", "SMS", name="contactmethod").create(op.get_bind())
    op.create_table(
        "birthing_persons",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("first_labour", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_birthing_persons")),
    )
    op.create_table(
        "contacts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("birthing_person_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("phone_number", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column(
            "contact_methods",
            sa.ARRAY(postgresql.ENUM("EMAIL", "SMS", name="contactmethod", create_type=False)),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["birthing_person_id"],
            ["birthing_persons.id"],
            name=op.f("fk_contacts_birthing_person_id_birthing_persons"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_contacts")),
    )
    op.create_table(
        "labours",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("birthing_person_id", sa.UUID(), nullable=False),
        sa.Column("first_labour", sa.Boolean(), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.Column(
            "current_phase",
            postgresql.ENUM(
                "EARLY",
                "ACTIVE",
                "TRANSITION",
                "PUSHING",
                "COMPLETE",
                name="labour_phase",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["birthing_person_id"],
            ["birthing_persons.id"],
            name=op.f("fk_labours_birthing_person_id_birthing_persons"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_labours")),
    )
    op.create_table(
        "contractions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("labour_id", sa.UUID(), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("intensity", sa.Integer(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["labour_id"], ["labours.id"], name=op.f("fk_contractions_labour_id_labours")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_contractions")),
    )
    sa.Enum("ADMIN", "USER", name="userroleenum").drop(op.get_bind())
    sa.Enum("EARLY", "ACTIVE", "TRANSITION", "PUSHING", "COMPLETE", name="labor_phase").drop(
        op.get_bind()
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum("EARLY", "ACTIVE", "TRANSITION", "PUSHING", "COMPLETE", name="labor_phase").create(
        op.get_bind()
    )
    sa.Enum("ADMIN", "USER", name="userroleenum").create(op.get_bind())
    op.drop_table("contractions")
    op.drop_table("labours")
    op.drop_table("contacts")
    op.drop_table("birthing_persons")
    sa.Enum("EMAIL", "SMS", name="contactmethod").drop(op.get_bind())
    sa.Enum("EARLY", "ACTIVE", "TRANSITION", "PUSHING", "COMPLETE", name="labour_phase").drop(
        op.get_bind()
    )
    # ### end Alembic commands ###
