# Báo cáo tổng hợp dữ liệu `DAAI_N1.4/silver_data`

- **Thư mục nguồn:** `D:\TH_DA&AI\DAAI_N1.4\silver_data`
- **Số bảng:** 15
- **Tổng số bản ghi:** 3,323,316
- **Tổng dung lượng:** 204,060,119 byte (194.61 MiB)
- **Kiểu dữ liệu:** suy luận từ nội dung CSV; không phải kiểu vật lý SQL. Mã định danh dạng số nên được xem như mã, không phải đại lượng đo.

## Khái niệm và chức năng dữ liệu

Silver là lớp dữ liệu đã được chuẩn hóa/làm sạch hơn nguồn thô, được chia thành các bảng theo nghiệp vụ. Bảng đơn hàng/dòng hàng mô tả giao dịch; các bảng khách hàng, sản phẩm, nhân viên, địa lý và shipper mô tả thực thể; các bảng thanh toán, trả hàng, đánh giá, khuyến mãi, tồn kho và web traffic ghi nhận sự kiện/chỉ số liên quan.

| Bảng | Khái niệm / chức năng | Grain hoặc khóa ứng viên | Dòng | Cột | Dung lượng |
|---|---|---|---:|---:|---:|
| `CUSTOMER_silver.csv` | Hồ sơ khách hàng đã chuẩn hóa, gồm địa chỉ ZIP, ngày đăng ký, nhóm nhân khẩu học và kênh thu hút khách hàng. | một dòng / `customer_id` | 121,930 | 6 | 5,974,177 byte (5.70 MiB) |
| `geography.csv` | Danh mục địa lý ánh xạ ZIP sang thành phố, vùng và quận/huyện. | một dòng / `zip` | 39,948 | 4 | 1,362,335 byte (1.30 MiB) |
| `inventory_silver.csv` | Ảnh chụp tồn kho theo ngày và sản phẩm; gồm lượng tồn/nhập/bán, chỉ số cung ứng, thuộc tính sản phẩm và các cờ outlier đã tạo trong xử lý silver. | một dòng / `snapshot_date+product_id` | 60,247 | 25 | 9,537,181 byte (9.10 MiB) |
| `ORDER_ITEM_PROMOTION_silver.csv` | Bảng liên kết giữa dòng đơn hàng/sản phẩm và chương trình khuyến mãi được áp dụng. | một dòng / `order_id+product_id+promo_id` | 276,309 | 3 | 6,466,380 byte (6.17 MiB) |
| `ORDER_ITEMS_silver.csv` | Chi tiết dòng hàng theo đơn và sản phẩm, gồm số lượng, đơn giá và chiết khấu. | một dòng / `order_id+product_id` | 714,653 | 5 | 19,750,323 byte (18.84 MiB) |
| `ORDER_silver.csv` | Thông tin đơn hàng ở cấp một dòng/đơn; bao gồm ngày, khách hàng, trạng thái, kênh/thiết bị, nhân viên bán hàng và comment. | một dòng / `order_id` | 646,945 | 9 | 100,749,788 byte (96.08 MiB) |
| `payment.csv` | Thông tin thanh toán theo đơn hàng, phương thức, giá trị và số kỳ. | một dòng / `order_id` | 646,945 | 4 | 17,736,345 byte (16.91 MiB) |
| `product.csv` | Danh mục sản phẩm cùng phân loại và thuộc tính thương mại. | một dòng / `product_id` | 2,412 | 8 | 192,759 byte (0.18 MiB) |
| `promotion.csv` | Danh mục chương trình khuyến mãi, thời gian, điều kiện và kênh áp dụng. | một dòng / `promo_id` | 50 | 10 | 4,958 byte (0.00 MiB) |
| `returns.csv` | Sự kiện/dòng trả hàng gồm đơn, sản phẩm, ngày, lý do, số lượng và tiền hoàn. | một dòng / `return_id` | 35,733 | 7 | 2,020,408 byte (1.93 MiB) |
| `reviews.csv` | Đánh giá sản phẩm theo đơn, gồm mã đánh giá, ngày, điểm và tiêu đề. | một dòng / `review_id` | 714,653 | 6 | 37,519,686 byte (35.78 MiB) |
| `sales_employee.csv` | Danh mục nhân viên bán hàng và thông tin hồ sơ liên quan. | một dòng / `sales_employee_id` | 200 | 5 | 11,119 byte (0.01 MiB) |
| `shipment.csv` | Thông tin vận chuyển theo đơn, gồm shipper, ngày gửi/giao và phí vận chuyển. | một dòng / `order_id` | 59,559 | 5 | 2,497,871 byte (2.38 MiB) |
| `shipper.csv` | Hồ sơ người/đơn vị giao hàng, thông tin nhân khẩu học, năng lực và khu vực. | một dòng / `shipper_id` | 80 | 16 | 9,801 byte (0.01 MiB) |
| `web_traffic_silver.csv` | Lưu lượng website theo ngày và nguồn; gồm phiên, khách truy cập, lượt xem và cờ outlier. | một dòng / `date` | 3,652 | 8 | 226,988 byte (0.22 MiB) |

### Diễn giải một số khái niệm

- `ORDER_silver` là bảng đơn ở cấp order; `ORDER_ITEMS_silver` ghi chi tiết sản phẩm trong đơn.
- `ORDER_ITEM_PROMOTION_silver` là bảng liên kết nhiều-nhiều giữa dòng hàng và promotion.
- `inventory_silver` là ảnh chụp tồn kho theo thời điểm, không phải giao dịch bán đơn lẻ.
- Cột có hậu tố `_is_outlier` là cờ do quy trình xử lý tạo ra; đây là dấu hiệu cần xem xét, không đồng nghĩa bản ghi sai hoặc phải xóa.
- `reviews` và `ORDER_silver.comment` có thể đại diện cho các dạng phản hồi khác nhau; không nên coi comment là rating khách hàng nếu chưa có quy tắc nghiệp vụ.

## Bất thường và điểm cần xác minh

1. **Cần xác minh ngày khách hàng:** 477,453/646,945 đơn (73.80%) có `order_date` trước `signup_date`. Nếu signup_date là ngày tạo hồ sơ đầu tiên, đây là bất nhất thời gian; không nên tự ý sửa hoặc loại đơn nếu chưa xác nhận nghiệp vụ.
2. **Cần xác minh ngày gia nhập shipper:** 59,559/59,559 chuyến (100.00%) có `ship_date` trước `join_date` trong hồ sơ shipper.

### Kiểm tra khóa và liên kết giữa bảng

| Liên kết | Bản ghi không tìm thấy khóa cha |
|---|---:|
| `ORDER_silver.csv.customer_id` → `CUSTOMER_silver.csv.customer_id` | 0 |
| `ORDER_silver.csv.zip` → `geography.csv.zip` | 0 |
| `ORDER_silver.csv.sales_employee_id` → `sales_employee.csv.sales_employee_id` | 0 |
| `ORDER_ITEMS_silver.csv.order_id` → `ORDER_silver.csv.order_id` | 0 |
| `ORDER_ITEMS_silver.csv.product_id` → `product.csv.product_id` | 0 |
| `ORDER_ITEM_PROMOTION_silver.csv.order_id` → `ORDER_silver.csv.order_id` | 0 |
| `ORDER_ITEM_PROMOTION_silver.csv.product_id` → `product.csv.product_id` | 0 |
| `ORDER_ITEM_PROMOTION_silver.csv.promo_id` → `promotion.csv.promo_id` | 0 |
| `payment.csv.order_id` → `ORDER_silver.csv.order_id` | 0 |
| `returns.csv.order_id` → `ORDER_silver.csv.order_id` | 0 |
| `returns.csv.product_id` → `product.csv.product_id` | 0 |
| `reviews.csv.order_id` → `ORDER_silver.csv.order_id` | 0 |
| `shipment.csv.order_id` → `ORDER_silver.csv.order_id` | 0 |
| `shipment.csv.shipper_id` → `shipper.csv.shipper_id` | 0 |
| `shipper.csv.zip` → `geography.csv.zip` | 0 |
| `inventory_silver.csv.product_id` → `product.csv.product_id` | 0 |


### Kiểm tra miền giá trị và cờ outlier

| Trường | Ngoài phạm vi dự kiến |
|---|---:|
| `inventory_silver.csv.fill_rate` | 0 |
| `inventory_silver.csv.sell_through_rate` | 0 |
| `web_traffic_silver.csv.bounce_rate` | 0 |
| `shipper.csv.shipper_rating` | 0 |
| `shipper.csv.delivery_success_rate` | 0 |
| `reviews.csv.rating` | 0 |

| Cờ outlier | Số dòng được đánh dấu |
|---|---:|
| `inventory_silver.csv.stock_on_hand_is_outlier` | 6,432 |
| `inventory_silver.csv.units_received_is_outlier` | 6,392 |
| `inventory_silver.csv.units_sold_is_outlier` | 6,388 |
| `inventory_silver.csv.days_of_supply_is_outlier` | 7,455 |
| `web_traffic_silver.csv.page_views_is_outlier` | 18 |

## Mô tả chi tiết bảng và cột

Trống là chuỗi rỗng trong CSV. Min/max/trung bình là thống kê trên dữ liệu quan sát; trung bình của mã định danh không mang ý nghĩa nghiệp vụ.

### `CUSTOMER_silver.csv`

- **Chức năng:** Hồ sơ khách hàng đã chuẩn hóa, gồm địa chỉ ZIP, ngày đăng ký, nhóm nhân khẩu học và kênh thu hút khách hàng.
- **Số dòng/cột:** 121,930/6; **dung lượng:** 5,974,177 byte; **encoding:** utf-8-sig.
- **Khóa ứng viên:** customer_id; **dòng thiếu/trùng khóa:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `customer_id` | Mã khách hàng | integer | 0 (0.00%) | 121,930 | 1 | 157,563 | 78,736.8987 | 6 ký tự |
| `zip` | Mã ZIP/khu vực địa lý | integer | 0 (0.00%) | 31,491 | 1,001 | 99,950 | 50,990.1656 | 5 ký tự |
| `signup_date` | Ngày đăng ký khách hàng | date | 0 (0.00%) | 3,941 | 2012-01-17 | 2022-12-31 | — | 10 ký tự |
| `gender` | Giới tính theo hồ sơ | string | 0 (0.00%) | 3 | — | — | — | 10 ký tự |
| `age_group` | Nhóm tuổi khách hàng | string | 0 (0.00%) | 5 | — | — | — | 5 ký tự |
| `acquisition_channel` | Kênh thu hút khách hàng | string | 0 (0.00%) | 6 | — | — | — | 14 ký tự |

### `geography.csv`

- **Chức năng:** Danh mục địa lý ánh xạ ZIP sang thành phố, vùng và quận/huyện.
- **Số dòng/cột:** 39,948/4; **dung lượng:** 1,362,335 byte; **encoding:** utf-8-sig.
- **Khóa ứng viên:** zip; **dòng thiếu/trùng khóa:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `zip` | Mã ZIP/khu vực địa lý | integer | 0 (0.00%) | 39,948 | 1 | 99,950 | 50,895.0847 | 5 ký tự |
| `city` | Thành phố | string | 0 (0.00%) | 42 | — | — | — | 19 ký tự |
| `region` | Vùng | string | 0 (0.00%) | 3 | — | — | — | 7 ký tự |
| `district` | Quận/huyện | string | 0 (0.00%) | 39 | — | — | — | 12 ký tự |

### `inventory_silver.csv`

- **Chức năng:** Ảnh chụp tồn kho theo ngày và sản phẩm; gồm lượng tồn/nhập/bán, chỉ số cung ứng, thuộc tính sản phẩm và các cờ outlier đã tạo trong xử lý silver.
- **Số dòng/cột:** 60,247/25; **dung lượng:** 9,537,181 byte; **encoding:** utf-8-sig.
- **Khóa ứng viên:** snapshot_date + product_id; **dòng thiếu/trùng khóa:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `snapshot_date` | Ngày chụp số liệu tồn kho | date | 0 (0.00%) | 126 | 2012-07-31 | 2022-12-31 | — | 10 ký tự |
| `product_id` | Mã sản phẩm | integer | 0 (0.00%) | 1,624 | 1 | 2,412 | 1,311.4085 | 4 ký tự |
| `stock_on_hand` | Lượng hàng tồn | integer | 0 (0.00%) | 1,895 | 3 | 2,673 | 189.2985 | 4 ký tự |
| `units_received` | Lượng hàng nhập | integer | 0 (0.00%) | 360 | 1 | 817 | 18.0468 | 3 ký tự |
| `units_sold` | Lượng hàng bán | integer | 0 (0.00%) | 303 | 1 | 670 | 15.4178 | 3 ký tự |
| `stockout_days` | Số ngày hết hàng | integer | 0 (0.00%) | 29 | 0 | 28 | 1.1606 | 2 ký tự |
| `days_of_supply` | Số ngày tồn kho đủ cung ứng | number | 0 (0.00%) | 9,289 | 5.2 | 68,100 | 912.6776 | 7 ký tự |
| `fill_rate` | Tỷ lệ đáp ứng nhu cầu | number | 0 (0.00%) | 29 | 0.0667 | 1 | 0.9613 | 6 ký tự |
| `stockout_flag` | Cờ cảnh báo hết hàng | integer | 0 (0.00%) | 2 | 0 | 1 | 0.6734 | 1 ký tự |
| `overstock_flag` | Cờ cảnh báo tồn quá mức | integer | 0 (0.00%) | 2 | 0 | 1 | 0.7626 | 1 ký tự |
| `reorder_flag` | Cờ đề nghị đặt hàng lại | integer | 0 (0.00%) | 1 | 0 | 0 | 0 | 1 ký tự |
| `sell_through_rate` | Tỷ lệ bán hết hàng | number | 0 (0.00%) | 4,017 | 0.0004 | 0.8531 | 0.1523 | 6 ký tự |
| `product_name` | Tên sản phẩm | string | 0 (0.00%) | 1,465 | — | — | — | 17 ký tự |
| `category` | Danh mục sản phẩm/nhóm áp dụng | string | 0 (0.00%) | 4 | — | — | — | 10 ký tự |
| `segment` | Phân khúc sản phẩm | string | 0 (0.00%) | 8 | — | — | — | 11 ký tự |
| `size` | Kích cỡ sản phẩm | string | 0 (0.00%) | 4 | — | — | — | 2 ký tự |
| `color` | Màu sản phẩm | string | 0 (0.00%) | 10 | — | — | — | 6 ký tự |
| `price` | Giá bán niêm yết | number | 0 (0.00%) | 1,249 | 440.37 | 40,950 | 5,741.9433 | 18 ký tự |
| `cogs` | Giá vốn hàng bán | number | 0 (0.00%) | 1,600 | 249.2806 | 38,902.5 | 4,522.1492 | 18 ký tự |
| `year` | Năm của kỳ ghi nhận | integer | 0 (0.00%) | 11 | 2,012 | 2,022 | 2,017.2228 | 4 ký tự |
| `month` | Tháng của kỳ ghi nhận | integer | 0 (0.00%) | 12 | 1 | 12 | 6.6173 | 2 ký tự |
| `stock_on_hand_is_outlier` | Cờ đánh dấu tồn kho là outlier | boolean | 0 (0.00%) | 2 | — | — | — | 5 ký tự |
| `units_received_is_outlier` | Cờ đánh dấu lượng nhập là outlier | boolean | 0 (0.00%) | 2 | — | — | — | 5 ký tự |
| `units_sold_is_outlier` | Cờ đánh dấu lượng bán là outlier | boolean | 0 (0.00%) | 2 | — | — | — | 5 ký tự |
| `days_of_supply_is_outlier` | Cờ đánh dấu ngày cung ứng là outlier | boolean | 0 (0.00%) | 2 | — | — | — | 5 ký tự |

### `ORDER_ITEM_PROMOTION_silver.csv`

- **Chức năng:** Bảng liên kết giữa dòng đơn hàng/sản phẩm và chương trình khuyến mãi được áp dụng.
- **Số dòng/cột:** 276,309/3; **dung lượng:** 6,466,380 byte; **encoding:** utf-8-sig.
- **Khóa ứng viên:** order_id + product_id + promo_id; **dòng thiếu/trùng khóa:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `order_id` | Mã đơn hàng | integer | 0 (0.00%) | 248,242 | 46,253 | 834,335 | 433,207.0691 | 6 ký tự |
| `product_id` | Mã sản phẩm | integer | 0 (0.00%) | 1,495 | 1 | 2,412 | 1,234.896 | 4 ký tự |
| `promo_id` | Mã chương trình khuyến mãi | string | 0 (0.00%) | 50 | — | — | — | 10 ký tự |

### `ORDER_ITEMS_silver.csv`

- **Chức năng:** Chi tiết dòng hàng theo đơn và sản phẩm, gồm số lượng, đơn giá và chiết khấu.
- **Số dòng/cột:** 714,653/5; **dung lượng:** 19,750,323 byte; **encoding:** utf-8-sig.
- **Khóa ứng viên:** order_id + product_id; **dòng thiếu/trùng khóa:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `order_id` | Mã đơn hàng | integer | 0 (0.00%) | 646,945 | 1 | 834,397 | 411,614.7584 | 6 ký tự |
| `product_id` | Mã sản phẩm | integer | 0 (0.00%) | 1,598 | 1 | 2,412 | 1,234.9269 | 4 ký tự |
| `quantity` | Số lượng sản phẩm trong dòng đơn hàng | integer | 0 (0.00%) | 14 | 1 | 15 | 4.4961 | 2 ký tự |
| `unit_price` | Đơn giá sản phẩm trong đơn hàng | number | 0 (0.00%) | 492,775 | 392.57 | 15,324.06 | 5,081.5124 | 8 ký tự |
| `discount_amount` | Số tiền chiết khấu | number | 0 (0.00%) | 107,010 | 0 | 4,838.15 | 584.6738 | 7 ký tự |

### `ORDER_silver.csv`

- **Chức năng:** Thông tin đơn hàng ở cấp một dòng/đơn; bao gồm ngày, khách hàng, trạng thái, kênh/thiết bị, nhân viên bán hàng và comment.
- **Số dòng/cột:** 646,945/9; **dung lượng:** 100,749,788 byte; **encoding:** utf-8-sig.
- **Khóa ứng viên:** order_id; **dòng thiếu/trùng khóa:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `order_id` | Mã đơn hàng | integer | 0 (0.00%) | 646,945 | 1 | 834,397 | 417,189.4703 | 6 ký tự |
| `order_date` | Ngày đặt hàng | date | 0 (0.00%) | 3,833 | 2012-07-04 | 2022-12-31 | — | 10 ký tự |
| `customer_id` | Mã khách hàng | integer | 0 (0.00%) | 90,246 | 1 | 157,563 | 84,906.2035 | 6 ký tự |
| `zip` | Mã ZIP/khu vực địa lý | integer | 0 (0.00%) | 29,932 | 1,001 | 99,950 | 55,410.7404 | 5 ký tự |
| `order_status` | Trạng thái đơn hàng | string | 0 (0.00%) | 6 | — | — | — | 9 ký tự |
| `device_type` | Loại thiết bị dùng để đặt hàng | string | 0 (0.00%) | 3 | — | — | — | 7 ký tự |
| `order_source` | Nguồn phát sinh đơn hàng | string | 0 (0.00%) | 6 | — | — | — | 14 ký tự |
| `sales_employee_id` | Mã nhân viên bán hàng | string | 0 (0.00%) | 200 | — | — | — | 7 ký tự |
| `comment` | Nội dung phản hồi gắn với đơn hàng | string | 0 (0.00%) | 18 | — | — | — | 98 ký tự |

### `payment.csv`

- **Chức năng:** Thông tin thanh toán theo đơn hàng, phương thức, giá trị và số kỳ.
- **Số dòng/cột:** 646,945/4; **dung lượng:** 17,736,345 byte; **encoding:** utf-8-sig.
- **Khóa ứng viên:** order_id; **dòng thiếu/trùng khóa:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `order_id` | Mã đơn hàng | integer | 0 (0.00%) | 646,945 | 1 | 834,397 | 417,189.4703 | 6 ký tự |
| `payment_method` | Phương thức thanh toán | string | 0 (0.00%) | 5 | — | — | — | 13 ký tự |
| `payment_value` | Số tiền thanh toán | number | 0 (0.00%) | 595,420 | 389.74 | 331,570.4 | 24,238.3344 | 9 ký tự |
| `installments` | Số kỳ thanh toán | integer | 0 (0.00%) | 5 | 1 | 12 | 3.4483 | 2 ký tự |

### `product.csv`

- **Chức năng:** Danh mục sản phẩm cùng phân loại và thuộc tính thương mại.
- **Số dòng/cột:** 2,412/8; **dung lượng:** 192,759 byte; **encoding:** utf-8-sig.
- **Khóa ứng viên:** product_id; **dòng thiếu/trùng khóa:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `product_id` | Mã sản phẩm | integer | 0 (0.00%) | 2,412 | 1 | 2,412 | 1,206.5 | 4 ký tự |
| `product_name` | Tên sản phẩm | string | 0 (0.00%) | 2,172 | — | — | — | 17 ký tự |
| `category` | Danh mục sản phẩm/nhóm áp dụng | string | 0 (0.00%) | 4 | — | — | — | 10 ký tự |
| `segment` | Phân khúc sản phẩm | string | 0 (0.00%) | 8 | — | — | — | 11 ký tự |
| `size` | Kích cỡ sản phẩm | string | 0 (0.00%) | 4 | — | — | — | 2 ký tự |
| `color` | Màu sản phẩm | string | 0 (0.00%) | 10 | — | — | — | 6 ký tự |
| `price` | Giá bán niêm yết | number | 0 (0.00%) | 1,990 | 9.0566 | 40,950 | 4,928.2162 | 18 ký tự |
| `cogs` | Giá vốn hàng bán | number | 0 (0.00%) | 2,381 | 5.1838 | 38,902.5 | 3,868.3467 | 18 ký tự |

### `promotion.csv`

- **Chức năng:** Danh mục chương trình khuyến mãi, thời gian, điều kiện và kênh áp dụng.
- **Số dòng/cột:** 50/10; **dung lượng:** 4,958 byte; **encoding:** utf-8-sig.
- **Khóa ứng viên:** promo_id; **dòng thiếu/trùng khóa:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `promo_id` | Mã chương trình khuyến mãi | string | 0 (0.00%) | 50 | — | — | — | 10 ký tự |
| `promo_name` | Tên chương trình khuyến mãi | string | 0 (0.00%) | 50 | — | — | — | 18 ký tự |
| `promo_type` | Loại hình khuyến mãi | string | 0 (0.00%) | 2 | — | — | — | 10 ký tự |
| `discount_value` | Giá trị hoặc tỷ lệ giảm | number | 0 (0.00%) | 6 | 10 | 50 | 18.5 | 4 ký tự |
| `start_date` | Ngày bắt đầu hiệu lực | date | 0 (0.00%) | 50 | 2013-01-31 | 2022-11-18 | — | 10 ký tự |
| `end_date` | Ngày kết thúc hiệu lực | date | 0 (0.00%) | 50 | 2013-03-01 | 2022-12-31 | — | 10 ký tự |
| `applicable_category` | Danh mục sản phẩm áp dụng | string | 0 (0.00%) | 3 | — | — | — | 14 ký tự |
| `promo_channel` | Kênh áp dụng khuyến mãi | string | 0 (0.00%) | 5 | — | — | — | 12 ký tự |
| `stackable_flag` | Cờ cho biết có thể cộng dồn khuyến mãi | integer | 0 (0.00%) | 2 | 0 | 1 | 0.24 | 1 ký tự |
| `min_order_value` | Giá trị đơn hàng tối thiểu để áp dụng | integer | 0 (0.00%) | 5 | 0 | 200,000 | 46,000 | 6 ký tự |

### `returns.csv`

- **Chức năng:** Sự kiện/dòng trả hàng gồm đơn, sản phẩm, ngày, lý do, số lượng và tiền hoàn.
- **Số dòng/cột:** 35,733/7; **dung lượng:** 2,020,408 byte; **encoding:** utf-8-sig.
- **Khóa ứng viên:** return_id; **dòng thiếu/trùng khóa:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `return_id` | Mã sự kiện trả hàng | string | 0 (0.00%) | 35,733 | — | — | — | 10 ký tự |
| `order_id` | Mã đơn hàng | integer | 0 (0.00%) | 35,733 | 1 | 834,347 | 411,607.8059 | 6 ký tự |
| `product_id` | Mã sản phẩm | integer | 0 (0.00%) | 1,245 | 3 | 2,412 | 1,235.8415 | 4 ký tự |
| `return_date` | Ngày trả hàng | date | 0 (0.00%) | 34 | 2012-07-11 | 2012-08-13 | — | 10 ký tự |
| `return_reason` | Lý do trả hàng | string | 0 (0.00%) | 5 | — | — | — | 16 ký tự |
| `return_quantity` | Số lượng sản phẩm trả | integer | 0 (0.00%) | 8 | 1 | 8 | 2.3816 | 1 ký tự |
| `refund_amount` | Số tiền hoàn trả | number | 0 (0.00%) | 34,932 | 531.61 | 122,592.48 | 12,169.3724 | 9 ký tự |

### `reviews.csv`

- **Chức năng:** Đánh giá sản phẩm theo đơn, gồm mã đánh giá, ngày, điểm và tiêu đề.
- **Số dòng/cột:** 714,653/6; **dung lượng:** 37,519,686 byte; **encoding:** utf-8-sig.
- **Khóa ứng viên:** review_id; **dòng thiếu/trùng khóa:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `review_id` | Mã đánh giá | string | 0 (0.00%) | 714,653 | — | — | — | 11 ký tự |
| `order_id` | Mã đơn hàng | integer | 0 (0.00%) | 646,945 | 1 | 834,397 | 411,614.7584 | 6 ký tự |
| `product_id` | Mã sản phẩm | integer | 0 (0.00%) | 1,598 | 1 | 2,412 | 1,234.9269 | 4 ký tự |
| `review_date` | Ngày đánh giá | date | 0 (0.00%) | 42 | 2012-07-10 | 2012-08-20 | — | 10 ký tự |
| `rating` | Điểm đánh giá | integer | 0 (0.00%) | 5 | 1 | 5 | 4.1901 | 1 ký tự |
| `review_title` | Tiêu đề/ngắn gọn của đánh giá | string | 0 (0.00%) | 16 | — | — | — | 23 ký tự |

### `sales_employee.csv`

- **Chức năng:** Danh mục nhân viên bán hàng và thông tin hồ sơ liên quan.
- **Số dòng/cột:** 200/5; **dung lượng:** 11,119 byte; **encoding:** utf-8-sig.
- **Khóa ứng viên:** sales_employee_id; **dòng thiếu/trùng khóa:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `sales_employee_id` | Mã nhân viên bán hàng | string | 0 (0.00%) | 200 | — | — | — | 7 ký tự |
| `name` | Tên nhân viên | string | 0 (0.00%) | 192 | — | — | — | 16 ký tự |
| `marital_status` | Tình trạng hôn nhân | string | 0 (0.00%) | 2 | — | — | — | 10 ký tự |
| `education_level` | Trình độ học vấn | string | 0 (0.00%) | 4 | — | — | — | 11 ký tự |
| `years_experience` | Số năm kinh nghiệm | integer | 0 (0.00%) | 20 | 1 | 20 | 10.91 | 2 ký tự |

### `shipment.csv`

- **Chức năng:** Thông tin vận chuyển theo đơn, gồm shipper, ngày gửi/giao và phí vận chuyển.
- **Số dòng/cột:** 59,559/5; **dung lượng:** 2,497,871 byte; **encoding:** utf-8-sig.
- **Khóa ứng viên:** order_id; **dòng thiếu/trùng khóa:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `order_id` | Mã đơn hàng | integer | 0 (0.00%) | 59,559 | 1 | 87,576 | 43,857.2624 | 5 ký tự |
| `shipper_id` | Mã người/đơn vị giao hàng | string | 0 (0.00%) | 80 | — | — | — | 8 ký tự |
| `ship_date` | Ngày gửi hàng | date | 0 (0.00%) | 351 | 2012-07-04 | 2013-06-19 | — | 10 ký tự |
| `delivery_date` | Ngày giao hàng | date | 0 (0.00%) | 355 | 2012-07-06 | 2013-06-25 | — | 10 ký tự |
| `shipping_fee` | Phí vận chuyển | number | 0 (0.00%) | 1,422 | 0 | 32 | 5.7402 | 5 ký tự |

### `shipper.csv`

- **Chức năng:** Hồ sơ người/đơn vị giao hàng, thông tin nhân khẩu học, năng lực và khu vực.
- **Số dòng/cột:** 80/16; **dung lượng:** 9,801 byte; **encoding:** utf-8-sig.
- **Khóa ứng viên:** shipper_id; **dòng thiếu/trùng khóa:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `shipper_id` | Mã người/đơn vị giao hàng | string | 0 (0.00%) | 80 | — | — | — | 8 ký tự |
| `shipper_name` | Tên người giao hàng | string | 0 (0.00%) | 73 | — | — | — | 18 ký tự |
| `shipper_phone` | Số điện thoại liên hệ người giao hàng | integer | 0 (0.00%) | 80 | 900,482,857 | 999,125,359 | 950,716,597.1125 | 9 ký tự |
| `shipper_gender` | Giới tính người giao hàng | string | 0 (0.00%) | 2 | — | — | — | 6 ký tự |
| `shipper_age` | Tuổi người giao hàng | integer | 0 (0.00%) | 27 | 24 | 55 | 41.7125 | 2 ký tự |
| `shipper_marital_status` | Tình trạng hôn nhân người giao hàng | string | 0 (0.00%) | 2 | — | — | — | 7 ký tự |
| `shipper_education` | Trình độ học vấn người giao hàng | string | 0 (0.00%) | 3 | — | — | — | 11 ký tự |
| `shipper_company` | Đơn vị vận chuyển | string | 0 (0.00%) | 8 | — | — | — | 14 ký tự |
| `shipper_vehicle` | Loại phương tiện giao hàng | string | 0 (0.00%) | 3 | — | — | — | 9 ký tự |
| `shipper_experience_years` | Số năm kinh nghiệm người giao hàng | integer | 0 (0.00%) | 12 | 1 | 12 | 7.625 | 2 ký tự |
| `shipper_rating` | Điểm đánh giá người giao hàng | number | 0 (0.00%) | 9 | 4.2 | 5 | 4.645 | 3 ký tự |
| `delivery_success_rate` | Tỷ lệ giao hàng thành công theo thang nguồn | number | 0 (0.00%) | 42 | 95.1 | 99.9 | 97.5113 | 4 ký tự |
| `average_delivery_time` | Thời gian giao hàng trung bình theo đơn vị nguồn | integer | 0 (0.00%) | 42 | 20 | 75 | 47.6625 | 2 ký tự |
| `working_shift` | Ca làm việc | string | 0 (0.00%) | 3 | — | — | — | 9 ký tự |
| `join_date` | Ngày gia nhập người giao hàng | date | 0 (0.00%) | 80 | 2018-01-12 | 2026-03-17 | — | 10 ký tự |
| `zip` | Mã ZIP/khu vực địa lý | integer | 0 (0.00%) | 76 | 3 | 90,029 | 30,004.875 | 5 ký tự |

### `web_traffic_silver.csv`

- **Chức năng:** Lưu lượng website theo ngày và nguồn; gồm phiên, khách truy cập, lượt xem và cờ outlier.
- **Số dòng/cột:** 3,652/8; **dung lượng:** 226,988 byte; **encoding:** utf-8-sig.
- **Khóa ứng viên:** date; **dòng thiếu/trùng khóa:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `date` | Ngày ghi nhận | date | 0 (0.00%) | 3,652 | 2013-01-01 | 2022-12-31 | — | 10 ký tự |
| `sessions` | Số phiên truy cập | integer | 0 (0.00%) | 3,447 | 7,973 | 50,947 | 25,041.7681 | 5 ký tự |
| `unique_visitors` | Số khách truy cập duy nhất | integer | 0 (0.00%) | 3,382 | 6,136 | 40,430 | 19,031.4044 | 5 ký tự |
| `page_views` | Số lượt xem trang | integer | 0 (0.00%) | 3,620 | 30,451 | 275,560 | 108,615.2245 | 6 ký tự |
| `bounce_rate` | Tỷ lệ thoát | number | 0 (0.00%) | 261 | 0.0032 | 0.0058 | 0.0045 | 7 ký tự |
| `avg_session_duration_sec` | Thời lượng phiên trung bình (giây) | number | 0 (0.00%) | 1,771 | 100.1 | 319.9 | 210.2832 | 5 ký tự |
| `traffic_source` | Nguồn truy cập | string | 0 (0.00%) | 6 | — | — | — | 14 ký tự |
| `page_views_is_outlier` | Cờ đánh dấu lượt xem trang là outlier | boolean | 0 (0.00%) | 2 | — | — | — | 5 ký tự |

## Phạm vi và hạn chế

- Kiểu dữ liệu, grain và ý nghĩa được suy luận từ tên cột/cấu trúc và giá trị quan sát; cần đối chiếu data contract để xác nhận định nghĩa chính thức.
- Cờ outlier được báo cáo như nhãn có sẵn; không đánh giá lại thuật toán phát hiện outlier.
- Báo cáo không đưa các ví dụ chứa dữ liệu cá nhân như tên, điện thoại hoặc comment.
