DROP FUNCTION IF EXISTS pbx_add_queue_member(varchar, varchar, integer);
DROP FUNCTION IF EXISTS pbx_remove_operator(varchar);
DROP FUNCTION IF EXISTS pbx_add_operator(varchar, varchar, varchar);
DROP VIEW IF EXISTS sip_operator_auth;
ALTER TABLE queue_members ALTER COLUMN uniqueid DROP DEFAULT;
DROP SEQUENCE IF EXISTS queue_members_uniqueid_seq;
DROP TABLE IF EXISTS pbx_settings;
