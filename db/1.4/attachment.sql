-- ----------------------------
-- Table structure for attachment
-- ----------------------------
CREATE TABLE "public"."attachment" (
  "id" varchar(22) COLLATE "pg_catalog"."default" NOT NULL,
  "key" varchar(70) COLLATE "pg_catalog"."default",
  "name" varchar(50) COLLATE "pg_catalog"."default",
  "description" text COLLATE "pg_catalog"."default",
  "attachment" text COLLATE "pg_catalog"."default" NOT NULL,
  "created" timestamp(0) NOT NULL DEFAULT timezone('utc'::text, now()),
  "updated" timestamp(0)
)
;

-- ----------------------------
-- Primary Key structure for table attachment
-- ----------------------------
ALTER TABLE "public"."attachment" ADD CONSTRAINT "attachment_pkey" PRIMARY KEY ("id");
