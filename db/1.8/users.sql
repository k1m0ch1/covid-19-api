-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS "public"."users";
CREATE TABLE "public"."users" (
  "id" varchar(22) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(100) COLLATE "pg_catalog"."default",
  "email" varchar(100) COLLATE "pg_catalog"."default",
  "birthdate" date,
  "phone" varchar(16) COLLATE "pg_catalog"."default",
  "created" timestamp(6) NOT NULL DEFAULT timezone('utc'::text, now()),
  "updated" timestamp(6)
)
;
COMMENT ON COLUMN "public"."users"."id" IS 'short uuid';

-- ----------------------------
-- Primary Key structure for table users
-- ----------------------------
ALTER TABLE "public"."users" ADD CONSTRAINT "users_pkey" PRIMARY KEY ("id");
