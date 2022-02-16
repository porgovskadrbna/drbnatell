-- upgrade --
ALTER TABLE "tells" ADD "has_video" BOOL NOT NULL DEFAULT False;
ALTER TABLE "tells" ALTER COLUMN "has_image" SET DEFAULT False;
-- downgrade --
ALTER TABLE "tells" DROP COLUMN "has_video";
ALTER TABLE "tells" ALTER COLUMN "has_image" DROP DEFAULT;
