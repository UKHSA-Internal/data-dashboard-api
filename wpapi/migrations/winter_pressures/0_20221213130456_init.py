from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "multipathogen" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "week" INT NOT NULL,
    "year" INT NOT NULL,
    "week_key" VARCHAR(7) NOT NULL,
    "publish_date" DATE NOT NULL,
    "season" VARCHAR(9),
    "influenza_pct" DECIMAL(3,1),
    "rsv_pct" DECIMAL(3,1),
    "rhinovirus_pct" DECIMAL(3,1),
    "parainfluenza_pct" DECIMAL(3,1),
    "hmpv_pct" DECIMAL(3,1),
    "adenovirus_pct" DECIMAL(3,1),
    "sars_cov_pct" DECIMAL(3,1),
    "influenza_a_h3n2_n_pct" DECIMAL(3,1),
    "influenza_a_h1n1_pdm09_n_pct" DECIMAL(3,1),
    "influenza_a_not_subtyped_n_pct" DECIMAL(3,1),
    "influenza_b_n_pct" DECIMAL(3,1)
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
