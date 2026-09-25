-- SQL Server DDL for CSV files exported by silver_to_3NF.ipynb.
-- Creates table structures only; import the CSV data after running this script.

CREATE TABLE geography (
    zip NVARCHAR(10) NOT NULL PRIMARY KEY,
    city NVARCHAR(100),
    region NVARCHAR(100),
    district NVARCHAR(100)
);

CREATE TABLE customer (
    customer_id INT NOT NULL PRIMARY KEY,
    zip NVARCHAR(10),
    signup_date DATE,
    gender NVARCHAR(30),
    age_group NVARCHAR(20),
    acquisition_channel NVARCHAR(100),
    CONSTRAINT FK_customer_geography FOREIGN KEY (zip) REFERENCES geography(zip)
);

CREATE TABLE sales_employee (
    sales_employee_id NVARCHAR(20) NOT NULL PRIMARY KEY,
    name NVARCHAR(150)
);

CREATE TABLE product (
    product_id INT NOT NULL PRIMARY KEY,
    product_name NVARCHAR(200),
    category NVARCHAR(100),
    segment NVARCHAR(100),
    size NVARCHAR(30),
    color NVARCHAR(50),
    price DECIMAL(18, 4),
    cogs DECIMAL(18, 4)
);

CREATE TABLE promotion (
    promo_id NVARCHAR(30) NOT NULL PRIMARY KEY,
    promo_name NVARCHAR(200),
    promo_type NVARCHAR(50),
    discount_value DECIMAL(18, 4),
    start_date DATE,
    end_date DATE,
    applicable_category NVARCHAR(100),
    promo_channel NVARCHAR(100),
    stackable_flag BIT,
    min_order_value DECIMAL(18, 4)
);

CREATE TABLE shipper (
    shipper_id NVARCHAR(30) NOT NULL PRIMARY KEY,
    shipper_name NVARCHAR(150),
    shipper_phone NVARCHAR(30),
    shipper_gender NVARCHAR(30),
    shipper_age INT,
    shipper_marital_status NVARCHAR(50),
    shipper_education NVARCHAR(100),
    shipper_company NVARCHAR(150),
    shipper_vehicle NVARCHAR(100),
    shipper_experience_years INT,
    shipper_rating DECIMAL(6, 2),
    delivery_success_rate DECIMAL(8, 4),
    average_delivery_time DECIMAL(10, 2),
    working_shift NVARCHAR(50),
    join_date DATE,
    zip NVARCHAR(10),
    CONSTRAINT FK_shipper_geography FOREIGN KEY (zip) REFERENCES geography(zip)
);

CREATE TABLE [order] (
    order_id INT NOT NULL PRIMARY KEY,
    order_date DATE,
    customer_id INT,
    zip NVARCHAR(10),
    order_status NVARCHAR(50),
    device_type NVARCHAR(50),
    order_source NVARCHAR(100),
    sales_employee_id NVARCHAR(20),
    CONSTRAINT FK_order_customer FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    CONSTRAINT FK_order_geography FOREIGN KEY (zip) REFERENCES geography(zip),
    CONSTRAINT FK_order_sales_employee FOREIGN KEY (sales_employee_id) REFERENCES sales_employee(sales_employee_id)
);

CREATE TABLE order_items (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT,
    unit_price DECIMAL(18, 4),
    discount_amount DECIMAL(18, 4),
    CONSTRAINT PK_order_items PRIMARY KEY (order_id, product_id),
    CONSTRAINT FK_order_items_order FOREIGN KEY (order_id) REFERENCES [order](order_id),
    CONSTRAINT FK_order_items_product FOREIGN KEY (product_id) REFERENCES product(product_id)
);

CREATE TABLE order_item_promotion (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    promo_id NVARCHAR(30) NOT NULL,
    CONSTRAINT PK_order_item_promotion PRIMARY KEY (order_id, product_id, promo_id),
    CONSTRAINT FK_order_item_promotion_item FOREIGN KEY (order_id, product_id)
        REFERENCES order_items(order_id, product_id),
    CONSTRAINT FK_order_item_promotion_promotion FOREIGN KEY (promo_id) REFERENCES promotion(promo_id)
);

CREATE TABLE payment (
    order_id INT NOT NULL PRIMARY KEY,
    payment_method NVARCHAR(50),
    payment_value DECIMAL(18, 4),
    installments INT,
    CONSTRAINT FK_payment_order FOREIGN KEY (order_id) REFERENCES [order](order_id)
);

CREATE TABLE returns (
    return_id NVARCHAR(30) NOT NULL PRIMARY KEY,
    order_id INT,
    product_id INT,
    return_date DATE,
    return_reason NVARCHAR(200),
    return_quantity INT,
    refund_amount DECIMAL(18, 4),
    CONSTRAINT FK_returns_order FOREIGN KEY (order_id) REFERENCES [order](order_id),
    CONSTRAINT FK_returns_product FOREIGN KEY (product_id) REFERENCES product(product_id)
);

CREATE TABLE reviews (
    review_id NVARCHAR(30) NOT NULL PRIMARY KEY,
    order_id INT,
    product_id INT,
    review_date DATE,
    rating INT,
    review_title NVARCHAR(500),
    CONSTRAINT FK_reviews_order FOREIGN KEY (order_id) REFERENCES [order](order_id),
    CONSTRAINT FK_reviews_product FOREIGN KEY (product_id) REFERENCES product(product_id)
);

CREATE TABLE shipment (
    order_id INT NOT NULL PRIMARY KEY,
    shipper_id NVARCHAR(30),
    ship_date DATE,
    delivery_date DATE,
    shipping_fee DECIMAL(18, 4),
    CONSTRAINT FK_shipment_order FOREIGN KEY (order_id) REFERENCES [order](order_id),
    CONSTRAINT FK_shipment_shipper FOREIGN KEY (shipper_id) REFERENCES shipper(shipper_id)
);

CREATE TABLE inventory (
    snapshot_date DATE NOT NULL,
    product_id INT NOT NULL,
    stock_on_hand INT,
    units_received INT,
    units_sold INT,
    stockout_days INT,
    days_of_supply DECIMAL(10, 2),
    fill_rate DECIMAL(10, 6),
    stockout_flag BIT,
    overstock_flag BIT,
    reorder_flag BIT,
    sell_through_rate DECIMAL(10, 6),
    CONSTRAINT PK_inventory PRIMARY KEY (snapshot_date, product_id),
    CONSTRAINT FK_inventory_product FOREIGN KEY (product_id) REFERENCES product(product_id)
);

CREATE TABLE web_traffic (
    [date] DATE NOT NULL PRIMARY KEY,
    sessions INT,
    unique_visitors INT,
    page_views INT,
    bounce_rate DECIMAL(10, 6),
    avg_session_duration_sec DECIMAL(10, 2),
    traffic_source NVARCHAR(100)
);

CREATE TABLE Dim_Date (
    date_key DATE NOT NULL PRIMARY KEY,
    [year] INT,
    [quarter] INT,
    [month] INT,
    month_name NVARCHAR(30),
    [day] INT,
    day_of_week INT,
    day_name NVARCHAR(30),
    is_weekend BIT,
    year_month NVARCHAR(7)
);

CREATE TABLE Dim_Customer (
    customer_id INT NOT NULL PRIMARY KEY,
    zip NVARCHAR(10),
    signup_date DATE,
    gender NVARCHAR(30),
    age_group NVARCHAR(20),
    acquisition_channel NVARCHAR(100),
    city NVARCHAR(100),
    region NVARCHAR(100),
    district NVARCHAR(100)
);

CREATE TABLE Dim_Employee (
    sales_employee_id NVARCHAR(20) NOT NULL PRIMARY KEY,
    name NVARCHAR(150)
);

CREATE TABLE Dim_Geography (
    zip NVARCHAR(10) NOT NULL PRIMARY KEY,
    city NVARCHAR(100),
    region NVARCHAR(100),
    district NVARCHAR(100)
);

CREATE TABLE Dim_Product (
    product_id INT NOT NULL PRIMARY KEY,
    product_name NVARCHAR(200),
    category NVARCHAR(100),
    segment NVARCHAR(100),
    size NVARCHAR(30),
    color NVARCHAR(50),
    price DECIMAL(18, 4),
    cogs DECIMAL(18, 4)
);

CREATE TABLE Fact_Sales (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    date_key DATE,
    customer_id INT,
    sales_employee_id NVARCHAR(20),
    zip NVARCHAR(10),
    order_status NVARCHAR(50),
    quantity INT,
    unit_price DECIMAL(18, 4),
    discount_amount DECIMAL(18, 4),
    gross_amount DECIMAL(18, 4),
    net_amount DECIMAL(18, 4),
    promo_count INT,
    has_promotion BIT,
    CONSTRAINT PK_Fact_Sales PRIMARY KEY (order_id, product_id),
    CONSTRAINT FK_Fact_Sales_Date FOREIGN KEY (date_key) REFERENCES Dim_Date(date_key),
    CONSTRAINT FK_Fact_Sales_Customer FOREIGN KEY (customer_id) REFERENCES Dim_Customer(customer_id),
    CONSTRAINT FK_Fact_Sales_Employee FOREIGN KEY (sales_employee_id) REFERENCES Dim_Employee(sales_employee_id),
    CONSTRAINT FK_Fact_Sales_Geography FOREIGN KEY (zip) REFERENCES Dim_Geography(zip),
    CONSTRAINT FK_Fact_Sales_Product FOREIGN KEY (product_id) REFERENCES Dim_Product(product_id)
);