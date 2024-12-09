-- Disable all foreign key constraints
SET session_replication_role = replica;

-- Delete all rows from the table
DELETE FROM {table_name};

-- Reset the auto-increment sequence
DO $$ 
DECLARE 
    seq_name text;
BEGIN 
    SELECT pg_get_serial_sequence('{table_name}', '{sequence_id}') INTO seq_name;
    IF seq_name IS NOT NULL THEN
        EXECUTE 'ALTER SEQUENCE ' || seq_name || ' RESTART WITH 1';
    END IF;
END $$;

-- Re-enable all foreign key constraints
SET session_replication_role = DEFAULT;