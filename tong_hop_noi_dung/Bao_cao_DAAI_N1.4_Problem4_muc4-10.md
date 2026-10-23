Báo cáo dữ liệu DAAI_N1.4 – Problem 4: Đánh giá năng lực thúc đẩy doanh số của nhân viên

Nội dung mục 4–10

Pipeline: Raw → Silver → Warehouse 3NF → Golden (Star Schema) → Dashboard & KPI. Phạm vi: CUSTOMER, ORDER, ORDER_ITEMS, ORDER_ITEM_PROMOTION. Đơn vị tiền giữ nguyên như dữ liệu gốc.

# 4. Mô tả tổng quan dữ liệu

| **Tầng**     | **Bảng / file**      | **Số dòng** | **Số cột** | **Ghi chú**                                                |
| ------------ | -------------------- | ----------- | ---------- | ---------------------------------------------------------- |
| Raw          | customers.csv        | 121.930     | 7          | Đăng ký 17/01/2012 – 31/12/2022                            |
| Raw          | orders_enriched.csv  | 646.945     | 17         | Đơn hàng 04/07/2012 – 31/12/2022; bảng phi chuẩn           |
| Raw          | order_items.csv      | 714.669     | 7          | Có promo_id và promo_id_2                                  |
| Silver = 3NF | CUSTOMER             | 121.930     | 6          | Bỏ city                                                    |
| Silver = 3NF | ORDER                | 646.945     | 9          | Giữ 9/17 cột, gồm comment                                  |
| Silver = 3NF | ORDER_ITEMS          | 714.653     | 5          | Đã gộp 16 cặp khóa trùng                                   |
| Silver = 3NF | ORDER_ITEM_PROMOTION | 276.309     | 3          | 50 mã khuyến mãi; chỉ lưu dòng có khuyến mãi               |
| Golden       | Fact_Sales           | 714.653     | 14         | Grain: 1 dòng hàng (order_id, product_id)                  |
| Golden       | Dim_Customer         | 121.930     | 9          | Đã gộp city, region, district                              |
| Golden       | Dim_Product          | 2.412       | 8          | 1.598 sản phẩm có giao dịch                                |
| Golden       | Dim_Date             | 3.833       | 10         | 04/07/2012 – 31/12/2022                                    |
| Golden       | Dim_Employee         | 200         | 5          | id, tên, years_experience, education_level, marital_status |
| Golden       | Dim_Geography        | 39.948      | 4          | Phủ 100% zip của khách; 29.932 zip có đơn                  |

Nội dung 4 bảng Silver và 3NF **giống hệt nhau** (chỉ khác BOM ở đầu file). Việc tách bảng diễn ra ở bước Raw → Silver.

**Phân nhóm thông tin:**

- Khách hàng: zip, ngày đăng ký, giới tính, nhóm tuổi, kênh thu hút (121.930 khách, 31.491 zip).
- Giao dịch: đơn hàng (trạng thái, thiết bị, nguồn đơn, nhân viên, nhận xét) và dòng hàng (số lượng, đơn giá, chiết khấu). Có 646.945 đơn, 1.598 sản phẩm và 200 nhân viên.
- Khuyến mãi: 50 mã, áp dụng cho 38,7% dòng hàng.
- Nhận xét: cột comment lưu một nhận xét chăm sóc khách hàng cho mỗi đơn, gồm 18 nội dung khác nhau.

**Thông điệp chính:** dữ liệu trải dài 10,5 năm với hơn 640 nghìn đơn; pipeline giữ nguyên số dòng của đơn và khách, chỉ gộp 16 dòng trùng khóa.

# 5. Các vấn đề về dữ liệu (Raw)

Raw sạch về định dạng; vấn đề nằm ở cấu trúc và logic nghiệp vụ.

| **Nhóm**                | **Phát hiện**                                                                                                   | **Số liệu**             |
| ----------------------- | --------------------------------------------------------------------------------------------------------------- | ----------------------- |
| Thiếu dữ liệu           | customers, orders_enriched không có ô trống                                                                     | 0                       |
|                         | promo_id trống (dòng không có khuyến mãi, không phải lỗi)                                                       | 438.353 (61,3%)         |
|                         | promo_id_2 trống                                                                                                | 714.463 (99,97%)        |
| Trùng lặp               | Không có dòng trùng hoàn toàn; không trùng customer_id, order_id                                                | 0                       |
|                         | Trùng khóa (order_id, product_id) với số lượng và giá khác nhau                                                 | 16 cặp (32 dòng)        |
| Định dạng               | Ngày đều yyyy-mm-dd; không dư khoảng trắng; giá trị phân loại nhất quán                                         | 0 lỗi                   |
| Ngoại lệ                | unit_price > 15.324,06 (max 43.056; trung vị 4.257,77)                                                          | 8.623 dòng (1,21%)      |
|                         | discount_amount > 2.419,07 (max 35.235,47)                                                                      | 105.767 dòng            |
| Logic hợp lệ            | Số lượng 1–8; không âm; không giá 0; chiết khấu luôn 0,4%–20% giá trị dòng; không có chiết khấu khi không có mã | 0 vi phạm               |
| **Sai logic nghiệp vụ** | **Đơn có order_date trước signup_date của chính khách**                                                         | **477.453 đơn (73,8%)** |
| Cấu trúc                | promo_id/promo_id_2 là nhóm lặp; city phụ thuộc zip; thuộc tính nhân viên lặp ở mọi đơn                         | xem mục 8               |
| Ghi nhận                | 31.684 khách (26%) chưa có đơn; 200 mã nhân viên có 192 tên khác nhau                                           | hợp lệ                  |

Các ngoại lệ về giá và chiết khấu là đuôi phân phối dài, không phải lỗi nhập liệu.

**Lỗi signup_date:** ở golden, 74,4% dòng hàng (71,1% doanh thu thuần) có ngày đặt trước ngày đăng ký. Tương quan giữa năm đăng ký và năm mua đầu tiên là 0,002. Cột này không dùng để phân tích tuổi đời hay cohort khách hàng. Phân tích doanh thu, AOV, trạng thái đơn và hiệu suất nhân viên **không dùng cột này**; tỷ lệ vi phạm đều giữa các nhân viên (72,1%–76,6%).

# 6. Xử lý dữ liệu thô (Raw → Silver)

Quy trình có hai giai đoạn.

**Giai đoạn 1 – tạo silver_data_raw** (trước 3 notebook):

- Chặn ngoại lệ (capping) kèm cột cờ outlier: unit_price tối đa 15.324,06 (8.623 dòng); discount_amount tối đa 2.419,07 (105.765 dòng).
- Bỏ promo_id_2 vì thiếu hơn 90% dữ liệu (ảnh hưởng 206 dòng, 0,03%). Dòng không có khuyến mãi mang giá trị No_Promo.
- Thêm các cột suy diễn total_price_before/after_discount.

**Giai đoạn 2 – 3 notebook (chuẩn hóa theo lược đồ 3NF):**

| **Bảng**             | **Các bước**                                                                                                                                                                                                            |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CUSTOMER             | Bỏ city (suy ra từ zip); strip chuỗi; ép kiểu int/date; loại dòng trùng hoàn toàn; kiểm tra PK                                                                                                                          |
| ORDER                | Bỏ 8 cột (city, region, district, payment_method, 4 thuộc tính nhân viên); giữ comment; strip; ép kiểu; kiểm tra PK và FK customer_id                                                                                   |
| ORDER_ITEMS          | Gộp theo khóa (order_id, product_id): quantity = tổng, discount = tổng, unit_price = bình quân gia quyền theo quantity; bỏ total_price_\* vì tính lại được (sai lệch chỉ do làm tròn); kiểm tra tổng quantity không đổi |
| ORDER_ITEM_PROMOTION | Lọc No_Promo; loại trùng; kiểm tra PK (order_id, product_id, promo_id) và FK order_id                                                                                                                                   |

**Quy tắc xử lý giá trị thiếu:** CUSTOMER và ORDER không có ô trống nên không có Drop hay Imputation. Ô trống do không có khuyến mãi trở thành «không có dòng» trong ORDER_ITEM_PROMOTION. CUSTOMER và ORDER giữ nguyên 100% dòng và giá trị trên các cột được giữ.

**Tác động của quy trình:**

- Tổng chiết khấu giảm 44% (749,6 triệu → 417,8 triệu); doanh thu thuần tăng 1,4% (15,68 tỷ → 15,91 tỷ).
- Tổng payment_value của bảng payment là 15.680.869.265, bằng doanh thu thuần Raw (15.680.869.265); doanh thu thuần của ORDER_ITEMS cao hơn con số này 224,9 triệu (1,4%).
- Gộp dòng trùng tạo 8 dòng có quantity > 8 (tối đa 15), vượt miền 1–8 của Raw.
- Việc bỏ promo_id_2 làm mất 206 dòng khuyến mãi thứ hai (PROMO-0015: 132; PROMO-0025: 74).

# 7. Mô hình hóa dữ liệu ERD

| **Thực thể**         | **PK**                           | **FK**                                                                      | **Thuộc tính**                                               |
| -------------------- | -------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------ |
| CUSTOMER             | customer_id                      | zip → GEOGRAPHY                                                             | signup_date, gender, age_group, acquisition_channel          |
| ORDER                | order_id                         | customer_id → CUSTOMER; zip → GEOGRAPHY; sales_employee_id → SALES_EMPLOYEE | order_date, order_status, device_type, order_source, comment |
| ORDER_ITEMS          | (order_id, product_id)           | order_id → ORDER; product_id → PRODUCT                                      | quantity, unit_price, discount_amount                        |
| ORDER_ITEM_PROMOTION | (order_id, product_id, promo_id) | (order_id, product_id) → ORDER_ITEMS; promo_id → PROMOTION                  | –                                                            |

**Quan hệ:**

- CUSTOMER 1–N ORDER: mỗi khách có 0 đến 107 đơn (trung bình 7,2 đơn trên khách có mua).
- ORDER 1–N ORDER_ITEMS: mỗi đơn có 1 đến 5 dòng; 89,7% đơn chỉ có 1 dòng.
- ORDER N–N PRODUCT, được giải bằng ORDER_ITEMS.
- ORDER_ITEMS N–N PROMOTION, được giải bằng ORDER_ITEM_PROMOTION. Cấu trúc hỗ trợ nhiều mã trên một dòng hàng; dữ liệu hiện tại có tối đa 1 mã mỗi dòng nên thực tế là 1–(0..1).
- GEOGRAPHY 1–N CUSTOMER và 1–N ORDER; SALES_EMPLOYEE 1–N ORDER.
- ORDER.zip bằng CUSTOMER.zip ở toàn bộ đơn hiện tại và được giữ làm khóa ngoại độc lập (địa chỉ giao hàng của đơn).
- Toàn vẹn tham chiếu: 0 khóa ngoại mồ côi ở các quan hệ order → customer, items → order, promo → items.

# 8. Chuẩn hóa dữ liệu 3NF

| **Dạng chuẩn** | **Vấn đề ở Raw**                                                                                                                                         | **Cách xử lý**                                                                                     |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| 1NF            | promo_id, promo_id_2 là nhóm lặp; 16 khóa (order_id, product_id) trùng                                                                                   | Tách ORDER_ITEM_PROMOTION; gộp dòng trùng để khóa duy nhất                                         |
| 2NF            | Thuộc tính cấp đơn lẫn với cấp dòng hàng                                                                                                                 | Tách ORDER và ORDER_ITEMS; mọi thuộc tính của ORDER_ITEMS phụ thuộc đủ khóa (order_id, product_id) |
| 3NF            | zip → city, region, district (29.932 zip, 0 vi phạm); sales_employee_id → tên, hôn nhân, học vấn, kinh nghiệm (200 mã, 0 vi phạm); customers: zip → city | Tách GEOGRAPHY và SALES_EMPLOYEE; bỏ city khỏi CUSTOMER                                            |

**Dị thường trước chuẩn hóa** (đơn 1 trong orders_enriched: zip 1109, Hanoi, EMP0103, kinh nghiệm 20 năm):

- Cập nhật: đổi thông tin EMP0103 phải sửa 3.200 dòng; đổi city của zip 1109 phải sửa 19 dòng; sót một dòng làm dữ liệu mâu thuẫn.
- Thêm: không thêm được nhân viên hay khu vực mới khi chưa có đơn.
- Xóa: xóa đơn cuối của một nhân viên làm mất thông tin nhân viên đó.

|                     | **Trước (orders_enriched)**                            | **Sau (3NF)**                          |
| ------------------- | ------------------------------------------------------ | -------------------------------------- |
| Số cột của bảng đơn | 17                                                     | 9 (ORDER)                              |
| Thông tin địa lý    | city, region, district lặp ở từng đơn                  | 1 dòng mỗi zip (GEOGRAPHY)             |
| Thông tin nhân viên | 4 thuộc tính lặp ở từng đơn (200 mã, 3.235 đơn mỗi mã) | 1 dòng mỗi nhân viên (SALES_EMPLOYEE)  |
| Khuyến mãi          | 2 cột lặp trong dòng hàng                              | Bảng riêng, chỉ lưu dòng có khuyến mãi |

# 9. Thiết kế Measure, Metric và KPI

Doanh thu thuần = Σ(quantity × unit_price − discount_amount). Doanh số của nhân viên tính trên mọi hóa đơn đã xử lý; **hóa đơn thành công là đơn có trạng thái delivered**. Hóa đơn được đếm bằng COUNT DISTINCT order_id vì Fact_Sales ở cấp dòng hàng (714.653 dòng so với 646.945 đơn).

## 9.1 Measure (số đo thô)

- Doanh thu gộp 16,32 tỷ; tổng chiết khấu 417,8 triệu; doanh thu thuần 15,91 tỷ.
- Doanh thu thuần của đơn delivered: 12,70 tỷ (79,8%).
- Số đơn: 646.945 (delivered 516.716; cancelled 59.462; returned 36.142; shipped 13.773; paid 13.577; created 7.275).
- Số lượng bán; số khách có mua: 90.246.
- Số đánh giá (REVIEWS): 714.653; số đơn hoàn trả (RETURNS): 35.733.

## 9.2 Metric toàn công ty

| **Metric**               | **Công thức**                           | **Giá trị**                                                                 |
| ------------------------ | --------------------------------------- | --------------------------------------------------------------------------- |
| AOV                      | doanh thu thuần / số đơn                | 24.586 (mọi đơn); 24.576 (đơn delivered)                                    |
| Tỷ lệ thành công         | đơn delivered / tổng đơn                | 79,9% (trên đơn đã đóng: 84,4%)                                             |
| Tỷ lệ hủy                | cancelled / tổng đơn                    | 9,19%                                                                       |
| Tỷ lệ hoàn trả           | đơn hoàn trả / tổng đơn                 | 5,52% theo RETURNS; 5,59% theo order_status                                 |
| Điểm rating trung bình   | AVG(rating)                             | 4,19 (theo dòng hàng)                                                       |
| Tỷ lệ mua lại            | khách ≥ 2 đơn / khách có mua            | 75,2%                                                                       |
| Tỷ lệ dòng có khuyến mãi | dòng có promo / tổng dòng               | 38,7%                                                                       |
| YoY                      | (năm này − năm trước) / năm trước       | 2022: +12,1%; 2019: −38,9%; năm 2012 chỉ từ 04/07 nên không làm gốc so sánh |
| MoM                      | (tháng này − tháng trước) / tháng trước | Biến động mạnh (tháng 11/2022: −31,8%)                                      |

## 9.3 Chỉ số theo nhân viên cho 5 problem statement

| **PS** | **Chỉ số**                           | **Công thức**                                                                                                         | **Nguồn**                 |
| ------ | ------------------------------------ | --------------------------------------------------------------------------------------------------------------------- | ------------------------- |
| 1      | Tổng doanh số; số hóa đơn thành công | Σ doanh thu thuần của mọi đơn; COUNT DISTINCT order_id (delivered)                                                    | ORDER, ORDER_ITEMS        |
| 2      | Top / Under performers               | Thứ hạng tổng hợp = tổng 3 hạng (tỷ lệ chuyển đổi, doanh thu trung bình mỗi hóa đơn, tổng doanh số); cờ ngoài dải ±2σ | ORDER, ORDER_ITEMS        |
| 3      | Độ ổn định                           | Hệ số biến thiên (CV) doanh số tháng; tương quan xếp hạng giữa các kỳ                                                 | ORDER, ORDER_ITEMS        |
| 4      | Thái độ phục vụ                      | Điểm rating trung bình; số lượng đánh giá; tỷ lệ đánh giá thấp (rating ≤ 2); tỷ lệ hoàn trả                           | REVIEWS, RETURNS (Silver) |
| 5      | Chuyển đổi và chất lượng             | Tỷ lệ thành công; doanh thu trung bình mỗi hóa đơn; tỷ lệ hủy; tỷ lệ hoàn trả; xếp hạng                               | ORDER, ORDER_ITEMS        |

REVIEWS có 714.653 dòng, mỗi dòng hàng một đánh giá (rating 1–5, trung bình 4,19) và nối với nhân viên qua order_id. RETURNS có 35.733 đơn hoàn trả. Cột comment của ORDER lưu nhận xét chăm sóc khách hàng theo từng đơn.

## 9.4 Kết quả giữa 200 nhân viên

| **Chỉ số**             | **Trung bình** | **Min – Max**               | **Độ lệch chuẩn thực tế** | **Độ lệch chuẩn nếu thuần ngẫu nhiên** |
| ---------------------- | -------------- | --------------------------- | ------------------------- | -------------------------------------- |
| Số đơn xử lý           | 3.235          | 3.084 – 3.414               | 52                        | 57                                     |
| Doanh số mọi đơn       | 79,5 triệu     | 73,4 – 84,8 triệu           | –                         | –                                      |
| Doanh số đơn delivered | 63,5 triệu     | 58,8 – 67,4 triệu (CV 2,5%) | 1,60 triệu                | –                                      |
| Tỷ lệ thành công       | 79,9%          | 78,0% – 81,7%               | 0,69%                     | 0,71%                                  |
| AOV (đơn delivered)    | 24.576         | 23.396 – 25.616             | 435                       | 440                                    |
| Tỷ lệ hủy / hoàn trả   | 9,2% / 5,6%    | 7,8–10,4% / 4,5–6,6%        | –                         | –                                      |
| CV doanh số tháng      | 0,55           | 0,48 – 0,64                 | –                         | –                                      |

Thứ hạng tổng hợp của dashboard xếp **EMP0163** hạng 1. Theo doanh số đơn delivered, nhóm đầu gồm EMP0143 (67,4 triệu; nhiều đơn nhất, 3.414), EMP0163, EMP0140, EMP0058, EMP0131; nhóm thấp nhất gồm EMP0198 (58,8 triệu), EMP0050, EMP0185. Xếp hạng doanh số liên hệ với số đơn (tương quan hạng 0,61) và AOV (0,66) nhiều hơn tỷ lệ thành công (0,28).

**Độ bền của xếp hạng:**

- Khi chia dữ liệu thành tháng chẵn và tháng lẻ, tương quan xếp hạng giữa hai nửa gần 0: tỷ lệ thành công −0,01, AOV −0,03, doanh số −0,11.
- Tương quan xếp hạng doanh số giữa các năm liên tiếp nằm trong khoảng −0,11 đến 0,04.

**Nhân viên ngoài dải ±2σ** (so với trung bình công ty, theo số đơn của từng người):

| **Chỉ số**                                       | **Cao hơn**                                 | **Thấp hơn**                       |
| ------------------------------------------------ | ------------------------------------------- | ---------------------------------- |
| Tỷ lệ thành công (9/200; kỳ vọng ngẫu nhiên ≈ 9) | EMP0093, EMP0118, EMP0124, EMP0133, EMP0163 | EMP0039, EMP0111, EMP0185, EMP0199 |
| AOV (5/200)                                      | EMP0163, EMP0196                            | EMP0016, EMP0050, EMP0094          |

Chỉ EMP0163 vượt dải trên ở cả hai chỉ số. Không nhân viên nào thấp hơn dải ở cả hai chỉ số và không nhân viên nào vượt ±3σ.

**Thuộc tính nhân viên** (trong Dim_Employee) không có liên hệ có ý nghĩa thống kê với hiệu suất (mọi p > 0,05):

| **Thuộc tính**              | **Kiểm định**   | **Kết quả**                                                            |
| --------------------------- | --------------- | ---------------------------------------------------------------------- |
| years_experience (1–20 năm) | Tương quan hạng | Tỷ lệ thành công ρ = −0,10; AOV ρ = 0,10; doanh số ρ = 0,01 (p ≥ 0,15) |
| education_level (4 nhóm)    | ANOVA           | p từ 0,12 đến 0,99                                                     |
| marital_status (2 nhóm)     | t-test          | p từ 0,06 đến 0,88 (thấp nhất: tỷ lệ trả hàng, p = 0,063)              |

## 9.5 KPI và chính sách

**Dải kiểm soát ±2σ** (nhân viên có khoảng 3.235 đơn): tỷ lệ thành công 78,5% – 81,3%; AOV 23.696 – 25.456.

**KPI công ty:** tỷ lệ hủy dưới 8% (hiện 9,19%); tỷ lệ hoàn trả dưới 5% (hiện 5,52%); điểm rating trung bình từ 4,19 trở lên; tăng tỷ trọng doanh thu đơn delivered (hiện 79,8%).

**Chính sách:**

- Khen thưởng áp dụng cho nhân viên vượt dải trên ở ít nhất 2 kỳ liên tiếp. Toàn kỳ hiện chỉ EMP0163 vượt dải trên ở hai chỉ số.
- Đào tạo áp dụng cho nhân viên thấp hơn dải ở ít nhất 2 kỳ, theo chỉ số yếu: tỷ lệ thành công thấp → quy trình chốt đơn và giảm hủy; AOV thấp → tư vấn bán thêm; rating thấp → kỹ năng chăm sóc khách hàng.
- Nhân viên trong dải vận hành bình thường.
- Kinh nghiệm, học vấn và hôn nhân không là tiêu chí phân loại hay phân bổ đào tạo.
- Chênh lệch giữa các nhân viên nằm trong biên dao động ngẫu nhiên; thưởng và phạt không dựa trên xếp hạng của một kỳ.

# 10. Thiết kế kho dữ liệu / Golden data (Star Schema)

**Fact_Sales** (grain: 1 dòng hàng):

- Khóa: order_id, product_id, date_key, customer_id, sales_employee_id, zip.
- Thuộc tính suy biến: order_status.
- Measure: quantity, unit_price, discount_amount, gross_amount, net_amount.
- Khuyến mãi: promo_count, has_promotion (276.309 dòng có khuyến mãi).

**Các bảng chiều:**

| **Bảng**      | **Khóa**          | **Thuộc tính**                                                                       |
| ------------- | ----------------- | ------------------------------------------------------------------------------------ |
| Dim_Customer  | customer_id       | zip, signup_date, gender, age_group, acquisition_channel, city, region, district     |
| Dim_Product   | product_id        | product_name, category, segment, size, color, price, cogs                            |
| Dim_Date      | date_key          | year, quarter, month, month_name, day, day_of_week, day_name, is_weekend, year_month |
| Dim_Employee  | sales_employee_id | name, years_experience, education_level, marital_status                              |
| Dim_Geography | zip               | city, region, district                                                               |

Mô hình dùng khóa tự nhiên; date_key chính là ngày. Kiểm tra: không trùng khóa chính ở cả 6 bảng, 0 khóa ngoại mồ côi, gross_amount và net_amount khớp công thức, tổng doanh thu thuần khớp Silver (15,906 tỷ).

**Lợi ích của Star Schema:**

- Truy vấn OLAP chỉ cần 1 phép JOIN từ Fact đến mỗi chiều, nhanh hơn chuỗi JOIN nhiều tầng của 3NF.
- Drill-down, roll-up và slice theo thời gian, nhân viên, sản phẩm, khu vực thực hiện trực tiếp.
- Dashboard dựng measure và bộ lọc trên mô hình, không phải viết lại logic.
- Bảng chiều nhỏ, dễ hiểu với người dùng nghiệp vụ; Dim_Product có cogs nên tính được biên lợi nhuận.

**Phạm vi của golden hiện tại:**

- device_type và order_source có trong ORDER và không có trong Fact_Sales.
- promo_id không nằm trong Fact_Sales; Fact_Sales có promo_count và has_promotion.
- Dashboard PS4 đọc REVIEWS và RETURNS từ tầng Silver, ngoài golden.

# Hạn chế và giả định

- Giai đoạn 1 chặn giá và chiết khấu; doanh thu thuần của ORDER_ITEMS cao hơn tổng payment_value 224,9 triệu (1,4%).
- promo_id_2 bị bỏ do thiếu hơn 90% dữ liệu (206 dòng).
- signup_date không nhất quán với lịch sử đơn hàng (73,8% đơn) nên không dùng trong KPI.
- Tổng doanh số của dashboard gồm cả đơn hủy, hoàn trả và đang xử lý; 20,2% doanh thu thuần không thuộc đơn delivered.
- review_date chỉ từ 10/07/2012 đến 20/08/2012 và return_date chỉ từ 11/07/2012 đến 13/08/2012 nên không dùng để theo dõi xu hướng PS4 theo thời gian.
- RETURNS ghi 35.733 đơn hoàn trả, order_status ghi 36.142 đơn returned.
- Chênh lệch giữa các nhân viên nằm trong biên dao động ngẫu nhiên; thưởng và phạt theo dõi qua nhiều kỳ.