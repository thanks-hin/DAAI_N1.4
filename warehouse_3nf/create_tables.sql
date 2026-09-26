-- SQL Server DDL for CSV files exported by silver_to_3NF.ipynb.
-- Creates table structures only; import the CSV data after running this script.
CREATE DATABASE SalesLogisticsDW
ON PRIMARY 
(
    NAME = N'SalesLogisticsDW_Data',
    FILENAME = N'D:C:\Users\Student\Downloads\DAAI_N1.4\warehouse_3nf\db\SalesLogisticsDW.mdf'
)
LOG ON
(
	NAME = N'SalesLogisticsDW_Log',
    FILENAME = N'D:C:\Users\Student\Downloads\DAAI_N1.4\warehouse_3nf\db\SalesLogisticsDW.ldf'
)

USE SalesLogisticsDW


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

USE SalesLogisticsDW;
GO

DECLARE @CsvDir NVARCHAR(500) = N'C:\Users\Student\Downloads\DAAI_N1.4\warehouse_3nf\';
DECLARE @sql NVARCHAR(MAX);

-- 1. geography
SET @sql = N'BULK INSERT geography FROM ''' + @CsvDir + N'geography.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- 2. product
SET @sql = N'BULK INSERT product FROM ''' + @CsvDir + N'product.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- 3. promotion
SET @sql = N'BULK INSERT promotion FROM ''' + @CsvDir + N'promotion.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- 4. sales_employee
SET @sql = N'BULK INSERT sales_employee FROM ''' + @CsvDir + N'sales_employee.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- 5. customer
SET @sql = N'BULK INSERT customer FROM ''' + @CsvDir + N'customer.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- 6. shipper
SET @sql = N'BULK INSERT shipper FROM ''' + @CsvDir + N'shipper.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- 7. [order]
SET @sql = N'BULK INSERT [order] FROM ''' + @CsvDir + N'order.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- 8. order_items
SET @sql = N'BULK INSERT order_items FROM ''' + @CsvDir + N'order_items.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- 9. order_item_promotion
SET @sql = N'BULK INSERT order_item_promotion FROM ''' + @CsvDir + N'order_item_promotion.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- 10. payment
SET @sql = N'BULK INSERT payment FROM ''' + @CsvDir + N'payment.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- 11. shipment
SET @sql = N'BULK INSERT shipment FROM ''' + @CsvDir + N'shipment.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- 12. returns
SET @sql = N'BULK INSERT returns FROM ''' + @CsvDir + N'returns.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- 13. reviews
SET @sql = N'BULK INSERT reviews FROM ''' + @CsvDir + N'reviews.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- 14. inventory
SET @sql = N'BULK INSERT inventory FROM ''' + @CsvDir + N'inventory.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- 15. web_traffic
SET @sql = N'BULK INSERT web_traffic FROM ''' + @CsvDir + N'web_traffic.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- Kiểm tra nhanh
select * from customer

SELECT 'geography' AS table_name, COUNT(*) AS row_count FROM geography
UNION ALL SELECT 'customer', COUNT(*) FROM customer
UNION ALL SELECT 'sales_employee', COUNT(*) FROM sales_employee
UNION ALL SELECT 'product', COUNT(*) FROM product
UNION ALL SELECT 'promotion', COUNT(*) FROM promotion
UNION ALL SELECT 'shipper', COUNT(*) FROM shipper
UNION ALL SELECT 'order', COUNT(*) FROM [order]
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'order_item_promotion', COUNT(*) FROM order_item_promotion
UNION ALL SELECT 'payment', COUNT(*) FROM payment
UNION ALL SELECT 'shipment', COUNT(*) FROM shipment
UNION ALL SELECT 'returns', COUNT(*) FROM returns
UNION ALL SELECT 'reviews', COUNT(*) FROM reviews
UNION ALL SELECT 'inventory', COUNT(*) FROM inventory
UNION ALL SELECT 'web_traffic', COUNT(*) FROM web_traffic;

USE SalesLogisticsDW;
GO

SET XACT_ABORT ON;  -- dừng ngay nếu có lỗi, tránh chạy sót mà không biết

DECLARE @CsvDir NVARCHAR(500) = N'C:\Users\Student\Downloads\DAAI_N1.4\warehouse_3nf\star_schema\';
DECLARE @sql NVARCHAR(MAX);

-- ============ 5 bảng Dim — nạp trước ============

-- Dim_Date
SET @sql = N'BULK INSERT Dim_Date FROM ''' + @CsvDir + N'Dim_Date.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- Dim_Customer
SET @sql = N'BULK INSERT Dim_Customer FROM ''' + @CsvDir + N'Dim_Customer.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- Dim_Employee
SET @sql = N'BULK INSERT Dim_Employee FROM ''' + @CsvDir + N'Dim_Employee.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- Dim_Geography
SET @sql = N'BULK INSERT Dim_Geography FROM ''' + @CsvDir + N'Dim_Geography.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- Dim_Product
SET @sql = N'BULK INSERT Dim_Product FROM ''' + @CsvDir + N'Dim_Product.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- ============ Fact_Sales — nạp sau cùng (phụ thuộc cả 5 bảng Dim ở trên) ============

SET @sql = N'BULK INSERT Fact_Sales FROM ''' + @CsvDir + N'Fact_Sales.csv'' WITH (
    FIRSTROW = 2, FIELDTERMINATOR = '','', ROWTERMINATOR = ''\n'', DATAFILETYPE = ''widechar'', TABLOCK);';
EXEC(@sql);

-- ============ Kiểm tra nhanh ============
SELECT 'Dim_Date' AS table_name, COUNT(*) AS row_count FROM Dim_Date
UNION ALL SELECT 'Dim_Customer', COUNT(*) FROM Dim_Customer
UNION ALL SELECT 'Dim_Employee', COUNT(*) FROM Dim_Employee
UNION ALL SELECT 'Dim_Geography', COUNT(*) FROM Dim_Geography
UNION ALL SELECT 'Dim_Product', COUNT(*) FROM Dim_Product
UNION ALL SELECT 'Fact_Sales', COUNT(*) FROM Fact_Sales;