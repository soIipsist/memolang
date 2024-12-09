-- Replace 'your_database_name' with the name of the database you want to drop.

-- Terminate all connections to the target database
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '{database_name}';

-- Now, drop the target database
DROP DATABASE {database_name};