-- Create the database 'bri_decesional'
CREATE DATABASE bri_decesional;

-- Create the user 'bri' with the password 'bri'
CREATE USER bri WITH PASSWORD 'bri';

-- Alter user
ALTER DATABASE bri_decesional OWNER TO bri;

-- Grant all privileges on the database 'bri_decesional' to the user 'bri'
GRANT ALL PRIVILEGES ON DATABASE bri_decesional TO bri;
