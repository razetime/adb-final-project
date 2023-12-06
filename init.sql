-- unless for testing out DO NOT RUN THIS FILE! Schema is not finalized and this
-- is subject to change.
-- If you have modifications done to 'adb_final' database DO NOT RUN THIS SCRIPT!!
-- change the first two lines to indicate which name you want instead.

-- Initialization script. Creates a database and imports all tables into it.
-- To run it,
-- On Windows: 
--  psql -U postgres -vscriptdir="<project directory>" -f <script path>
--  For example, on my system this is:
--  psql -U postgres -vscriptdir="C:\Users\raghu\OneDrive\Documents\code\adb-final" -f "C:\Users\raghu\OneDrive\Documents\code\adb-final\init.sql"
-- On MacOS:
--  psql -vscriptdir="<project directory>" -f <script path>
--  Example:
--  psql -U postgres -vscriptdir="/home/razetime/adb-final" -f /home/razetime/adb-final/init.sql

-- Tested on psql 11.21.

DROP DATABASE IF EXISTS adb_final;
create database adb_final;

\c adb_final
\cd :scriptdir
\cd e-commerce_data
\cd 電商數據
\! echo %cd% -- print debug
create table product_list_2012 (
  product_id integer,
  product_name varchar(50),
  supplier_code smallint,
  product_vol_length real,
  product_size_width real,
  product_vol_height real,
  product_vol_weight integer,
  storehouse_name varchar(3),
  prod_create_time timestamp
);
\copy product_list_2012 FROM '2012_product_list.csv' WITH (
    FORMAT CSV,
    HEADER true,
    DELIMITER ',',
    QUOTE E'\b'    -- hack to make sure postgres doe not complain about
    );             -- quoting chars.  

