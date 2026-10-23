# Báo cáo Data Pipeline: Raw → Silver → 3NF → Star Schema

_Phần của bạn (geography, shipments_realistic, orders_enriched), mục 4–10, dựa trên các file CSV, notebook silver_to_3NF (DAAI_N1.4) và lược đồ Luoc_do_quan_he_3NF.docx. Số liệu đo trực tiếp từ 3 file này; thông tin các bảng khác chỉ lấy từ output notebook._

**Pipeline:** Raw → Silver (làm sạch) → warehouse_3nf (15 bảng) → golden_data / star_schema (5 Dim + 1 Fact) → Dashboard & KPI.

## 4. Mô tả tổng quan dữ liệu (Data Overview)

Ba file của bạn gồm 646,945 đơn hàng, 566,067 chuyến giao và 39,948 mã zip, trải dài 2012-07-04 → 2022-12-31 (10,5 năm).

### 4.1 Ba file Raw

| File                    | Số dòng | Số cột | Khoảng thời gian                                  | Grain (1 dòng là gì)  | Vai trò                                             |
| ----------------------- | ------- | ------ | ------------------------------------------------- | --------------------- | --------------------------------------------------- |
| geography.csv           | 39,948  | 4      | không có cột ngày                                 | 1 mã zip              | Bảng tra cứu địa lý                                 |
| orders_enriched.csv     | 646,945 | 17     | 2012-07-04 → 2022-12-31                           | 1 đơn hàng            | Đơn hàng đã gộp địa lý, thanh toán, hồ sơ nhân viên |
| shipments_realistic.csv | 566,067 | 22     | ship 2012-07-04 → 2022-12-29; giao đến 2022-12-31 | 1 chuyến giao (1 đơn) | Sự kiện giao hàng đã gộp hồ sơ shipper và địa lý    |

Ngoài ra geography_1.csv giống hệt geography.csv về nội dung (chỉ khác BOM và ký tự xuống dòng).

### 4.2 Các bảng Silver / 3NF sinh ra từ 3 file

| Bảng           | Nguồn                   | Số dòng                                       | Số cột                           |
| -------------- | ----------------------- | --------------------------------------------- | -------------------------------- |
| GEOGRAPHY      | geography.csv           | 39,948                                        | 4                                |
| ORDER          | orders_enriched.csv     | 646,945                                       | 8                                |
| SALES_EMPLOYEE | orders_enriched.csv     | 200                                           | 5 ở Silver (2 trong lược đồ 3NF) |
| SHIPPER        | shipments_realistic.csv | 80                                            | 16                               |
| SHIPMENT       | shipments_realistic.csv | 59,559 trong shipment_silver (raw có 566,067) | 5                                |

### 4.3 Nhóm thông tin và đặc điểm từng file

| Nhóm               | Nội dung thực tế đo được                                                                                                                                |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Địa lý             | 3 region (East 18,929 zip; Central 14,512; West 6,507), 42 city, 39 district, zip từ 1 đến 99950; đơn hàng dùng 29,932 zip (74,9%)                      |
| Đơn hàng           | 6 trạng thái, 3 loại thiết bị (mobile, desktop, tablet), 6 nguồn đơn, 5 phương thức thanh toán, 90,246 khách, trung bình 7,17 đơn/khách, 168,8 đơn/ngày |
| Nhân viên bán hàng | 200 nhân viên (192 tên khác nhau), kinh nghiệm 1–20 năm, 4 trình độ học vấn, 2 tình trạng hôn nhân                                                      |
| Giao hàng          | 80 shipper thuộc 8 hãng (Ninja Van, J&T Express, Viettel Post, BEST Express, GHTK, GHN, Ahamove, Shopee Express), 3 loại xe, 3 ca làm việc              |

**Điểm nhấn khi thuyết trình:** hệ thống không có bảng cửa hàng. Kênh bán được nhận diện qua order_source và device_type, còn địa bàn qua zip.

## 5. Các vấn đề về dữ liệu (Data Quality Issues)

Ba file sạch về cấu trúc (0 null, 0 dòng trùng, ngày đúng định dạng) nhưng có nhiều lỗi logic nghiệp vụ và thiết kế phẳng cần xử lý.

### 5.1 Thiếu, trùng, định dạng: kết quả kiểm tra

| Kiểm tra             | geography                          | orders_enriched                            | shipments_realistic                                |
| -------------------- | ---------------------------------- | ------------------------------------------ | -------------------------------------------------- |
| Null / thiếu         | 0                                  | 0 (17 cột)                                 | 0 (22 cột)                                         |
| Dòng trùng hoàn toàn | 0                                  | 0                                          | 0                                                  |
| Khóa trùng           | zip: 0                             | order_id: 0                                | order_id: 0; (order_id, shipper_id): 0             |
| Ngày sai định dạng   | không có cột ngày                  | 100% đúng YYYY-MM-DD                       | parse được 100%; ngày giao không nhỏ hơn ngày ship |
| Tham chiếu           | mọi zip của đơn có trong geography | city, region, district khớp geography 100% | mọi order_id có trong ORDER                        |

### 5.2 Lỗi định dạng, ký tự, thiết kế

| Lỗi                                | Bằng chứng                                                                                                                                                      | Mức độ                |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| zip không đồng nhất độ dài         | 38,027 zip có 5 chữ số, 1,833 có 4, 18 có 3, 62 có 2, 8 có 1; lưu kiểu số nên mất số 0 đầu                                                                      | Trung bình            |
| Số điện thoại shipper mất số 0 đầu | Cả 80 số đều đúng 9 chữ số, lưu kiểu số nguyên                                                                                                                  | Trung bình            |
| Nhãn ngôn ngữ không nhất quán      | Nhân viên: "Đã kết hôn", "Đại học"; shipper: "Married", "Bachelor"                                                                                              | Nhẹ                   |
| Nhãn district bị dùng lại          | Mỗi district xuất hiện ở 12–16 thành phố khác nhau; có 534 cặp (city, district)                                                                                 | Cao khi muốn làm khóa |
| Cột nhiễu                          | comment chỉ có 18 câu mẫu lặp trên 646,945 dòng, không liên quan nhân viên cụ thể                                                                               | Nhẹ                   |
| Tên và giới tính không khớp        | Ví dụ "Hoàng Thị Khánh" ghi Male, "Võ Thanh Nam" ghi Female                                                                                                     | Nhẹ                   |
| Thiết kế phẳng, dư thừa            | orders_enriched lặp city/region/district và 4 thuộc tính nhân viên trên mọi đơn; shipments_realistic lặp 16 thuộc tính shipper, mỗi shipper lặp 6,930–7,225 lần | Cao, xử lý ở bước 3NF |
| Mã hóa file                        | BOM (utf-8-sig) và CRLF/LF lẫn lộn                                                                                                                              | Nhẹ                   |

### 5.3 Ngoại lệ và sai logic nghiệp vụ

- **join_date sai logic:** 519,276 / 566,067 dòng (91,7%) có ngày gia nhập shipper muộn hơn ngày giao thật; 38/80 shipper gia nhập sau cả ngày cuối dữ liệu (2022-12-31), muộn nhất 2026-03-17.
- **Vùng của shipper không liên quan vùng giao:** chỉ 34,8% chuyến có region shipper trùng region của đơn (ngẫu nhiên với 3 vùng), và 2,6% trùng city.
- **Chỉ số shipper không phản ánh thực tế:** average_delivery_time (20–75) hầu như không tương quan với thời gian giao thật (hệ số 0,002); rating và delivery_success_rate cũng không tương quan (0,0003). Thời gian giao thật phân bố đều 2–7 ngày.
- **shipping_fee hai cụm:** trung vị 1,73, nhưng 13,4% chuyến có phí trên 10 (p90 = 25,09, tối đa 32). Tỷ lệ này gần như bằng nhau ở mọi hãng, loại xe, vùng (13,3–13,6%) nên không giải thích được bằng nghiệp vụ. Ngoài ra có 805 chuyến phí bằng 0.
- **COD nhưng đã paid:** 2,127 đơn phương thức cod mang trạng thái paid, cần xác nhận quy tắc nghiệp vụ.
- **Thiếu shipment:** 564 đơn delivered, returned, shipped (524 + 29 + 11) không có chuyến giao. Đơn cancelled, created, paid không có chuyến giao (hợp lý).
- **Khoảng trống order_id:** id chạy 1 → 834,397 nhưng chỉ có 646,945 đơn (thiếu 187,452).
- **Silver của shipment bị cắt:** shipment_silver chỉ có 59,559 dòng (10,5%), từ 2012-07-04 đến 2013-06-25, trong khi raw có 566,067 dòng đến 2022-12-29. Cần xác nhận đây là lấy mẫu hay lỗi.
- **Bình thường:** ship_date luôn sau hoặc cùng ngày order_date (trễ 0–3 ngày, trung bình 1,5 ngày); đơn phân bổ đều cho nhân viên (3,084–3,414 đơn mỗi người).

## 6. Xử lý dữ liệu thô (Raw → Silver)

Silver giữ nguyên số dòng của geography và orders vì dữ liệu raw không có null hay trùng; công việc chính là tách cột về đúng thực thể và chuẩn hóa kiểu dữ liệu.

### 6.1 Pipeline theo từng file

| File raw                                   | Bước thực hiện                                                                                                                                                                                                                                   | Kết quả Silver                                               |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------ |
| geography.csv                              | Đọc utf-8-sig; giữ 4 cột; drop_duplicates theo zip                                                                                                                                                                                               | GEOGRAPHY 39,948 dòng (loại 0 dòng)                          |
| orders_enriched.csv                        | Đọc utf-8-sig; giữ 8 cột đơn hàng (order_id, order_date, customer_id, zip, order_status, device_type, order_source, sales_employee_id); bỏ city/region/district, payment_method, comment và 4 cột hồ sơ nhân viên; drop_duplicates theo order_id | ORDER 646,945 dòng, 8 cột                                    |
| orders_enriched.csv (phần nhân viên)       | Lấy sales_employee_id, sales_employee_name, marital_status, education_level, years_experience; drop_duplicates theo sales_employee_id                                                                                                            | SALES_EMPLOYEE 200 dòng (Silver giữ 5 cột)                   |
| shipments_realistic.csv (phần shipper)     | Lấy 16 thuộc tính shipper; drop_duplicates theo shipper_id; bổ sung zip                                                                                                                                                                          | SHIPPER 80 dòng, 16 cột                                      |
| shipments_realistic.csv (phần chuyến giao) | Giữ order_id, shipper_id, ship_date, delivery_date, shipping_fee; drop_duplicates theo (order_id, shipper_id)                                                                                                                                    | SHIPMENT: file shipment_silver có 59,559 dòng (raw: 566,067) |

### 6.2 Thuật toán khử trùng (Deduplication)

\# Quy tắc: khóa nghiệp vụ trước, kiểm tra xung đột sau, không xóa mù  
df = df.drop_duplicates() # 1) trùng toàn dòng  
assert df\["order_id"\].is_unique # 2) khóa chính  
grp = df.groupby("shipper_id")\[attr_cols\].nunique()  
assert (grp.max() == 1).all() # 3) thuộc tính tách ra phải nhất quán  
shipper = df\[\["shipper_id"\] + attr_cols\].drop_duplicates("shipper_id")

Kết quả kiểm tra: mọi thuộc tính shipper (17 cột) và nhân viên (4 cột) chỉ có đúng 1 giá trị cho mỗi id, nên tách bảng không làm mất hay mâu thuẫn dữ liệu.

### 6.3 Chính sách giá trị thiếu

- Raw của 3 file có 0 null nên **không phải Drop hay Imputation** ở bước này.
- Quy tắc áp dụng nếu dữ liệu mới phát sinh null: thiếu khóa chính hoặc khóa ngoại (order_id, zip, shipper_id) thì loại dòng; thiếu cột số (shipping_fee) thì giữ NULL, không điền 0, vì 0 làm sai trung bình; thiếu cột nhãn thì ghi "Unknown".

### 6.4 Quy tắc chuẩn hóa kiểu và chuỗi

- **Ngày:** pd.to_datetime(errors="coerce"), đếm NaT trước khi ghi; lưu dạng YYYY-MM-DD.
- **zip:** lưu varchar và đệm số 0 về đúng 5 ký tự; nếu giữ kiểu số thì ghi rõ lý do.
- **shipper_phone:** lưu varchar, đệm số 0 đầu.
- **Chuỗi:** trim khoảng trắng, thống nhất ngôn ngữ nhãn (Anh hoặc Việt) giữa nhân viên và shipper.
- **Loại nhiễu:** bỏ cột comment (18 câu mẫu lặp lại) và cột trùng payment_method khỏi ORDER.
- **Mã hóa xuất file:** utf-8-sig; nạp DB bằng pandas thay vì BULK INSERT để chịu lỗi quote tốt hơn.

### 6.5 Việc cần quyết định trước khi chốt Silver

- **shipment_silver bị cắt:** nếu không có chủ đích, phải sinh lại SHIPMENT từ toàn bộ 566,067 dòng raw.
- **Gán zip cho shipper:** raw chỉ có city, region, district, nhưng mỗi tổ hợp này ứng với trung bình 87 zip (từ 36 đến 141). Cần ghi rõ cách chọn zip đã dùng cho SHIPPER, vì không có đáp án duy nhất từ dữ liệu.

## 7. Mô hình hóa dữ liệu ERD

Từ 3 file phẳng, ERD có 5 thực thể chính (GEOGRAPHY, SALES_EMPLOYEE, ORDER, SHIPPER, SHIPMENT), nối với CUSTOMER và PAYMENT của các thành viên khác.

### 7.1 Thực thể, khóa chính, khóa ngoại

| Thực thể       | Nguồn               | PK                     | FK                                                                          | Thuộc tính chính                                                                                   |
| -------------- | ------------------- | ---------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| GEOGRAPHY      | geography.csv       | zip                    | không có                                                                    | city, region, district                                                                             |
| SALES_EMPLOYEE | orders_enriched     | sales_employee_id      | không có                                                                    | name (+ marital_status, education_level, years_experience ở Silver)                                |
| ORDER          | orders_enriched     | order_id               | customer_id → CUSTOMER; zip → GEOGRAPHY; sales_employee_id → SALES_EMPLOYEE | order_date, order_status, device_type, order_source                                                |
| SHIPPER        | shipments_realistic | shipper_id             | zip → GEOGRAPHY                                                             | tên, điện thoại, hãng, xe, ca làm, rating, delivery_success_rate, average_delivery_time, join_date |
| SHIPMENT       | shipments_realistic | (order_id, shipper_id) | order_id → ORDER; shipper_id → SHIPPER                                      | ship_date, delivery_date, shipping_fee                                                             |

Thực thể liên quan của nhóm khác: CUSTOMER (PK customer_id, FK zip), PAYMENT (PK và FK order_id → ORDER; giữ payment_method đã bị bỏ khỏi ORDER).

### 7.2 Bản chất quan hệ

| Quan hệ                | Loại                                     | Giải thích và số liệu                                                              |
| ---------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------- |
| GEOGRAPHY – ORDER      | 1–N                                      | 39,948 zip, đơn hàng dùng 29,932 zip                                               |
| GEOGRAPHY – SHIPPER    | 1–N                                      | Mỗi shipper gắn 1 zip; 80 shipper                                                  |
| GEOGRAPHY – CUSTOMER   | 1–N                                      |                                                                                    |
| CUSTOMER – ORDER       | 1–N                                      | 90,246 khách có đơn, trung bình 7,17 đơn/khách                                     |
| SALES_EMPLOYEE – ORDER | 1–N                                      | 200 nhân viên, 3,084–3,414 đơn mỗi người                                           |
| ORDER – PAYMENT        | 1–1                                      | PK của PAYMENT là order_id                                                         |
| ORDER – SHIPMENT       | 1–N theo thiết kế, 1–1 trên dữ liệu thực | Mỗi order_id có tối đa 1 chuyến giao; đơn cancelled, created, paid không có chuyến |
| SHIPPER – SHIPMENT     | 1–N                                      | Mỗi shipper khoảng 6,930–7,225 chuyến (raw)                                        |

Không có quan hệ N–N trong phạm vi 3 file. Quan hệ N–N duy nhất của toàn mô hình là ORDER_ITEMS – PROMOTION, đã được giải quyết bằng bảng nối ORDER_ITEM_PROMOTION (nhóm khác phụ trách).

## 8. Chuẩn hóa dữ liệu 3NF

Cả hai file giao dịch đều ở 1NF nhưng vi phạm 3NF; tách thành 5 bảng loại bỏ toàn bộ phụ thuộc bắc cầu đã kiểm chứng bằng dữ liệu.

### 8.1 Phụ thuộc hàm đã kiểm chứng trên dữ liệu thật

| Phụ thuộc hàm                                           | Kết quả kiểm tra                                         | Hành động                                    |
| ------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------- |
| zip → city, region, district                            | Khớp 100% trên 646,945 đơn                               | Bỏ 3 cột khỏi ORDER, giữ FK zip              |
| sales_employee_id → tên, hôn nhân, học vấn, kinh nghiệm | Mỗi id chỉ có đúng 1 giá trị cho cả 4 thuộc tính         | Tách SALES_EMPLOYEE (200 dòng)               |
| order_id → payment_method                               | Thuộc tính của thanh toán, không phải của đơn            | Chuyển sang PAYMENT                          |
| shipper_id → 16 thuộc tính shipper                      | Mỗi shipper chỉ có đúng 1 giá trị cho cả 17 cột kiểm tra | Tách SHIPPER (80 dòng)                       |
| city, region, district của shipper → zip                | Không duy nhất: mỗi tổ hợp ứng với 36–141 zip            | Lưu thẳng zip trong SHIPPER, không suy ngược |
| district → city                                         | **Sai**: cả 39 district ứng với 12–16 city               | Không tách DISTRICT, giữ GEOGRAPHY phẳng     |
| city → region                                           | **Đúng**: mỗi city chỉ thuộc 1 region (0 ngoại lệ)       | Có thể tách tiếp, xem 8.4                    |

### 8.2 Vi phạm dạng chuẩn của từng file

- **orders_enriched** (khóa order_id): city, region, district phụ thuộc vào zip, và 4 thuộc tính nhân viên phụ thuộc vào sales_employee_id. Cả hai là phụ thuộc bắc cầu, vi phạm 3NF.
- **shipments_realistic** (khóa (order_id, shipper_id)): 16 thuộc tính shipper chỉ phụ thuộc shipper_id, là một phần của khóa, vi phạm 2NF. Thêm city, region, district phụ thuộc vào vị trí của shipper (vi phạm 3NF).

### 8.3 Minh họa trước và sau

|                      | Trước                                              | Sau 3NF                                  |
| -------------------- | -------------------------------------------------- | ---------------------------------------- |
| Địa lý trong đơn     | city, region, district lặp trên 646,945 dòng       | GEOGRAPHY 39,948 dòng; ORDER chỉ giữ zip |
| Hồ sơ nhân viên      | 4 thuộc tính lặp trên 646,945 dòng                 | SALES_EMPLOYEE 200 dòng                  |
| Hồ sơ shipper        | 16 thuộc tính lặp trên 566,067 dòng                | SHIPPER 80 dòng                          |
| Cột trong file chính | orders_enriched 17 cột; shipments_realistic 22 cột | ORDER 8 cột; SHIPMENT 5 cột              |

**Dị thường trong bản phẳng:**

- **Cập nhật:** đổi hãng của 1 shipper phải sửa 6,930–7,225 dòng; đổi trình độ của 1 nhân viên phải sửa khoảng 3,100–3,400 dòng. Sót 1 dòng là dữ liệu mâu thuẫn.
- **Thêm:** không thể thêm shipper mới hoặc nhân viên mới nếu chưa có đơn hoặc chuyến giao.
- **Xóa:** xóa chuyến giao cuối cùng của một shipper (hay đơn cuối của một nhân viên) làm mất luôn hồ sơ của họ.

### 8.4 Điểm cần quyết định

- **city → region là 1–1**, nên zip → city → region vẫn còn phụ thuộc bắc cầu theo đúng định nghĩa 3NF. Phương án chặt chẽ: CITY(city_id, city, region) và GEOGRAPHY(zip, city_id, district). Phương án giữ GEOGRAPHY phẳng vẫn chấp nhận được vì đây là bảng tra cứu tĩnh, ít cập nhật. Notebook hiện chỉ kiểm tra district nên chưa phát hiện điểm này.
- **Lệch lược đồ:** SALES_EMPLOYEE Silver có 5 cột, lược đồ 3NF chỉ có 2 (sales_employee_id, name). Cần thống nhất, đề xuất bổ sung 3 cột còn lại vào lược đồ.

## 9. Thiết kế Measure, Metric và KPI

Bộ chỉ số bám 3 chủ đề của dữ liệu bạn phụ trách: hiệu quả đơn hàng, chất lượng giao hàng và năng lực nhân viên bán hàng, đo theo vùng và thời gian.

### 9.1 Measure (số đo thô)

| Measure          | Công thức                                                                                      | Bảng nguồn |
| ---------------- | ---------------------------------------------------------------------------------------------- | ---------- |
| Order Count      | COUNT(DISTINCT order_id)                                                                       | ORDER      |
| Customer Count   | COUNT(DISTINCT customer_id)                                                                    | ORDER      |
| Orders by Status | COUNT(order_id) nhóm theo order_status                                                         | ORDER      |
| Shipment Count   | COUNT(\*)                                                                                      | SHIPMENT   |
| Shipping Fee     | SUM(shipping_fee)                                                                              | SHIPMENT   |
| Lead Time (ngày) | delivery_date − ship_date                                                                      | SHIPMENT   |
| Net Revenue      | SUM(quantity × unit_price − discount_amount); hiện là 15,905,743,139.85 (đơn vị tiền chưa nêu) | Fact_Sales |
| Units Sold       | SUM(quantity)                                                                                  | Fact_Sales |

### 9.2 Metric (chỉ số phân tích)

| Metric                               | Công thức                                                 | Cắt theo               |
| ------------------------------------ | --------------------------------------------------------- | ---------------------- |
| Delivered Rate                       | Đơn delivered / tổng đơn                                  | Tháng, vùng, nhân viên |
| Cancel Rate, Return Rate             | Đơn cancelled (returned) / tổng đơn                       | Tháng, nguồn đơn       |
| AOV                                  | Net Revenue / Order Count                                 | Tháng, vùng, kênh      |
| MoM, YoY Growth                      | (kỳ này / kỳ trước) − 1 trên Order Count hoặc Net Revenue | Tháng, năm             |
| Orders per Customer                  | Order Count / Customer Count                              | Năm                    |
| Avg Lead Time                        | AVG(delivery_date − ship_date)                            | Hãng, vùng             |
| Order-to-Ship Lag                    | AVG(ship_date − order_date)                               | Tháng                  |
| Avg Shipping Fee, High-fee Share     | AVG(shipping_fee); tỷ lệ chuyến có phí > 10               | Hãng, loại xe          |
| Shipment Coverage                    | Đơn có chuyến giao / đơn delivered + returned + shipped   | Năm                    |
| Successful Order Rate theo nhân viên | Đơn delivered / tổng đơn của nhân viên                    | Nhân viên              |
| Revenue per Employee                 | Net Revenue / nhân viên; xếp hạng                         | Nhân viên              |

### 9.3 KPI (chỉ số trọng yếu)

Baseline lấy từ dữ liệu hiện có. **Mục tiêu là đề xuất của mình**, nhóm cần chốt lại theo bối cảnh nghiệp vụ.

| KPI                                        | Baseline                  | Mục tiêu đề xuất                                   |
| ------------------------------------------ | ------------------------- | -------------------------------------------------- |
| Delivered Rate                             | 79,9% (516,716 / 646,945) | ≥ 85%                                              |
| Cancel Rate                                | 9,2% (59,462 đơn)         | ≤ 7%                                               |
| Return Rate                                | 5,6% (36,142 đơn)         | ≤ 4%                                               |
| Đơn chưa hoàn tất (created, paid, shipped) | 5,3% (34,625 đơn)         | ≤ 3%                                               |
| Avg Lead Time                              | 4,5 ngày (2–7 ngày)       | ≤ 4 ngày                                           |
| Order-to-Ship Lag                          | 1,5 ngày (0–3 ngày)       | ≤ 1 ngày                                           |
| Shipment Coverage                          | 99,9% (thiếu 564 đơn)     | 100%                                               |
| Tỷ lệ chuyến phí cao (> 10)                | 13,4%                     | Làm rõ nguyên nhân trước khi đặt mục tiêu          |
| Khách có ít nhất 1 đơn                     | 74% (90,246 / 121,930)    | ≥ 80%                                              |
| Chênh lệch số đơn giữa nhân viên           | 3,084 – 3,414 đơn/người   | Xếp hạng theo delivered rate và AOV thay vì số đơn |

**Xu hướng:** số đơn mỗi năm đạt đỉnh 82,622 (2015), rơi xuống 41,601 năm 2019 (từ 69,510 năm 2018) và thấp nhất 34,525 năm 2021; năm 2012 chỉ có nửa năm. Mục tiêu tăng trưởng nên đặt theo YoY dương từ năm 2022 (36,004 đơn).

## 10. Thiết kế kho dữ liệu Golden Data (Star Schema)

Notebook đã xuất 1 Fact và 5 Dim; phần giao hàng của bạn chưa có Fact riêng nên đề xuất thêm Fact_Shipment và Dim_Shipper.

### 10.1 Hiện trạng đã xuất (star_schema/)

| Bảng          | Loại                           | Số dòng | Ghi chú liên quan đến 3 file                                                    |
| ------------- | ------------------------------ | ------- | ------------------------------------------------------------------------------- |
| Fact_Sales    | Fact, grain 1 dòng ORDER_ITEMS | 714,653 | Gắn order_date, customer_id, sales_employee_id, zip, order_status từ ORDER      |
| Dim_Date      | Dim                            | 3,833   | 2012-07-04 → 2022-12-31; year, quarter, month, day_name, is_weekend, year_month |
| Dim_Geography | Dim                            | 39,948  | zip, city, region, district từ GEOGRAPHY                                        |
| Dim_Employee  | Dim                            | 200     | Hiện chỉ có sales_employee_id, name                                             |
| Dim_Customer  | Dim                            | 121,930 | Đã gộp city, region, district                                                   |
| Dim_Product   | Dim                            | 2,412   | Nhóm khác phụ trách                                                             |

Kiểm tra toàn vẹn: 0 dòng Fact_Sales có khóa ngoại không khớp bất kỳ Dim nào.

### 10.2 Đề xuất bổ sung cho phần giao hàng và nhân viên

| Bảng đề xuất                | Grain                  | Nội dung                                                                                                                                                            |
| --------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Fact_Shipment               | 1 chuyến giao (1 đơn)  | Measure: shipping_fee, lead_time_days, order_to_ship_days. FK: order_id, shipper_key, order_date_key, ship_date_key, delivery_date_key, geography_key, employee_key |
| Dim_Shipper                 | 1 shipper (80 dòng)    | Tên, hãng, loại xe, ca làm, rating, delivery_success_rate, zip, region                                                                                              |
| Dim_Employee (mở rộng)      | 1 nhân viên (200 dòng) | Thêm marital_status, education_level, years_experience để phân tích theo nhóm kinh nghiệm                                                                           |
| Dim_Order_Status (tùy chọn) | 6 giá trị              | order_status, device_type, order_source gộp thành chiều đơn hàng nhỏ (junk dimension)                                                                               |

Dim_Date dùng 3 vai trò (role-playing): ngày đặt, ngày ship, ngày giao. Dim_Geography dùng chung cho đơn hàng và shipper.

### 10.3 Việc nên làm khi dựng Golden Data

- Dùng **surrogate key** số nguyên cho Dim và date_key dạng YYYYMMDD thay cho kiểu ngày.
- Đệm zip về 5 ký tự trước khi nối Fact với Dim_Geography.
- Chỉ dựng Fact_Shipment sau khi shipment Silver được xử lý đủ 566,067 dòng; nếu dùng 59,559 dòng, mọi KPI giao hàng chỉ phủ 2012-07 → 2013-06.
- Không dùng join_date, average_delivery_time, delivery_success_rate của shipper để kết luận hiệu suất, vì dữ liệu không nhất quán với thực tế (mục 5.3).

### 10.4 Lợi ích của Star Schema

- **Truy vấn OLAP nhanh:** chỉ cần 1 mức JOIN từ Fact tới Dim, thay vì nối chuỗi ORDER, GEOGRAPHY, SALES_EMPLOYEE, SHIPMENT, SHIPPER như ở 3NF.
- **Dashboard dễ dựng:** Dim denormalized (Dim_Customer có sẵn city, region) cho phép lọc, nhóm, drill-down từ vùng xuống thành phố trực tiếp trong Power BI hoặc Tableau.
- **Đo lường tách khỏi ngữ cảnh:** Fact chỉ chứa số đo và khóa; thêm chiều phân tích mới không phải sửa Fact.
- **Chỉ số nhất quán:** Delivered Rate, AOV, Lead Time định nghĩa một lần trên Fact, mọi báo cáo dùng chung.
- **Hiệu năng:** Fact dài nhưng hẹp (14 cột), Dim ngắn; phù hợp lưu trữ cột và bảng tổng hợp sẵn.