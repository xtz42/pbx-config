-- 0002: создать очередь одной строкой.
-- SELECT pbx_add_queue('main');                 -- rrmemory, 20 с на оператора
-- SELECT pbx_add_queue('vip', 'ringall', 15);
CREATE FUNCTION pbx_add_queue(p_name varchar, p_strategy varchar DEFAULT 'rrmemory',
                              p_member_timeout integer DEFAULT 20)
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
    IF p_name !~ '^[a-z0-9_-]{1,64}$' THEN
        RAISE EXCEPTION 'Имя очереди: латиница в нижнем регистре, цифры, _ и -: %', p_name;
    END IF;
    INSERT INTO queues (name, strategy, timeout, retry, wrapuptime, ringinuse,
                        joinempty, leavewhenempty, announce_holdtime, announce_position)
         VALUES (p_name, p_strategy::queue_strategy_values, p_member_timeout, 2, 0, 'no',
                 'yes', 'no', 'no', 'no');
END;
$$;
