DO $$ 
DECLARE
    tbl RECORD;
    col RECORD;
    column_list TEXT;
    query TEXT;
BEGIN
    -- Loop through each table in the public schema
    FOR tbl IN
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    LOOP
        -- Build a comma-separated list of columns for each table
        column_list := '';
        FOR col IN
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = tbl.table_name
        LOOP
            column_list := column_list || col.column_name || ', ';
        END LOOP;

        -- Remove the trailing comma and space
        column_list := RTRIM(column_list, ', ');

        -- Construct and execute a query to fetch all columns and data from the table
        query := 'SELECT ' || column_list || ' FROM ' || tbl.table_name || ';';
        RAISE NOTICE '%', query;
        EXECUTE query;
    END LOOP;
END $$;
