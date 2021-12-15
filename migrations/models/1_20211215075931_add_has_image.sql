-- upgrade --
ALTER TABLE "tells" ADD "has_image" BOOL NOT NULL;
-- downgrade --
ALTER TABLE "tells" DROP COLUMN "has_image";
