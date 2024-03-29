"""initial

Revision ID: b9d4fb17eb8d
Revises: 
Create Date: 2023-03-27 14:59:12.142678

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "b9d4fb17eb8d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "cookies",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("created", postgresql.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated", postgresql.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("data", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__cookies")),
    )
    op.create_table(
        "headers",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("created", postgresql.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated", postgresql.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("data", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__headers")),
    )
    op.create_table(
        "subscribers",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("created", postgresql.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated", postgresql.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("active", sa.Boolean(), server_default="False", nullable=False),
        sa.Column("max_price", postgresql.ARRAY(sa.TEXT()), nullable=True),
        sa.Column("floor", postgresql.ARRAY(sa.TEXT()), nullable=True),
        sa.Column("rooms", postgresql.ARRAY(sa.TEXT()), nullable=True),
        sa.Column("heating", postgresql.ARRAY(sa.TEXT()), nullable=True),
        sa.Column("areas", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("furniture", postgresql.ARRAY(sa.TEXT()), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__subscribers")),
    )
    op.create_table(
        "towns",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("created", postgresql.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated", postgresql.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("name", sa.TEXT(), nullable=False),
        sa.Column("last_parsing", postgresql.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__towns")),
    )
    op.create_table(
        "ads",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("created", postgresql.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated", postgresql.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("last_seen", postgresql.TIMESTAMP(), nullable=False),
        sa.Column("removed", sa.Boolean(), server_default="False", nullable=False),
        sa.Column("last_condition_removed", sa.Boolean(), server_default="False", nullable=False),
        sa.Column("thumbnail_url", sa.TEXT(), nullable=False),
        sa.Column("title", sa.TEXT(), nullable=True),
        sa.Column("lat", sa.FLOAT(), nullable=True),
        sa.Column("lon", sa.FLOAT(), nullable=True),
        sa.Column("attributes", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("url", sa.TEXT(), nullable=True),
        sa.Column("photos", postgresql.ARRAY(sa.TEXT()), nullable=True),
        sa.Column("map_image", sa.TEXT(), nullable=True),
        sa.Column("address_town", sa.INTEGER(), nullable=True),
        sa.Column("district", sa.TEXT(), nullable=True),
        sa.Column("area", sa.TEXT(), nullable=True),
        sa.Column("creation_date", postgresql.TIMESTAMP(), nullable=True),
        sa.Column("gross_area", sa.TEXT(), nullable=True),
        sa.Column("net_area", sa.TEXT(), nullable=True),
        sa.Column("room_count", sa.TEXT(), nullable=True),
        sa.Column("building_age", sa.TEXT(), nullable=True),
        sa.Column("floor", sa.TEXT(), nullable=True),
        sa.Column("building_floor_count", sa.INTEGER(), nullable=True),
        sa.Column("heating_type", sa.TEXT(), nullable=True),
        sa.Column("bathroom_count", sa.TEXT(), nullable=True),
        sa.Column("balcony", sa.Boolean(), nullable=True),
        sa.Column("furniture", sa.Boolean(), nullable=True),
        sa.Column("using_status", sa.TEXT(), nullable=True),
        sa.Column("dues", sa.TEXT(), nullable=True),
        sa.Column("deposit", sa.TEXT(), nullable=True),
        sa.ForeignKeyConstraint(["address_town"], ["towns.id"], name=op.f("fk__ads__address_town__towns")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__ads")),
    )
    op.create_table(
        "areas",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("created", postgresql.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated", postgresql.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("name", sa.TEXT(), nullable=False),
        sa.Column("town_id", sa.INTEGER(), nullable=False),
        sa.Column("is_closed", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["town_id"], ["towns.id"], name=op.f("fk__areas__town_id__towns")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__areas")),
    )
    op.create_table(
        "prices",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("created", postgresql.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated", postgresql.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("ad_id", sa.INTEGER(), nullable=False),
        sa.Column("price", sa.FLOAT(), nullable=False),
        sa.ForeignKeyConstraint(["ad_id"], ["ads.id"], name=op.f("fk__prices__ad_id__ads")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__prices")),
    )
    op.create_table(
        "telegram_posts",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("created", postgresql.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated", postgresql.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("ad_id", sa.INTEGER(), nullable=False),
        sa.Column("channel_message_id", sa.INTEGER(), nullable=False),
        sa.Column("chat_message_id", sa.INTEGER(), nullable=False),
        sa.ForeignKeyConstraint(["ad_id"], ["ads.id"], name=op.f("fk__telegram_posts__ad_id__ads")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__telegram_posts")),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("telegram_posts")
    op.drop_table("prices")
    op.drop_table("areas")
    op.drop_table("ads")
    op.drop_table("towns")
    op.drop_table("subscribers")
    op.drop_table("headers")
    op.drop_table("cookies")
    # ### end Alembic commands ###
