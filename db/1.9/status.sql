-- ----------------------------
-- Table structure for status
-- ----------------------------
DROP TABLE IF EXISTS "public"."status";
CREATE SEQUENCE status_id_seq;

CREATE TABLE status (
    id integer NOT NULL DEFAULT nextval('status_id_seq'),
		confirmed integer NOT NULL,
		recovered integer NOT NULL,
		active_recovered integer NOT NULL,
		deaths integer NOT NULL,
		country_id VARCHAR NOT NULL,
		created TIMESTAMP,
		updated TIMESTAMP
);

ALTER SEQUENCE status_id_seq OWNED BY status.id;
