-- migrate:up
CREATE TABLE IF NOT EXISTS tells (
    "id" UUID PRIMARY KEY,
    "text" TEXT NOT NULL,
    "has_image" BOOLEAN NOT NULL DEFAULT FALSE,
    "has_video" BOOLEAN NOT NULL DEFAULT FALSE,
    "created_at" TIMESTAMP NOT NULL
);

-- migrate:down
DROP TABLE IF EXISTS tells;
