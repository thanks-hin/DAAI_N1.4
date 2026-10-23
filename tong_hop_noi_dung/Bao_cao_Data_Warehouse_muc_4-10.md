**BÁO CÁO KIẾN TRÚC VÀ ĐƯỜNG ỐNG DỮ LIỆU  
(DATA PIPELINE & DATA WAREHOUSE)**

_Chi tiết các nội dung Kỹ thuật: Từ Mục 4 đến Mục 10  
Hệ thống Bán lẻ & Thương mại Điện tử_

**4\. MÔ TẢ TỔNG QUAN DỮ LIỆU (DATA OVERVIEW)**

Hệ thống dữ liệu tiếp nhận và xử lý 4 tập dữ liệu nguồn (Data Assets) chính phục vụ toàn bộ nhu cầu phân tích vận hành, bán hàng, tồn kho và trải nghiệm khách hàng:

| **Tên bảng** | **Số dòng (Rows)** | **Số cột (Cols)** | **Khoảng thời gian**    | **Tần suất**  | **Tầng lưu trữ** |
| ------------ | ------------------ | ----------------- | ----------------------- | ------------- | ---------------- |
| web_traffic  | 3,652              | 8                 | 01/01/2013 - 31/12/2022 | Hàng ngày     | raw -> silver    |
| inventory    | 60,247             | 25                | 31/07/2012 - 31/12/2022 | Hàng tháng    | raw -> silver    |
| reviews      | 714,653            | 6                 | 10/07/2012 - 20/08/2012 | Batch / Event | raw -> silver    |
| returns      | 35,733             | 7                 | 11/07/2012 - 13/08/2012 | Batch / Event | raw -> silver    |

**Các miền dữ liệu chính (Data Domains):**

- **1\. Tương tác Web (Web Traffic):** web_traffic: Lưu trữ lượt truy cập, người dùng duy nhất, số trang xem, tỷ lệ thoát (bounce rate), thời gian trung bình phiên và nguồn lưu lượng (Organic, Paid Search, Social Media, Email, Referral, Direct).
- **2\. Sản phẩm & Tồn kho (Inventory):** inventory: Quản lý tồn kho đầu/cuối kỳ, lượng nhập, lượng bán, số ngày đứt hàng (stockout_days), ngày cung ứng (days_of_supply), tỷ lệ lấp đầy (fill_rate) và thuộc tính sản phẩm (giá bán, giá vốn COGS, category, segment, size, color).
- **3\. Đánh giá Khách hàng (Reviews):** reviews: Phản hồi khách hàng sau mua bao gồm điểm đánh giá (1-5 sao), tiêu đề nhận xét và liên kết đơn hàng/sản phẩm.
- **4\. Đổi trả hàng (Returns):** returns: Ghi nhận thông tin đổi trả hàng, lý do trả (wrong_size, defective, changed_mind, late_delivery, not_as_described), số lượng và số tiền hoàn trả.

**5\. CÁC VẤN ĐỀ VỀ DỮ LIỆU (DATA QUALITY ISSUES)**

Trong quá trình khảo sát dữ liệu thô (Raw Data Audit), hệ thống phát hiện các vấn đề chất lượng dữ liệu cốt lõi sau:

**5.1. Dữ liệu thiếu (Missing / Null Values)**

- **Bảng Reviews & Returns:** Một số bản ghi thiếu tiêu đề đánh giá hoặc lý do trả hàng chưa được phân loại rõ ràng.
- **Bảng Inventory:** Xuất hiện các trường hợp days_of_supply hoặc sell_through_rate chứa giá trị Inf/NaN do phép chia cho 0 khi units_sold = 0 hoặc stock_on_hand = 0.

**5.2. Định dạng không chuẩn & Chuỗi ký tự nhiễu**

- **Chuẩn hóa chuỗi:** Các cột chuỗi như category, traffic_source chứa khoảng trắng thừa (leading/trailing whitespace) và không đồng nhất về chữ hoa/chữ thường.
- **Kiểu dữ liệu:** Định dạng ngày tháng chưa đồng bộ ISO-8601 giữa các bảng nguồn, cột giá tiền chứa ký tự không số.

**5.3. Giá trị ngoại lệ (Outliers) & Bất thường logic nghiệp vụ**

- **Bảng Web Traffic:** Phát hiện 18 bản ghi (0.49%) có lượt xem trang (page_views) tăng đột biến bất thường (>200,000 views/ngày) do đợt khuyến mãi lớn hoặc lưu lượng bot/crawler.
- **Bảng Inventory:** Tồn tại 6,432 bản ghi (10.68%) stock_on_hand_is_outlier và 7,455 bản ghi (12.37%) days_of_supply_is_outlier do hàng tồn quá lớn nhưng không phát sinh giao dịch bán.

**6\. XỬ LÝ DỮ LIỆU THÔ (RAW TO SILVER TRANSFORMATION)**

Đường ống ETL/ELT thực hiện làm sạch dữ liệu từ Raw Landing Zone sang tầng Silver Cleaned Data theo các bước chuẩn hóa tự động:

- **1\. Khử trùng lặp (Deduplication):** Sử dụng thuật toán ROW_NUMBER() OVER (PARTITION BY business_key ORDER BY updated_at DESC) để loại bỏ các bản ghi trùng lặp.
- **2\. Chuẩn hóa Định dạng:** Ép kiểu chuỗi ngày về chuẩn ISO DATE (YYYY-MM-DD), loại bỏ khoảng trắng thừa TRIM() và chuyển toàn bộ định danh phân loại về LOWER().
- **3\. Xử lý Missing Value:** Sử dụng SAFE_DIVIDE để tính toán tỷ lệ, thay thế Null bằng giá trị mặc định chuẩn ('unknown' cho lý do trả hàng, 3 sao trung tính cho rating thiếu).
- **4\. Đánh dấu Ngoại lệ (Outlier Flagging):** Không loại bỏ (Drop) dữ liệu tài chính/tồn kho thực tế. Thay vào đó, áp dụng thuật toán IQR/Z-Score để thêm các cột cờ cảnh báo (page_views_is_outlier, stock_on_hand_is_outlier, days_of_supply_is_outlier) giúp tầng BI lọc linh hoạt.

**7\. MÔ TẢ MÔ HÌNH DỮ LIỆU ERD (ENTITY-RELATIONSHIP DIAGRAM)**

Tầng Cơ sở dữ liệu Chuẩn hóa (Warehouse 3NF) được thiết kế bao gồm các thực thể quan hệ chặt chẽ:

- **Thực thể dim_customer:** Lưu trữ thông tin khách hàng (customer_id \[PK\], name, email, phone, city, created_at).
- **Thực thể dim_product:** Lưu trữ thông tin sản phẩm (product_id \[PK\], product_name, category_id, segment_id, size, color, price, cogs).
- **Thực thể orders:** Lưu thông tin giao dịch tổng thể (order_id \[PK\], customer_id \[FK\], order_date, status, traffic_source_id).
- **Thực thể order_items:** Chi tiết từng mặt hàng trong đơn (order_id \[FK\], product_id \[FK\], quantity, unit_price, discount_amount).
- **Thực thể returns:** Ghi nhận lượt đổi trả (return_id \[PK\], order_id \[FK\], product_id \[FK\], return_date, return_reason, refund_amount). Quan hệ 1-N với orders.
- **Thực thể reviews:** Ghi nhận phản hồi (review_id \[PK\], order_id \[FK\], product_id \[FK\], rating, review_title, review_date). Quan hệ 1-N với orders.
- **Thực thể inventory_snapshot:** Ảnh chụp tồn kho định kỳ (snapshot_date, product_id \[FK\], stock_on_hand, units_received, units_sold, stockout_days, days_of_supply).

**8\. CHUẨN HÓA DỮ LIỆU 3NF (THIRD NORMAL FORM)**

Nhằm đảm bảo tính toàn vẹn dữ liệu, triệt tiêu sự dư thừa và tránh các dị thường (Insert/Update/Delete Anomalies), dữ liệu thô dạng bảng gộp (Flat Table) được đưa về Dạng chuẩn 3 (3NF):

- **Dạng chuẩn 1 (1NF):** Đảm bảo mọi thuộc tính đều mang giá trị nguyên tố (Atomic), loại bỏ danh sách hoặc chuỗi gộp.
- **Dạng chuẩn 2 (2NF):** Loại bỏ phụ thuộc một phần (Partial Dependency). Tách thông tin sản phẩm cố định ra khỏi bảng biến động tồn kho theo thời gian.
- **Dạng chuẩn 3 (3NF):** Loại bỏ phụ thuộc bắc cầu (Transitive Dependency). Tách các thuộc tính phân loại (category, segment) thành các thực thể danh mục độc lập.

**Minh họa Chuyển đổi Bảng Tồn kho sang 3NF:**

Trước chuẩn hóa (Bảng Flat): Tên sản phẩm, danh mục, giá bán bị lặp lại 60,247 lần, gây lãng phí dung lượng và nguy cơ bất đồng bộ khi cập nhật giá.

Sau chuẩn hóa 3NF: Tách thành 2 bảng riêng biệt:

- **Bảng Chiều:** dim_product(product_id \[PK\], product_name, category, price, cogs) - Chỉ lưu 1 bản ghi duy nhất cho mỗi mã sản phẩm.
- **Bảng Sự kiện:** inventory_snapshot(snapshot_date, product_id \[FK\], stock_on_hand, units_sold, stockout_days) - Chỉ lưu mã sản phẩm và chỉ số biến động theo thời gian.

**9\. THIẾT KẾ MEASURE, METRIC VÀ KPI**

Hệ thống chỉ số đo lường hiệu quả hoạt động kinh doanh được phân tầng rõ ràng từ số đo thô đến KPI chiến lược:

**9.1. Measures (Số đo thô - Basic Aggregations)**

- **Tổng doanh thu gộp:** Gross Revenue = SUM(order_items.quantity \* order_items.unit_price)
- **Tổng tiền hoàn trả:** Total Refund Amount = SUM(returns.refund_amount)
- **Tổng số lượng bán:** Total Units Sold = SUM(inventory_snapshot.units_sold)
- **Tổng lượt truy cập:** Total Traffic Sessions = SUM(web_traffic.sessions)

**9.2. Metrics (Chỉ số tính toán phân tích)**

- **Doanh thu thuần:** Net Revenue = Gross Revenue - Total Refund Amount
- **Giá trị đơn hàng trung bình:** Average Order Value (AOV) = Net Revenue / Total Orders
- **Tỷ lệ trả hàng:** Return Rate = (SUM(return_quantity) / SUM(units_sold)) \* 100%
- **Tỷ lệ chuyển đổi Web:** Conversion Rate = (Total Orders / Total Traffic Sessions) \* 100%
- **Vòng quay hàng tồn kho:** Inventory Turnover = SUM(units_sold) / AVG(stock_on_hand)

**9.3. KPIs (Chỉ số mục tiêu chiến lược)**

- **KPI Doanh thu:** Mục tiêu tăng trưởng doanh thu thuần MoM > 15%.
- **KPI Tồn kho:** Tỷ lệ đứt hàng (Stockout Rate) < 3% và Tỷ lệ tồn kho vượt trần (Overstock Rate) < 10%.
- **KPI Chất lượng dịch vụ:** Tỷ lệ trả hàng &lt; 5%, Điểm đánh giá CSAT trung bình &gt;= 4.2 / 5.0 sao.

**10\. THIẾT KẾ KHO DỮ LIỆU / GOLDEN DATA (STAR SCHEMA)**

Tầng Golden Data Warehouse được tổ chức theo Mô hình Hình sao (Star Schema) tối ưu hóa cho truy vấn OLAP và hiển thị Dashboard BI tốc độ cao:

**10.1. Các Bảng Sự kiện (Fact Tables)**

- **Fact Bán hàng:** Fact_Sales: Chứa các số đo doanh thu, số lượng, giảm giá, giá vốn, lợi nhuận gộp. Kết nối với Dim_Date, Dim_Customer, Dim_Product, Dim_TrafficSource.
- **Fact Tồn kho:** Fact_Inventory_Monthly: Chứa số đo tồn kho đầu/cuối kỳ, lượng nhập, lượng bán, ngày đứt hàng, tỷ lệ lấp đầy. Kết nối với Dim_Date, Dim_Product.
- **Fact Đổi trả:** Fact_Returns: Chứa số lượng trả, số tiền hoàn tiền, lý do trả. Kết nối với Dim_Date, Dim_Product, Dim_Customer.

**10.2. Các Bảng Chiều (Dimension Tables)**

- **Chiều Sản phẩm:** Dim_Product: Khoá thay thế (product_key), product_id, product_name, category, segment, size, color, current_price.
- **Chiều Thời gian:** Dim_Date: Khoá date_key (YYYYMMDD), full_date, day_of_week, month, quarter, year, is_weekend, is_holiday.
- **Chiều Khách hàng:** Dim_Customer: Khoá customer_key, customer_id, gender, age_group, city, customer_segment.
- **Chiều Nguồn Traffic:** Dim_TrafficSource: Khoá traffic_source_key, channel_name, channel_type (Paid/Organic/Direct).

**10.3. Lợi ích của Mô hình Star Schema đối với BI & Analytic Reporting**

- **Tối ưu truy vấn:** Giảm thiểu độ phức tạp của các câu lệnh JOIN, tăng tốc độ truy vấn báo cáo gấp 5-10 lần so với mô hình 3NF.
- **Thao tác linh hoạt:** Hỗ trợ thao tác Drill-down, Slice & Dice mượt mà trên Power BI / Tableau.
- **Nhất quán dữ liệu:** Đảm bảo tính nhất quán của tập chỉ số (Single Source of Truth) cho toàn bộ tổ chức.