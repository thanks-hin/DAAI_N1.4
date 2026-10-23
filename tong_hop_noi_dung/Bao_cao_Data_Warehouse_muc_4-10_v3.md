**BÁO CÁO PHÂN TÍCH VÀ THIẾT KẾ KHO DỮ LIỆU**

Phạm vi: PAYMENT, PRODUCT, PROMOTION, SHIPMENT (Mục 4 – 10)

_Pipeline: Raw → Silver → Warehouse 3NF → Golden Data (Star Schema) → Dashboard & KPI_

## Phạm vi và lưu ý về nguồn số liệu

- **Phạm vi:** nhóm phụ trách 4 bảng **PAYMENT, PRODUCT, PROMOTION, SHIPMENT** (kèm SHIPPER tách ra từ shipments). Các bảng còn lại do thành viên khác phụ trách, báo cáo chỉ nhắc khi liên quan trực tiếp (khóa ngoại, đối chiếu chéo).
- Số liệu của 4 bảng được tính trực tiếp từ 8 file CSV (Raw và Silver) và file lược đồ Luoc_do_quan_he_3NF.docx. Số liệu của SHIPPER và các bảng liên quan (GEOGRAPHY, ORDER, ORDER_ITEMS, ORDER_ITEM_PROMOTION) lấy từ output đã lưu trong notebook.
- Chưa có code xử lý Raw → Silver của PAYMENT, PRODUCT, PROMOTION, nên mục 6 mô tả thay đổi quan sát được giữa file Raw và Silver. Phần quy trình theo code chỉ có cho SHIPPER.
- Các mục tiêu KPI (X, Y, Z, 80%...) là ngưỡng gợi ý, nhóm cần tự chốt.

# 4. Mô tả tổng quan dữ liệu

## 4.1. Thống kê Raw và Silver

| **Tầng** | **File**                | **Số dòng** | **Số cột** | **Khoảng thời gian**                   |
| -------- | ----------------------- | ----------- | ---------- | -------------------------------------- |
| Raw      | payments.csv            | 646,945     | 4          | Không có cột ngày (order_id 1–834,397) |
| Raw      | products.csv            | 2,412       | 8          | Không có cột ngày                      |
| Raw      | promotions.csv          | 50          | 10         | 2013-01-31 → 2022-12-31                |
| Raw      | shipments_realistic.csv | 566,067     | 22         | ship_date 2012-07-04 → 2022-12-29      |
| Silver   | payment_silver.csv      | 646,945     | 4          | Như Raw                                |
| Silver   | product_silver.csv      | 2,412       | 8          | Như Raw                                |
| Silver   | promotion_silver.csv    | 50          | 10         | Như Raw                                |
| Silver   | shipment_silver.csv     | 59,559      | 5          | ship_date 2012-07-04 → 2013-06-19      |

- Toàn bộ dữ liệu giao dịch trải khoảng **10,5 năm (07/2012 – 12/2022)**.
- Số đơn giao mỗi năm tăng từ 2013, đạt khoảng 72 nghìn đơn/năm (2015–2016), rồi giảm còn khoảng 30 nghìn đơn/năm (2020–2022).

**Lưu ý:** shipment_silver.csv chỉ có 59,559 / 566,067 dòng (10,5%), tức order_id 1–87,576. Khi thuyết trình cần nói rõ đây là tập con, hoặc nạp Silver đầy đủ.

## 4.2. Bảng tách ra từ shipments và các bảng liên quan

| **Bảng Silver** | **Nguồn đầu vào**       | **Dòng vào** | **Cột vào** | **Dòng ra** | **Cột ra** | **Ghi chú**                |
| --------------- | ----------------------- | ------------ | ----------- | ----------- | ---------- | -------------------------- |
| SHIPPER         | shipments_realistic.csv | 566,067      | 22          | 80          | 16         | Gộp theo shipper, thêm zip |

Các bảng sau do thành viên khác phụ trách, chỉ nêu vì liên quan trực tiếp đến 4 bảng của nhóm:

| **Bảng**             | **Số dòng** | **Liên quan đến**                 | **Ghi chú**                                             |
| -------------------- | ----------- | --------------------------------- | ------------------------------------------------------- |
| ORDER                | 646,945     | PAYMENT, SHIPMENT (khóa order_id) | Số dòng bằng PAYMENT. order_status có 6 giá trị         |
| ORDER_ITEMS          | 714,653     | PRODUCT (khóa product_id)         | Gộp 16 cặp khóa trùng từ 714,669 dòng                   |
| ORDER_ITEM_PROMOTION | 276,309     | PROMOTION (khóa promo_id)         | 38,7% dòng hàng có khuyến mãi, tối đa 1 khuyến mãi/dòng |
| GEOGRAPHY            | 39,948      | SHIPPER (khóa zip)                | zip duy nhất, 0 NULL                                    |

## 4.3. Phân nhóm thông tin

| **Nhóm**      | **Bảng (3NF)**                                                                         | **Nguồn hiện có**   | **Đặc điểm nổi bật**                                                                                       |
| ------------- | -------------------------------------------------------------------------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------- |
| Sản phẩm      | PRODUCT                                                                                | products            | 2,412 SKU, 4 category, 8 segment, 4 size, 10 màu, 14 thương hiệu (tiền tố tên)                             |
| Khuyến mãi    | PROMOTION                                                                              | promotions          | 50 chương trình (45 giảm theo %, 5 giảm cố định). Theo ORDER_ITEM_PROMOTION, 38,7% dòng hàng có khuyến mãi |
| Thanh toán    | PAYMENT                                                                                | payments            | 646,945 giao dịch, giá trị TB 24,238. 5 phương thức, trả góp 1/2/3/6/12 kỳ                                 |
| Vận chuyển    | SHIPMENT, SHIPPER                                                                      | shipments           | 80 shipper, 8 hãng, 34 thành phố, 3 vùng                                                                   |
| Các nhóm khác | CUSTOMER, ORDER, ORDER_ITEMS, SALES_EMPLOYEE, RETURNS, REVIEWS, INVENTORY, WEB_TRAFFIC | nhóm khác phụ trách | Không thuộc phạm vi báo cáo này                                                                            |

**Về Dim_Store:** hệ thống không có bảng cửa hàng. Kênh được thể hiện qua order_source và promo_channel (online, in_store, email, social_media...), nên thay Dim_Store bằng chiều kênh bán (trong Dim_Order_Profile).

# 5. Các vấn đề về dữ liệu (Raw)

Về cấu trúc, Raw khá sạch: không có dòng trùng, không có khóa trùng, ngày đều đúng định dạng. Phần lớn lỗi là lỗi **logic nghiệp vụ**.

| **Nhóm lỗi**              | **File**                           | **Phát hiện cụ thể**                                                                                                                                                                                                                                                        | **Mức độ**                                          |
| ------------------------- | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| Thiếu dữ liệu             | promotions                         | applicable_category NULL **40/50 dòng (80%)**. Các cột và file khác có 0 NULL                                                                                                                                                                                               | Trung bình (NULL mang nghĩa "áp dụng mọi category") |
| Trùng lặp                 | Cả 4 file                          | 0 dòng trùng hoàn toàn, 0 khóa trùng (order_id, product_id, promo_id)                                                                                                                                                                                                       | Không có                                            |
| Trùng nghiệp vụ           | products                           | **240 sản phẩm** trùng bộ (product_name, size, color) nhưng khác product_id và giá chênh rất lớn. Ví dụ LotusWear UE-01 / S / red có giá 12,596.85 và 34.04                                                                                                                 | Cao                                                 |
| Định dạng ngày            | promotions, shipments              | Ngày lưu dạng chuỗi YYYY-MM-DD, parse đúng 100%. Cần ép về kiểu DATE                                                                                                                                                                                                        | Thấp                                                |
| Ký tự / chính tả          | shipments                          | Không có khoảng trắng thừa, không lệch hoa/thường. shipper_phone lưu số nguyên 9 chữ số nên **mất số 0 đầu**                                                                                                                                                                | Thấp                                                |
| Ngoại lệ giá              | products                           | **659 SP (27,3%) giá < 500** (trung vị ~33) so với 1,753 SP còn lại (trung vị 5,607). Hai quần thể lệch nhau cỡ 170 lần, nghi sai thang đo                                                                                                                                  | Cao                                                 |
| Ngoại lệ phí ship         | shipments                          | **76,050 dòng (13,4%)** phí từ 14,29 đến 32, trong khi trung vị 1,73. Có **805 dòng phí = 0**                                                                                                                                                                               | Cao                                                 |
| Sai logic thời gian       | shipments                          | join_date của shipper **sau** ship_date ở **519,276 dòng (91,7%)**. join_date lên tới 2026-03-17, trong khi dữ liệu kết thúc năm 2022                                                                                                                                       | Cao                                                 |
| Đơn vị không rõ           | shipments                          | average_delivery_time từ 20 đến 75, không rõ đơn vị. Số ngày giao thực tế chỉ 2–7 ngày                                                                                                                                                                                      | Trung bình                                          |
| Mâu thuẫn tên - giới tính | shipments                          | 35,563 / 106,736 dòng có tên đệm "Thị" nhưng giới tính Male (heuristic)                                                                                                                                                                                                     | Thấp                                                |
| Giá trị hiếm              | payments                           | installments = 2 chỉ **1,094 dòng (0,17%)**, trong khi 1/3/6/12 phổ biến. COD luôn có 1 kỳ (hợp lý)                                                                                                                                                                         | Thấp                                                |
| Phân phối lệch            | payments                           | 30,219 dòng (4,7%) vượt ngưỡng IQR (72,744), max 331,570. Có thể là đơn lớn thật, nên gắn cờ chứ không xóa                                                                                                                                                                  | Thấp                                                |
| Giá trị giữ chỗ thay NULL | order_items (liên quan promotions) | promo_id = 'No_Promo' ở **61,3%** dòng hàng. Cột có 51 giá trị (50 chương trình + No_Promo). Cần loại giá trị này khi nối với PROMOTION                                                                                                                                     | Thấp                                                |
| Địa lý mơ hồ              | shipments → geography              | **80/80 shipper** có nhiều hơn 1 zip khớp với (city, region, district). Notebook chọn zip nhỏ nhất, nên zip của SHIPPER là **suy đoán**                                                                                                                                     | Cao                                                 |
| Mất khớp giữa bảng        | payments ↔ shipments               | 80,878 đơn có thanh toán nhưng không có giao hàng (12,5%). ORDER có 646,945 dòng, bằng số dòng PAYMENT, và order_status gồm cancelled, created, paid, returned, shipped, delivered, nên nhiều khả năng đây là đơn hủy hoặc chưa giao. Cần đếm theo order_status để xác nhận | Cần xác nhận                                        |

Các kiểm tra sau đều **đạt**: không có giá, giá vốn hoặc số tiền thanh toán ≤ 0; cogs < price ở mọi sản phẩm; delivery_date ≥ ship_date ở mọi dòng; end_date ≥ start_date ở mọi khuyến mãi. Bảng liên quan GEOGRAPHY có 0 NULL và zip duy nhất.

# 6. Xử lý dữ liệu thô (Raw → Silver)

## 6.1. Những gì thực sự khác nhau giữa Raw và Silver

| **File**   | **Thay đổi quan sát được**                                                                                                                           |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| payments   | Không đổi (nội dung giống hệt)                                                                                                                       |
| products   | Chỉ sắp xếp lại theo product_id                                                                                                                      |
| promotions | applicable_category NULL → 'all categories' (40 dòng)                                                                                                |
| shipments  | 22 cột → 5 cột (order_id, shipper_id, ship_date, delivery_date, shipping_fee). Thuộc tính shipper tách sang bảng SHIPPER. Dòng giảm 566,067 → 59,559 |

## 6.2. Luồng thư mục và tầng dữ liệu

- silver_data_raw/\*\_silver.csv (Silver phẳng, đã có cờ outlier) hoặc file gốc → **notebook từng bảng** → silver_data/ (bảng Silver theo hình dạng 3NF) và reports/ (log từng bảng, các file \_rejected_\*).
- Sau đó notebook silver_to_3NF đọc silver_data/, xuất 15 bảng vào warehouse_3nf/ và star schema vào warehouse_3nf/star_schema/.

## 6.3. Quy trình làm sạch (theo code notebook SHIPPER)

<div class="joplin-table-wrapper"><table><thead><tr><th><p><strong>Bước</strong></p></th><th><p><strong>Quy tắc</strong></p></th><th><p><strong>Kết quả thực tế</strong></p></th></tr></thead><tbody><tr><td><p>1. Profiling</p></td><td><p>In shape, số ô thiếu, số dòng trùng, kiểu dữ liệu, miền giá trị các cột phân loại, định dạng ngày và ID</p></td><td><p>Mọi bảng đều được khảo sát trước khi xử lý</p></td></tr><tr><td><p>2. Xử lý thiếu</p></td><td><p><strong>Không tự sinh khóa.</strong> Dòng thiếu khóa chính được cô lập vào reports/_rejected_*.csv. Cột số bị thiếu thì <strong>điền trung vị (median)</strong>: shipper_rating, shipper_age</p></td><td><p>0 dòng thiếu, bước điền chưa phải chạy</p></td></tr><tr><td><p>3. Quy tắc miền giá trị</p></td><td><p>Rating trong [0, 5], tuổi shipper trong [18, 70]. Vi phạm thì cô lập ra file riêng, đặt NaN rồi điền median</p></td><td><p>0 vi phạm</p></td></tr><tr><td><p>4a. Khử trùng: thực thể lặp</p></td><td><p>SHIPPER (566,067 → 80 dòng): kiểm tra <strong>hằng định</strong> bằng groupby().nunique(). Nếu một thuộc tính đổi giá trị theo dòng thì <strong>dừng pipeline bằng `raise`</strong>. Nếu đạt thì drop_duplicates(subset=shipper_id)</p></td><td><p>0 vi phạm hằng định</p></td></tr><tr><td><p>4c. Khử trùng: dòng trùng hoàn toàn</p></td><td><pre><code>drop_duplicates()</code></pre></td><td><p>0 dòng bị xóa</p></td></tr><tr><td><p>5. Chuẩn hóa kiểu và chuỗi</p></td><td><p>strip khoảng trắng; ID và số điện thoại dạng chuỗi; zip kiểu Int64; join_date về kiểu date; số nguyên Int64</p></td><td><p>Không phát sinh lỗi parse</p></td></tr><tr><td><p>8. Ánh xạ khóa ngoại</p></td><td><p>SHIPPER: quy đổi (city, region, district) → zip bằng cách chọn zip nhỏ nhất khớp, ghi shipper_zip_assignment_log.csv</p></td><td><p>80/80 shipper có nhiều zip khớp, nên zip là suy đoán</p></td></tr><tr><td><p>9. Kiểm tra ràng buộc</p></td><td><p>assert PK duy nhất và không NULL, FK zip không mồ côi, rating và tuổi hợp lệ, join_date parse được. Ghi file log vào reports/</p></td><td><p>Tất cả đạt, 0 FK mồ côi</p></td></tr></tbody></table></div>

**Cần nói thẳng khi thuyết trình:** (1) Quy trình theo code ở trên chỉ có cho SHIPPER. Với PAYMENT, PRODUCT, PROMOTION chưa có code, nên mục 6.1 chỉ mô tả thay đổi quan sát được: payments giữ nguyên, products chỉ sắp xếp lại, promotions điền applicable_category. (2) Các lỗi logic ở mục 5 **chưa được xử lý trong Silver**: thang giá sản phẩm, phí ship bất thường, join_date sau ngày giao, 240 SP trùng nghiệp vụ, số điện thoại mất số 0 đầu (notebook SHIPPER chỉ đổi sang chuỗi). Hãy trình bày chúng là "đã phát hiện, gắn cờ, đề xuất xử lý". (3) Các bước xử lý thiếu và miền giá trị chưa kích hoạt vì dữ liệu không có lỗi, nên nói là "đã thiết kế sẵn".

# 7. Mô hình hóa dữ liệu ERD

## 7.1. Thực thể, khóa chính, khóa ngoại

Chỉ liệt kê thực thể liên quan trực tiếp đến 4 bảng của nhóm. ORDER, ORDER_ITEMS, ORDER_ITEM_PROMOTION do nhóm khác phụ trách.

| **Thực thể**         | **Khóa chính (PK)**              | **Khóa ngoại (FK)**                 |
| -------------------- | -------------------------------- | ----------------------------------- |
| GEOGRAPHY            | zip                              |                                     |
| SHIPPER              | shipper_id                       | zip                                 |
| PRODUCT              | product_id                       |                                     |
| PROMOTION            | promo_id                         |                                     |
| ORDER                | order_id                         | customer_id, zip, sales_employee_id |
| ORDER_ITEMS          | (order_id, product_id)           | order_id, product_id                |
| ORDER_ITEM_PROMOTION | (order_id, product_id, promo_id) | (order_id, product_id), promo_id    |
| SHIPMENT             | (order_id, shipper_id)           | order_id, shipper_id                |
| PAYMENT              | order_id                         | order_id                            |

## 7.2. Bản chất quan hệ

| **Quan hệ**                            | **Loại**        | **Giải thích**                                                                                            |
| -------------------------------------- | --------------- | --------------------------------------------------------------------------------------------------------- |
| GEOGRAPHY → CUSTOMER / SHIPPER / ORDER | 1-N             | Một zip có nhiều khách, shipper, đơn                                                                      |
| ORDER ↔ PRODUCT                        | N-N             | Giải bằng ORDER_ITEMS                                                                                     |
| ORDER_ITEMS ↔ PROMOTION                | N-N             | Giải bằng ORDER_ITEM_PROMOTION (một dòng hàng có thể áp nhiều khuyến mãi)                                 |
| ORDER ↔ SHIPPER                        | N-N (lý thuyết) | Giải bằng SHIPMENT. **Dữ liệu thực tế: mỗi đơn đúng 1 shipper** (order_id không trùng trong 566,067 dòng) |
| ORDER → PAYMENT                        | 1-1             | order_id không trùng trong 646,945 dòng, là PK của PAYMENT                                                |
| SHIPPER → SHIPMENT                     | 1-N             | Trung bình ~7,076 đơn/shipper                                                                             |

**Nơi nạp dữ liệu:** notebook nạp vào SQL Server, database SalesLogisticsDW, qua pyodbc và sqlalchemy.

# 8. Chuẩn hóa dữ liệu 3NF

## 8.1. Từ cấu trúc thô đến 3NF

| **Dạng chuẩn** | **Vi phạm**                                                                                                                                                         | **Cách xử lý**                                                                                         |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 1NF            | Liên quan PROMOTION: lược đồ gốc có promo_id, promo_id_2 (nhóm lặp) trong ORDER_ITEMS. **Dữ liệu thực tế chỉ có 1 cột \`promo_id\`**, tối đa 1 khuyến mãi/dòng hàng | Tách ORDER_ITEM_PROMOTION (nhóm khác xử lý, 276,309 dòng). Cấu trúc vẫn cho phép nhiều khuyến mãi/dòng |
| 2NF            | SHIPMENT có PK ghép (order_id, shipper_id) nhưng order_id đã duy nhất, nên ship_date, delivery_date, shipping_fee chỉ phụ thuộc một phần của khóa                   | Đặt PK = order_id, shipper_id là FK (xem 8.4)                                                          |
| 3NF            | Phụ thuộc bắc cầu shipper_id → zip → city/region/district (SHIPPER). Ngoài ra payment_method bị trùng ở ORDER và PAYMENT                                            | Chuyển sang GEOGRAPHY qua FK zip. Bỏ payment_method khỏi ORDER, chỉ giữ ở PAYMENT                      |

## 8.2. Minh họa trước và sau (từ shipments_realistic.csv)

**Trước:** 1 bảng 22 cột × 566,067 dòng. Cả 16 thuộc tính shipper phụ thuộc hoàn toàn vào shipper_id (đã kiểm chứng: mỗi shipper_id chỉ có đúng 1 giá trị cho mọi cột). Chỉ có 80 shipper nhưng thông tin bị lặp trung bình **~7,076 lần** mỗi người.

| **shipper_id** | **order_id**          | **ship_date** | **shipping_fee** | **shipper_company** | **rating** | **city**            | **region** |
| -------------- | --------------------- | ------------- | ---------------- | ------------------- | ---------- | ------------------- | ---------- |
| SHP00001       | 1                     | 2012-07-07    | 1.37             | Viettel Post        | 5.0        | Phan Rang-Thap Cham | Central    |
| SHP00001       | (hàng nghìn đơn khác) | ...           | ...              | Viettel Post        | 5.0        | Phan Rang-Thap Cham | Central    |

**Sau:**

| **Bảng**  | **Nội dung**                                                 | **Quy mô**   |
| --------- | ------------------------------------------------------------ | ------------ |
| SHIPMENT  | order_id, shipper_id, ship_date, delivery_date, shipping_fee | 5 cột        |
| SHIPPER   | shipper_id + 14 thuộc tính + zip                             | 80 dòng      |
| GEOGRAPHY | zip, city, region, district                                  | bảng tra cứu |

**Dị thường được loại bỏ:**

- **Sửa:** đổi shipper_rating của một shipper phải cập nhật ~7,000 dòng, sót một dòng là dữ liệu mâu thuẫn. Sau chuẩn hóa chỉ sửa 1 dòng.
- **Thêm:** shipper mới chưa có đơn thì không thể lưu (vì khóa là order_id). Sau chuẩn hóa thì lưu được.
- **Xóa:** xóa đơn hàng cuối cùng của một shipper làm mất luôn thông tin shipper đó. Sau chuẩn hóa thì không.

## 8.3. Dữ liệu trả lời hai điểm "cần xác nhận" của lược đồ 3NF

| **Điểm cần xác nhận**                                     | **Kết quả kiểm tra**                                                                                                                             | **Kết luận**                                                                                                                     |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| **PRODUCT:** category có quyết định segment không?        | **Không.** Streetwear có 4 segment, Casual có 2, Outdoor có 2, GenZ có 1. Segment "Activewear" xuất hiện ở cả Casual và Outdoor                  | **Giữ nguyên PRODUCT**, không tách CATEGORY                                                                                      |
| **GEOGRAPHY:** district → city → region có một-một không? | city → region **đúng** (34 thành phố → 3 vùng, không ngoại lệ). district → city **sai**: nhãn "District #k" ứng với tối đa 5 thành phố khác nhau | Tách **CITY(city, region)** là hợp lý. district **không** lồng trong city nên giữ làm thuộc tính riêng, không tách bảng DISTRICT |
| **SHIPPER:** zip có xác định duy nhất không?              | 80/80 shipper có nhiều zip khớp với (city, region, district); notebook chọn zip nhỏ nhất                                                         | zip của SHIPPER là suy đoán, nên chỉ phân tích shipper theo city hoặc region                                                     |

Giới hạn: kiểm tra district → city và city → region mới chạy trên dữ liệu địa lý của shipper (80 dòng). Cần chạy lại trên geography.csv (39,948 zip) khi có file.

## 8.4. Cài đặt trong notebook silver_to_3NF

- Notebook đọc silver_data/, xuất **15 bảng 3NF** vào warehouse_3nf/ (cộng thêm region, city, district hoặc category nếu điều kiện tách thỏa).
- Hai quyết định tách bảng (GEOGRAPHY, PRODUCT) được **tự động kiểm tra bằng dữ liệu** bằng groupby().nunique(), không tách cứng theo giả định.
- Với PRODUCT, category → segment bị vi phạm ở 3 trong 4 category, nên notebook giữ product phẳng, khớp kết quả ở mục 8.3.
- Với GEOGRAPHY, kiểm tra của notebook chỉ có hai kết cục: tách đủ 4 bảng hoặc giữ phẳng. Nếu district → city bị vi phạm (rất có thể, theo dữ liệu shipper) thì bảng giữ phẳng và **vẫn còn phụ thuộc bắc cầu \`zip → city → region\`**. Có thể thêm nhánh chỉ tách CITY, hoặc ghi chú đây là chủ đích đơn giản hóa.
- Việc ánh xạ zip cho SHIPPER được làm ở notebook Silver SHIPPER_silver_processing, còn notebook 3NF chỉ đọc cột zip có sẵn. Tuy nhiên zip này là suy đoán (xem 8.3).

**Nên cân nhắc sửa:** SHIPMENT đang có PK (order_id, shipper_id). Dữ liệu cho thấy order_id đã duy nhất, nên ship_date, delivery_date, shipping_fee chỉ phụ thuộc một phần của khóa ghép (vi phạm 2NF). Nếu nghiệp vụ không cho một đơn chia nhiều shipper, nên đặt **PK = \`order_id\`** và để shipper_id là FK.

# 9. Thiết kế Measure, Metric và KPI

## 9.1. Phân biệt

|         | **Bản chất**                                                    | **Ví dụ**                                                                      |
| ------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Measure | Số đo thô, cộng gộp được, nằm trong Fact                        | SUM(payment_value), SUM(quantity), SUM(shipping_fee), COUNT(DISTINCT order_id) |
| Metric  | Tính từ một hoặc nhiều measure (tỷ lệ, trung bình, tăng trưởng) | AOV, MoM Growth, Gross Margin %, thời gian giao trung bình                     |
| KPI     | Metric gắn mục tiêu, ngưỡng và kỳ hạn                           | "Tỷ lệ giao ≤ 5 ngày ≥ 80%"                                                    |

## 9.2. Hệ thống chỉ số kèm số nền (baseline) từ dữ liệu thật

<div class="joplin-table-wrapper"><table><thead><tr><th><p><strong>Mảng</strong></p></th><th><p><strong>Measure</strong></p></th><th><p><strong>Metric</strong></p></th><th><p><strong>Baseline hiện tại</strong></p></th><th><p><strong>KPI gợi ý</strong></p></th></tr></thead><tbody><tr><td><p>Vận chuyển</p></td><td><p>COUNT(order_id), SUM(shipping_fee)</p></td><td><pre><code>delivery_days = delivery_date − ship_date</code></pre></td><td><p>Trung bình <strong>4,5 ngày</strong> (phân bố đều 2–7 ngày). <strong>66,7%</strong> giao ≤ 5 ngày, 50,0% giao ≤ 4 ngày. Tám hãng đều ~4,5 ngày</p></td><td><p>Giao ≤ 5 ngày <strong>≥ 80%</strong></p></td></tr><tr><td><p>Thanh toán</p></td><td><p>SUM(payment_value), số đơn</p></td><td><p>Giá trị thanh toán TB, cơ cấu phương thức, tỷ lệ trả góp</p></td><td><p>TB <strong>24,238</strong>/đơn. Credit card 55,1%, PayPal 15,0%, COD 14,9%, Apple Pay 10,0%, chuyển khoản 5,0%. Trả góp ≥ 3 kỳ: 59,2%</p></td><td><p>Tỷ trọng COD ≤ X%</p></td></tr><tr><td><p>Lợi nhuận</p></td><td><p>SUM(price), SUM(cogs)</p></td><td><p>Gross Margin % = (price − cogs) / price</p></td><td><p>Biên trung bình theo SKU <strong>26,6%</strong> (theo tổng danh mục: 21,5%)</p></td><td><p>Gross Margin ≥ Y%</p></td></tr><tr><td><p>Danh mục sản phẩm</p></td><td><pre><code>COUNT(product_id)</code></pre></td><td><p>Tỷ trọng SKU theo category</p></td><td><p>2,412 SKU: Streetwear <strong>54,7%</strong>, Outdoor 30,8%, Casual 8,3%, GenZ 6,1%</p></td><td><p>Chỉ báo mô tả, chưa đặt KPI</p></td></tr><tr><td><p>Khuyến mãi</p></td><td><p>COUNT(promo_id), số dòng hàng có khuyến mãi</p></td><td><p>Discount Rate = giảm giá / doanh thu; tỷ lệ dòng hàng có khuyến mãi</p></td><td><p>50 chương trình, giảm % trung bình <strong>15,0%</strong>, 12/50 cho phép cộng dồn, 31/50 không yêu cầu đơn tối thiểu. <strong>38,7%</strong> dòng hàng có khuyến mãi (276,309 / 714,653)</p></td><td><p>Discount Rate ≤ Z%</p></td></tr></tbody></table></div>

- KPI bán hàng, khách hàng, hoàn trả, tồn kho và nhân viên do nhóm khác phụ trách nên không đưa vào.
- Biên lợi nhuận ở trên tính trên **giá niêm yết của danh mục**, chưa phải biên thực tế của đơn bán. Số thực tế cần ORDER_ITEMS.
- Hệ thống **không có ngày hẹn giao**, nên "giao đúng hạn" phải tự định nghĩa SLA (ở đây giả định 5 ngày). Hãy nêu rõ giả định này.
- Tính cộng gộp: doanh thu và số lượng là additive. stock_on_hand là semi-additive (không cộng theo thời gian). Các tỷ lệ (fill_rate, bounce_rate) là non-additive, phải tính lại từ tử số và mẫu số.

# 10. Thiết kế Golden Data (Star Schema)

## 10.1. Phần đã cài đặt trong notebook (Bước 17, 6 bảng)

Golden Data hiện được xuất vào warehouse_3nf/star_schema/, phục vụ Đề tài 4 (đánh giá năng lực nhân viên bán hàng).

| **Bảng**                             | **Mô tả**                                                                                                                                      |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Fact_Sales**                       | Nhóm khác phụ trách. Grain: 1 dòng hàng trong ORDER_ITEMS. Có product_id nối với Dim_Product, promo_count và has_promotion thể hiện khuyến mãi |
| Dim_Customer, Dim_Employee, Dim_Date | Nhóm khác phụ trách                                                                                                                            |
| **Dim_Product**                      | Của nhóm bạn: từ PRODUCT (gộp CATEGORY nếu đã tách). Do category → segment không 1-1 nên giữ phẳng                                             |
| Dim_Geography                        | Liên quan SHIPPER: zip, district, city, region                                                                                                 |

**Phần của nhóm bạn:** đã có Dim_Product và Dim_Geography. Còn thiếu Fact_Payment, Fact_Shipment, Dim_Shipper, Dim_Promotion + Bridge và Dim_Order_Profile (xem 10.2).

- Notebook dùng **khóa nghiệp vụ** (customer_id, date_key = ngày), chưa dùng surrogate key.
- Khuyến mãi được biểu diễn bằng promo_count, has_promotion trong Fact, chưa có Dim_Promotion.
- Notebook có bước kiểm tra chéo khóa ngoại Fact_Sales với từng Dim (kỳ vọng 0 dòng lệch). Kết quả chạy thật chưa được lưu trong file.

## 10.2. Thiết kế mở rộng (hướng phát triển)

| **Fact**      | **Grain (1 dòng =)** | **Chiều liên kết**                           | **Measures**                |
| ------------- | -------------------- | -------------------------------------------- | --------------------------- |
| Fact_Payment  | 1 đơn                | date, order_profile                          | payment_value, installments |
| Fact_Shipment | 1 đơn giao           | ship_date, delivery_date, shipper, geography | shipping_fee, delivery_days |

**Vì sao tách Fact_Payment:** PAYMENT ở mức đơn hàng còn Fact_Sales ở mức dòng hàng. Nếu để payment_value trong Fact_Sales thì đơn nhiều sản phẩm sẽ bị cộng trùng.

| **Dimension mở rộng**                  | **Nguồn**                       | **Ghi chú thiết kế**                                                                                       |
| -------------------------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Dim_Promotion + Bridge_Sales_Promotion | PROMOTION, ORDER_ITEM_PROMOTION | Bridge xử lý quan hệ N-N                                                                                   |
| Dim_Shipper                            | SHIPPER                         | 80 dòng. Nên xử lý join_date sai logic trước khi nạp                                                       |
| Dim_Order_Profile                      | ORDER + PAYMENT                 | Junk dimension: order_status, device_type, order_source (kênh bán), payment_method. **Thay cho Dim_Store** |
| Dim_Geography (nâng cấp)               | GEOGRAPHY                       | Hierarchy **Region → City**. district là thuộc tính riêng, không lồng trong city (xem 8.3)                 |
| Dim_Date (mở rộng)                     | Sinh tự động                    | Role-playing: order / ship / delivery / return date. Cần mở rộng dải ngày để phủ cả ngày giao hàng         |

**Quy ước:** dùng surrogate key cho mọi Dimension, có dòng "Unknown" (key = −1) cho giá trị thiếu. Tầng Gold chấp nhận dư thừa có chủ đích, ngược với Silver/3NF.

## 10.3. Lợi ích cho OLAP và Dashboard

| **Lợi ích**      | **Giải thích**                                                                                                               |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Truy vấn nhanh   | Chỉ cần Fact JOIN vài Dimension (độ sâu JOIN = 1), thay vì đi qua chuỗi ORDER → ORDER_ITEMS → PRODUCT → CUSTOMER → GEOGRAPHY |
| Dễ hiểu          | Cấu trúc "số liệu ở giữa, góc nhìn xung quanh" khớp với câu hỏi nghiệp vụ                                                    |
| Thao tác OLAP    | Drill-down (Region → City), roll-up, slice, dice, pivot dựa trên hierarchy                                                   |
| Tối ưu BI        | Power BI, Tableau, Looker nhận mô hình chiều tự nhiên                                                                        |
| Nhất quán chỉ số | Conformed dimensions và measure định nghĩa một lần, mọi báo cáo dùng chung                                                   |
| Dễ mở rộng       | Thêm Fact hoặc Dimension mới mà không phá cấu trúc cũ                                                                        |