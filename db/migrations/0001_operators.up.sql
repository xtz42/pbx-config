-- 0001: операторы и очереди «строкой в БД».
-- Применяется к базе каждого тенанта поверх таблиц Asterisk (db/asterisk-alembic).

-- Служебные настройки, которые заполняет Ansible (инфраструктура, не данные).
CREATE TABLE pbx_settings (
    key     varchar(64) PRIMARY KEY,
    value   varchar(255) NOT NULL,
    comment varchar(255)
);

-- Asterisk не задаёт uniqueid участникам очередей сам.
CREATE SEQUENCE queue_members_uniqueid_seq;
ALTER TABLE queue_members ALTER COLUMN uniqueid SET DEFAULT nextval('queue_members_uniqueid_seq');

-- Учётные данные операторов для Kamailio (регистратор). Только чтение.
CREATE VIEW sip_operator_auth AS
    SELECT a.username, a.password
      FROM ps_auths a
      JOIN ps_endpoints e ON e.id = a.id
     WHERE a.auth_type = 'userpass';

-- Добавить оператора: SELECT pbx_add_operator('1001', 'пароль', 'Фамилия Имя');
-- Asterisk звонит оператору через SBC (ps_aors.contact), регистрацию проверяет Kamailio.
CREATE FUNCTION pbx_add_operator(p_ext varchar, p_password varchar, p_name varchar DEFAULT NULL)
RETURNS void LANGUAGE plpgsql AS $$
DECLARE
    v_sbc varchar;
BEGIN
    IF p_ext !~ '^[0-9]{2,8}$' THEN
        RAISE EXCEPTION 'Номер оператора должен состоять из 2–8 цифр: %', p_ext;
    END IF;
    IF length(p_password) < 8 THEN
        RAISE EXCEPTION 'Пароль оператора короче 8 символов';
    END IF;
    SELECT value INTO v_sbc FROM pbx_settings WHERE key = 'sbc_address';
    IF v_sbc IS NULL THEN
        RAISE EXCEPTION 'Не задан pbx_settings.sbc_address (раскатайте роль postgresql)';
    END IF;

    INSERT INTO ps_aors (id, contact, max_contacts, qualify_frequency)
         VALUES (p_ext, 'sip:' || p_ext || '@' || v_sbc, 1, 0);
    INSERT INTO ps_auths (id, auth_type, username, password)
         VALUES (p_ext, 'userpass', p_ext, p_password);
    INSERT INTO ps_endpoints (id, aors, context, disallow, allow, direct_media,
                              dtmf_mode, callerid, language)
         VALUES (p_ext, p_ext, 'from-operator', 'all', 'alaw,ulaw', 'no',
                 'rfc4733', coalesce(p_name, p_ext) || ' <' || p_ext || '>', NULL);
END;
$$;

CREATE FUNCTION pbx_remove_operator(p_ext varchar)
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM queue_members WHERE interface = 'PJSIP/' || p_ext;
    DELETE FROM ps_endpoints WHERE id = p_ext;
    DELETE FROM ps_auths WHERE id = p_ext;
    DELETE FROM ps_aors WHERE id = p_ext;
END;
$$;

-- Добавить оператора в очередь: SELECT pbx_add_queue_member('main', '1001');
CREATE FUNCTION pbx_add_queue_member(p_queue varchar, p_ext varchar, p_penalty integer DEFAULT 0)
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM queues WHERE name = p_queue) THEN
        RAISE EXCEPTION 'Нет очереди %', p_queue;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM ps_endpoints WHERE id = p_ext) THEN
        RAISE EXCEPTION 'Нет оператора %', p_ext;
    END IF;
    INSERT INTO queue_members (queue_name, interface, membername, state_interface, penalty, paused)
         VALUES (p_queue, 'PJSIP/' || p_ext, p_ext, 'PJSIP/' || p_ext, p_penalty, 0);
END;
$$;
