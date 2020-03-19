-- ----------------------------
-- Table structure for places
-- ----------------------------
DROP TABLE IF EXISTS "public"."places";
CREATE TABLE "public"."places" (
  "id" varchar(22) COLLATE "pg_catalog"."default" NOT NULL,
  "name" text COLLATE "pg_catalog"."default" NOT NULL,
  "lng" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "lat" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "created" timestamp(6) NOT NULL DEFAULT timezone('utc'::text, now()),
  "updated" timestamp(6)
)
;
COMMENT ON COLUMN "public"."places"."id" IS 'uuid';

-- ----------------------------
-- Primary Key structure for table places
-- ----------------------------
ALTER TABLE "public"."places" ADD CONSTRAINT "places_pkey" PRIMARY KEY ("id");
