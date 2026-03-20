CREATE TABLE "schema_migrations" (version varchar(128) primary key);
CREATE TABLE tells (
    "id" UUID PRIMARY KEY,
    "text" TEXT NOT NULL,
    "has_image" BOOLEAN NOT NULL DEFAULT FALSE,
    "has_video" BOOLEAN NOT NULL DEFAULT FALSE,
    "created_at" TIMESTAMP NOT NULL
);
-- Dbmate schema migrations
INSERT INTO "schema_migrations" (version) VALUES
  ('20260320214437');
