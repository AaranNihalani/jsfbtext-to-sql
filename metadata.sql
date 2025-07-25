CREATE TABLE brands (brand_id int primary key, brand_name varchar(100));
CREATE TABLE categories (category_id int primary key, category_name text);
CREATE TABLE customers (customer_id int primary key, first_name text , last_name text,phone int, email varchar(50), street varchar(100), city text, state text, zip_code int);
CREATE TABLE order_items (order_id int primary key, item_id int,product_id int, quantity int, list_price float, discount float);
CREATE TABLE orders (order_id int, customer_id int, order_status int, order_date date, required_date date, shipped_date date, store_id int, staff_id int);
CREATE TABLE products (product_id int, product_name varchar(100), brand_id int, category_id int, model_year date, list_price float);
CREATE TABLE staffs (staff_id int primary key, first_name text, last_name text, email varchar(100),phone int,actives int, store_id int, manager_id int);
CREATE TABLE stocks (store_id int primary key, product_id int, quantity int);
CREATE TABLE stores (store_id int primary key, store_name text, phone int,  email varchar(100), street varchar(100),  city text, state text, zip_code int);