-- unless for testing out DO NOT RUN THIS FILE! Schema is not finalized and this
-- is subject to change.
-- If you have modifications done to 'adb_final' database DO NOT RUN THIS SCRIPT!!
-- change the first two lines to indicate which name you want instead.

-- Initialization script. Creates a database and imports all tables into it.
-- To run it,
-- run correct_orders_csv.py with python.
-- On Windows: 
--  psql -U postgres -vscriptdir="<project directory>" -f <script path>
--  For example, on my system this is:
--  psql -U postgres -vscriptdir="C:\Users\raghu\OneDrive\Documents\code\adb-final" -f "C:\Users\raghu\OneDrive\Documents\code\adb-final\init.sql"
-- On MacOS:
--  psql -vscriptdir="<project directory>" -f <script path>
--  Example:
--  psql -U postgres -vscriptdir="/home/razetime/adb-final" -f /home/razetime/adb-final/init.sql

-- Tested on psql 11.21.

-- DROP DATABASE IF EXISTS adb_final;
-- create database adb_final;

\c adb_final
\cd :scriptdir
\cd e-commerce_data
\cd 電商數據
\! echo %cd% 
-- create table product_list_2012 (
--   product_id integer,
--   product_name varchar(50),
--   supplier_code smallint,
--   product_vol_length real,
--   product_size_width real,
--   product_vol_height real,
--   product_vol_weight integer,
--   storehouse_name varchar(3),
--   prod_create_time timestamp
-- );
-- \copy product_list_2012 FROM '2012_product_list.csv' WITH (FORMAT CSV,HEADER true,DELIMITER ',',QUOTE E'\b');
-- QUOTE E'\b' is a hack to prevent postgres from complaining about quote chars in the names.

-- 300mb. takes around 30 seconds on my pc.
-- create table if not exists cancel_order (
--   RG_order_number integer,
--   cancel_date timestamp,
--   proc_status smallint,
--   cancel_reason varchar(12)
-- );

-- \copy cancel_order FROM 'cancel_order.csv' WITH (FORMAT CSV,HEADER true,DELIMITER ',',QUOTE E'\b',NULL 'NULL');

-- drop table order_2011Q1_temp;
-- schema for orders:
--   customer_code varchar(50),
--   RG_order_number integer,
--   product_vol_length real,     -- These
--   product_vol_width real,      -- columns
--   product_vol_height real,     -- are
--   product_vol_weight integer,  -- always
--   packaging_box_number integer,-- null.
--   order_number varchar(15),
--   sub_order_number varchar(15),
--   shipping_order_number varchar(30),
--   order_establishment_time timestamp,
--   product_number integer,
--   latest_shipping_date timestamp,
--   shipping_date timestamp,
--   zip_code smallint, 
--   delivery_address varchar(100),
--   delivery_manufacturer varchar(10),
--   warehouse varchar(5),
--   shipping_method varchar(5),
--   cumulative_delivery_times smallint


\echo "importing 2011, Q1"
drop table order_template;
create table order_template (
  customer_code varchar(70),
  RG_order_number integer,
  order_number varchar(15),
  sub_order_number varchar(15),
  shipping_order_number varchar(30),
  order_establishment_time timestamp,
  product_number integer,
  latest_shipping_date timestamp,
  shipping_date timestamp,
  zip_code smallint, 
  delivery_city varchar(10),
  delivery_district varchar(10),
  delivery_manufacturer varchar(20),
  warehouse varchar(5),
  shipping_method varchar(5),
  cumulative_delivery_times smallint
);

drop table order_2011Q1;
create table order_2011Q1 (like order_template including all);
-- \copy order_2011Q1 FROM 'order_2011Q1_corrected.csv' WITH (FORMAT CSV,HEADER true,DELIMITER ',',QUOTE '"',NULL 'NULL');
-- \echo "importing 2011, Q2"
drop table order_2011Q2;
CREATE TABLE order_2011Q2 (like order_template including all);
-- \copy order_2011Q2 FROM 'order_2011Q2_corrected.csv' WITH (FORMAT CSV,HEADER true,DELIMITER ',',QUOTE '"',NULL 'NULL');
-- \echo "importing 2011, Q3"
drop table if exists order_2011Q3;
CREATE TABLE order_2011Q3 (like order_template including all);
-- \copy order_2011Q3 FROM 'order_2011Q3_corrected.csv' WITH (FORMAT CSV,HEADER true,DELIMITER ',',QUOTE E'\b',NULL 'NULL',ESCAPE '\');
-- \echo "importing 2011, Q4"
drop table order_2011Q4;
CREATE TABLE order_2011Q4 (like order_template including all);
-- \copy order_2011Q4 FROM 'order_2011Q4_corrected.csv' WITH (FORMAT CSV,HEADER true,DELIMITER ',',QUOTE '"',NULL 'NULL');
-- \echo "importing 2012, Q1"
drop table order_2012Q1;
CREATE TABLE order_2012Q1 (like order_2011Q1 including all);
-- \copy order_2012Q1 FROM 'order_2012Q1_corrected.csv' WITH (FORMAT CSV,HEADER true,DELIMITER ',',QUOTE '"',NULL 'NULL');
-- \echo "importing 2012, Q2"
drop table order_2012Q2;
CREATE TABLE order_2012Q2 (like order_2011Q1 including all);
-- \copy order_2012Q2 FROM 'order_2012Q2_corrected.csv' WITH (FORMAT CSV,HEADER true,DELIMITER ',',QUOTE '"',NULL 'NULL');


\l+ adb_final
