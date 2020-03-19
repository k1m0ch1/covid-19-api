-- ----------------------------
-- Table structure for stories
-- ----------------------------
DROP TABLE IF EXISTS "public"."stories";
CREATE TABLE "public"."stories" (
  "id" varchar(22) COLLATE "pg_catalog"."default" NOT NULL,
  "place_id" varchar(22) COLLATE "pg_catalog"."default",
  "user_id" varchar(22) COLLATE "pg_catalog"."default",
  "availability" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "num" int8,
  "price" int8,
  "validity" varchar(50) COLLATE "pg_catalog"."default",
  "created" timestamp(6) DEFAULT timezone('utc'::text, now()),
  "updated" timestamp(6)
)
;

-- ----------------------------
-- Primary Key structure for table stories
-- ----------------------------
ALTER TABLE "public"."stories" ADD CONSTRAINT "stories_pkey" PRIMARY KEY ("id");
