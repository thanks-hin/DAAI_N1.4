# Báo cáo tổng hợp dữ liệu `student_data`

- **Thư mục nguồn:** `D:\TH_DA&AI\student_data`
- **Số tệp dữ liệu:** 15 (12 CSV, 3 JSON)
- **Tổng số bản ghi:** 2,959,355
- **Tổng dung lượng tệp:** 321,567,953 byte (306.67 MiB)
- **Lưu ý kiểu dữ liệu:** CSV/JSON không khai báo schema SQL; kiểu dưới đây được suy luận từ nội dung. Các mã định danh dạng số vẫn nên được lưu như chuỗi nếu cần giữ định dạng/ý nghĩa mã.

## Khái niệm và chức năng các tập dữ liệu

| Tệp | Khái niệm / chức năng | Bản ghi | Cột | Kích thước |
|---|---|---:|---:|---:|
| `customers.csv` | Hồ sơ khách hàng: mã khách hàng, địa chỉ/địa lý, ngày đăng ký và nhóm nhân khẩu học/kênh tiếp cận. | 121,930 | 7 | 7,079,679 byte (6.75 MiB) |
| `epd.json` | Tập dữ liệu JSON có cấu trúc thuộc tính sản phẩm; cần đối chiếu phiên bản với products.csv trước khi ghép. | 1,000 | 8 | 224,069 byte (0.21 MiB) |
| `eprom.json` | Tập dữ liệu JSON về chương trình khuyến mãi; cần đối chiếu phiên bản với promotions.csv trước khi ghép. | 1,000 | 10 | 324,919 byte (0.31 MiB) |
| `geography.csv` | Danh mục địa lý ánh xạ mã ZIP đến thành phố, vùng và quận/huyện. | 39,948 | 4 | 1,402,281 byte (1.34 MiB) |
| `inventory.csv` | Ảnh chụp tồn kho theo ngày và sản phẩm; có số lượng, chỉ số cung ứng và cờ cảnh báo. | 60,247 | 17 | 5,668,678 byte (5.41 MiB) |
| `order_items.csv` | Chi tiết dòng hàng trong đơn: sản phẩm, số lượng, đơn giá, chiết khấu và mã khuyến mãi. | 714,669 | 7 | 23,942,735 byte (22.83 MiB) |
| `orders_enriched.csv` | Bảng đơn hàng đã làm giàu thông tin khách hàng, địa lý, thanh toán, nhân viên, trạng thái và phản hồi. | 646,945 | 17 | 155,195,353 byte (148.01 MiB) |
| `payments.csv` | Thông tin thanh toán theo đơn, gồm phương thức, số tiền và số kỳ thanh toán. | 646,945 | 4 | 18,383,288 byte (17.53 MiB) |
| `products.csv` | Danh mục sản phẩm và thuộc tính thương mại như danh mục, kích cỡ, màu, giá và giá vốn. | 2,412 | 8 | 195,223 byte (0.19 MiB) |
| `promotions.csv` | Danh mục chương trình khuyến mãi, thời hạn, điều kiện, kênh và mức giảm. | 50 | 10 | 4,444 byte (0.00 MiB) |
| `returns.csv` | Các dòng trả hàng theo đơn/sản phẩm, ngày, lý do, số lượng và tiền hoàn. | 39,939 | 7 | 2,281,456 byte (2.18 MiB) |
| `reviews.csv` | Đánh giá sản phẩm gắn với đơn và khách hàng, gồm ngày, điểm và tiêu đề. | 113,551 | 7 | 6,791,414 byte (6.48 MiB) |
| `shipments_realistic.csv` | Thông tin giao vận theo đơn, kết hợp sự kiện giao hàng với hồ sơ người giao/đơn vị vận chuyển. | 566,067 | 22 | 99,635,541 byte (95.02 MiB) |
| `tf.json` | Tập dữ liệu JSON về lưu lượng truy cập; cần đối chiếu ngày và nguồn với web_traffic.csv trước khi ghép. | 1,000 | 7 | 230,151 byte (0.22 MiB) |
| `web_traffic.csv` | Lưu lượng truy cập website theo ngày và nguồn truy cập. | 3,652 | 7 | 208,722 byte (0.20 MiB) |

### Nhóm dữ liệu theo nghiệp vụ

- **Khách hàng và địa lý:** `customers.csv`, `geography.csv`.
- **Đơn hàng và bán hàng:** `orders_enriched.csv`, `order_items.csv`, `payments.csv`.
- **Danh mục và khuyến mãi:** `products.csv`, `promotions.csv`.
- **Hậu mãi:** `returns.csv`, `reviews.csv`.
- **Vận hành:** `inventory.csv`, `shipments_realistic.csv`.
- **Phân tích kênh số:** `web_traffic.csv`.
- **Các bản JSON song song:** `epd.json`, `eprom.json`, `tf.json`; cần kiểm tra phiên bản/phạm vi trước khi ghép với các CSV tên tương ứng.

## Bất thường và điểm cần xác minh

1. **Cao — thời gian đăng ký khách hàng:** 477,453/646,945 đơn hàng (73.80%) có ngày đặt trước `signup_date` của khách hàng. Điều này không nhất quán nếu `signup_date` là ngày tạo hồ sơ lần đầu; cần xác minh ý nghĩa cột hoặc nguồn ngày.
2. **Cao — thời gian nhân viên giao hàng:** 519,276/566,067 lô giao hàng (91.73%) có `join_date` của shipper sau `ship_date`. Phạm vi ngày gia nhập kéo đến 2026 trong khi sự kiện giao hàng kết thúc năm 2022; cần xác minh đây là ngày tham chiếu của hồ sơ hay lỗi ghép.
3. **Cao — mã sản phẩm trong epd.json:** có 2 bản ghi thiếu/để trống `product_id`; các bản ghi này không thể liên kết tin cậy theo mã.
4. **Trung bình — phiên bản danh mục sản phẩm:** products.csv có 2,412 mã khác nhau, epd.json có 997 mã hợp lệ; giao nhau 997. Hai tệp không phải hai bản sao cùng phạm vi, không nên thay thế/ghép toàn bộ nếu chưa xác định phiên bản.
5. **Trung bình — phiên bản khuyến mãi:** promotions.csv có 50 mã, eprom.json có 1,000 mã hợp lệ và không có mã giao nhau. Không dùng hai nguồn như cùng một danh mục khuyến mãi nếu chưa chuẩn hóa/mapping mã.
6. **Trung bình — phiên bản lưu lượng truy cập:** web_traffic.csv có 3,652 ngày, tf.json có 1,000 giá trị ngày (998 giá trị trùng); tf.json có 2 giá trị `date` không phân tích được thành ngày. Hai tệp có phạm vi khác nhau.
7. **Cần xác nhận — dòng hàng lặp cặp đơn/sản phẩm:** có 16 dòng vượt số khóa duy nhất cho cặp `(order_id, product_id)` xuất hiện nhiều lần trong order_items.csv. Điều này không nhất thiết là lỗi nếu một đơn có nhiều dòng/giá cho cùng sản phẩm; cần xác nhận khóa nghiệp vụ của bảng chi tiết.
8. **Phạm vi tồn kho:** inventory.csv có 1,624 mã sản phẩm khác nhau, trong đó 1,624/2,412 mã thuộc products.csv. Phần danh mục không có bản ghi tồn kho có thể là sản phẩm không được theo dõi trong giai đoạn này.

### Kiểm tra liên kết giữa các bảng

| Liên kết | Bản ghi không tìm thấy khóa cha |
|---|---:|
| `orders_enriched.csv.customer_id` → `customers.csv.customer_id` | 0 |
| `orders_enriched.csv.zip` → `geography.csv.zip` | 0 |
| `order_items.csv.order_id` → `orders_enriched.csv.order_id` | 0 |
| `order_items.csv.product_id` → `products.csv.product_id` | 0 |
| `order_items.csv.promo_id` → `promotions.csv.promo_id` | 0 |
| `order_items.csv.promo_id_2` → `promotions.csv.promo_id` | 0 |
| `payments.csv.order_id` → `orders_enriched.csv.order_id` | 0 |
| `returns.csv.order_id` → `orders_enriched.csv.order_id` | 0 |
| `returns.csv.product_id` → `products.csv.product_id` | 0 |
| `reviews.csv.order_id` → `orders_enriched.csv.order_id` | 0 |
| `reviews.csv.product_id` → `products.csv.product_id` | 0 |
| `reviews.csv.customer_id` → `customers.csv.customer_id` | 0 |
| `shipments_realistic.csv.order_id` → `orders_enriched.csv.order_id` | 0 |
| `inventory.csv.product_id` → `products.csv.product_id` | 0 |

Đối chiếu các trường địa lý được làm giàu trong orders_enriched.csv với geography.csv: 0 dòng không khớp.
Đối chiếu `payment_method` giữa orders_enriched.csv và payments.csv: 0 dòng không khớp.

### Kiểm tra miền giá trị cơ bản

| Trường | Phạm vi kiểm tra | Ngoài phạm vi |
|---|---:|---:|
| `reviews.csv.rating` | 1–5 | 0 |
| `inventory.csv.fill_rate` | 0–1 | 0 |
| `inventory.csv.sell_through_rate` | 0–1 | 0 |
| `web_traffic.csv.bounce_rate` | 0–1 | 0 |
| `order_items.csv.quantity` | ≥ 1 | 0 |
| `order_items.csv.unit_price` | ≥ 0 | 0 |
| `order_items.csv.discount_amount` | ≥ 0 | 0 |
| `payments.csv.payment_value` | ≥ 0 | 0 |
| `payments.csv.installments` | ≥ 1 | 0 |
| `products.csv.price` | ≥ 0 | 0 |
| `products.csv.cogs` | ≥ 0 | 0 |
| `returns.csv.return_quantity` | ≥ 1 | 0 |
| `returns.csv.refund_amount` | ≥ 0 | 0 |
| `shipments_realistic.csv.shipping_fee` | ≥ 0 | 0 |
| `shipments_realistic.csv.shipper_rating` | 0–5 | 0 |
| `shipments_realistic.csv.delivery_success_rate` | 0–100 | 0 |
| `shipments_realistic.csv.shipper_age` | 18–100 | 0 |

## Mô tả chi tiết cột

Các số min/max/trung bình chỉ có ý nghĩa thống kê theo giá trị hiện có; không thay thế định nghĩa nghiệp vụ. Tỷ lệ trống tính trên số bản ghi của tệp.

### `customers.csv`

- **Chức năng:** Hồ sơ khách hàng: mã khách hàng, địa chỉ/địa lý, ngày đăng ký và nhóm nhân khẩu học/kênh tiếp cận.
- **Kích thước tệp:** 7,079,679 byte; **encoding:** utf-8-sig; **số dòng:** 121,930; **số cột:** 7.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Khác biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `customer_id` | Mã khách hàng | integer | 0 (0.00%) | 121,930 | 1 | 157,563 | 78,736.8987 | 6 ký tự |
| `zip` | Mã ZIP/khu vực địa lý | integer | 0 (0.00%) | 31,491 | 1,001 | 99,950 | 50,990.1656 | 5 ký tự |
| `city` | Thành phố | string | 0 (0.00%) | 42 | — | — | — | 19 ký tự |
| `signup_date` | Ngày đăng ký khách hàng | date | 0 (0.00%) | 3,941 | 2012-01-17 | 2022-12-31 | — | 10 ký tự |
| `gender` | Giới tính theo hồ sơ | string | 0 (0.00%) | 3 | — | — | — | 10 ký tự |
| `age_group` | Nhóm tuổi khách hàng | string | 0 (0.00%) | 5 | — | — | — | 5 ký tự |
| `acquisition_channel` | Kênh thu hút khách hàng | string | 0 (0.00%) | 6 | — | — | — | 14 ký tự |

### `epd.json`

- **Chức năng:** Tập dữ liệu JSON có cấu trúc thuộc tính sản phẩm; cần đối chiếu phiên bản với products.csv trước khi ghép.
- **Kích thước tệp:** 224,069 byte; **encoding:** UTF-8 JSON; **số dòng:** 1,000; **số cột:** 8.
- **Khóa ứng viên `product_id` thiếu/trùng:** 3.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Khác biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `product_id` | Mã sản phẩm | integer | 2 (0.20%) | 997 | 1 | 1,000 | 501.1834 | 9 ký tự |
| `product_name` | Tên sản phẩm | string | 0 (0.00%) | 959 | — | — | — | 17 ký tự |
| `category` | Danh mục sản phẩm/nhóm áp dụng | string | 0 (0.00%) | 6 | — | — | — | 11 ký tự |
| `segment` | Phân khúc sản phẩm | string | 0 (0.00%) | 8 | — | — | — | 11 ký tự |
| `size` | Kích cỡ sản phẩm | string | 0 (0.00%) | 4 | — | — | — | 2 ký tự |
| `color` | Màu sản phẩm | string | 0 (0.00%) | 10 | — | — | — | 6 ký tự |
| `price` | Giá bán | mixed | 0 (0.00%) | 909 | — | — | — | 18 ký tự |
| `cogs` | Giá vốn hàng bán | number | 0 (0.00%) | 996 | 6.8905 | 30,319.38 | 3,951.8959 | 18 ký tự |

### `eprom.json`

- **Chức năng:** Tập dữ liệu JSON về chương trình khuyến mãi; cần đối chiếu phiên bản với promotions.csv trước khi ghép.
- **Kích thước tệp:** 324,919 byte; **encoding:** UTF-8 JSON; **số dòng:** 1,000; **số cột:** 10.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Khác biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `promo_id` | Mã khuyến mãi | string | 0 (0.00%) | 1,000 | — | — | — | 21 ký tự |
| `promo_name` | Tên chương trình khuyến mãi | string | 2 (0.20%) | 50 | — | — | — | 18 ký tự |
| `promo_type` | Loại hình khuyến mãi | string | 0 (0.00%) | 2 | — | — | — | 10 ký tự |
| `discount_value` | Giá trị hoặc tỷ lệ giảm | mixed | 0 (0.00%) | 10 | — | — | — | 14 ký tự |
| `start_date` | Ngày bắt đầu hiệu lực | date | 0 (0.00%) | 51 | 2013-01-31 | 2026-12-31 | — | 10 ký tự |
| `end_date` | Ngày kết thúc hiệu lực | date | 0 (0.00%) | 51 | 2013-03-01 | 2026-01-01 | — | 10 ký tự |
| `applicable_category` | Danh mục sản phẩm áp dụng | string | 783 (78.30%) | 2 | — | — | — | 10 ký tự |
| `promo_channel` | Kênh áp dụng khuyến mãi | string | 0 (0.00%) | 6 | — | — | — | 12 ký tự |
| `stackable_flag` | Cờ cho biết có thể cộng dồn khuyến mãi | integer | 0 (0.00%) | 2 | 0 | 1 | 0.228 | 1 ký tự |
| `min_order_value` | Giá trị đơn hàng tối thiểu để áp dụng | integer | 0 (0.00%) | 5 | 0 | 200,000 | 47,250 | 6 ký tự |

### `geography.csv`

- **Chức năng:** Danh mục địa lý ánh xạ mã ZIP đến thành phố, vùng và quận/huyện.
- **Kích thước tệp:** 1,402,281 byte; **encoding:** utf-8-sig; **số dòng:** 39,948; **số cột:** 4.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Khác biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `zip` | Mã ZIP/khu vực địa lý | integer | 0 (0.00%) | 39,948 | 1 | 99,950 | 50,895.0847 | 5 ký tự |
| `city` | Thành phố | string | 0 (0.00%) | 42 | — | — | — | 19 ký tự |
| `region` | Vùng | string | 0 (0.00%) | 3 | — | — | — | 7 ký tự |
| `district` | Quận/huyện | string | 0 (0.00%) | 39 | — | — | — | 12 ký tự |

### `inventory.csv`

- **Chức năng:** Ảnh chụp tồn kho theo ngày và sản phẩm; có số lượng, chỉ số cung ứng và cờ cảnh báo.
- **Kích thước tệp:** 5,668,678 byte; **encoding:** utf-8-sig; **số dòng:** 60,247; **số cột:** 17.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Khác biệt | Min | Max | Trung bình | Dài tối đa |
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
| `year` | Năm của kỳ ghi nhận tồn kho | integer | 0 (0.00%) | 11 | 2,012 | 2,022 | 2,017.2228 | 4 ký tự |
| `month` | Tháng của kỳ ghi nhận tồn kho | integer | 0 (0.00%) | 12 | 1 | 12 | 6.6173 | 2 ký tự |

### `order_items.csv`

- **Chức năng:** Chi tiết dòng hàng trong đơn: sản phẩm, số lượng, đơn giá, chiết khấu và mã khuyến mãi.
- **Kích thước tệp:** 23,942,735 byte; **encoding:** utf-8-sig; **số dòng:** 714,669; **số cột:** 7.
- **Khóa ứng viên `order_id + product_id` thiếu/trùng:** 16.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Khác biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `order_id` | Mã đơn hàng | integer | 0 (0.00%) | 646,945 | 1 | 834,397 | 411,615.0766 | 6 ký tự |
| `product_id` | Mã sản phẩm | integer | 0 (0.00%) | 1,598 | 1 | 2,412 | 1,234.9314 | 4 ký tự |
| `quantity` | Số lượng sản phẩm | integer | 0 (0.00%) | 8 | 1 | 8 | 4.496 | 1 ký tự |
| `unit_price` | Đơn giá | number | 0 (0.00%) | 501,330 | 392.57 | 43,056 | 5,114.6902 | 8 ký tự |
| `discount_amount` | Số tiền chiết khấu | number | 0 (0.00%) | 204,449 | 0 | 35,235.47 | 1,048.8874 | 8 ký tự |
| `promo_id` | Mã khuyến mãi | string | 438,353 (61.34%) | 50 | — | — | — | 10 ký tự |
| `promo_id_2` | Mã khuyến mãi bổ sung | string | 714,463 (99.97%) | 2 | — | — | — | 10 ký tự |

### `orders_enriched.csv`

- **Chức năng:** Bảng đơn hàng đã làm giàu thông tin khách hàng, địa lý, thanh toán, nhân viên, trạng thái và phản hồi.
- **Kích thước tệp:** 155,195,353 byte; **encoding:** utf-8-sig; **số dòng:** 646,945; **số cột:** 17.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Khác biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `order_id` | Mã đơn hàng | integer | 0 (0.00%) | 646,945 | 1 | 834,397 | 417,189.4703 | 6 ký tự |
| `order_date` | Ngày đặt hàng | date | 0 (0.00%) | 3,833 | 2012-07-04 | 2022-12-31 | — | 10 ký tự |
| `customer_id` | Mã khách hàng | integer | 0 (0.00%) | 90,246 | 1 | 157,563 | 84,906.2035 | 6 ký tự |
| `zip` | Mã ZIP/khu vực địa lý | integer | 0 (0.00%) | 29,932 | 1,001 | 99,950 | 55,410.7404 | 5 ký tự |
| `city` | Thành phố | string | 0 (0.00%) | 42 | — | — | — | 19 ký tự |
| `region` | Vùng | string | 0 (0.00%) | 3 | — | — | — | 7 ký tự |
| `district` | Quận/huyện | string | 0 (0.00%) | 39 | — | — | — | 12 ký tự |
| `order_status` | Trạng thái đơn hàng | string | 0 (0.00%) | 6 | — | — | — | 9 ký tự |
| `payment_method` | Phương thức thanh toán | string | 0 (0.00%) | 5 | — | — | — | 13 ký tự |
| `device_type` | Loại thiết bị | string | 0 (0.00%) | 3 | — | — | — | 7 ký tự |
| `order_source` | Nguồn đơn hàng | string | 0 (0.00%) | 6 | — | — | — | 14 ký tự |
| `sales_employee_id` | Mã nhân viên bán hàng | string | 0 (0.00%) | 200 | — | — | — | 7 ký tự |
| `sales_employee_name` | Tên nhân viên bán hàng | string | 0 (0.00%) | 192 | — | — | — | 16 ký tự |
| `marital_status` | Tình trạng hôn nhân trong hồ sơ | string | 0 (0.00%) | 2 | — | — | — | 10 ký tự |
| `education_level` | Trình độ học vấn trong hồ sơ | string | 0 (0.00%) | 4 | — | — | — | 11 ký tự |
| `years_experience` | Số năm kinh nghiệm | integer | 0 (0.00%) | 20 | 1 | 20 | 10.9073 | 2 ký tự |
| `comment` | Nội dung phản hồi | string | 0 (0.00%) | 18 | — | — | — | 98 ký tự |

### `payments.csv`

- **Chức năng:** Thông tin thanh toán theo đơn, gồm phương thức, số tiền và số kỳ thanh toán.
- **Kích thước tệp:** 18,383,288 byte; **encoding:** utf-8-sig; **số dòng:** 646,945; **số cột:** 4.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Khác biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `order_id` | Mã đơn hàng | integer | 0 (0.00%) | 646,945 | 1 | 834,397 | 417,189.4703 | 6 ký tự |
| `payment_method` | Phương thức thanh toán | string | 0 (0.00%) | 5 | — | — | — | 13 ký tự |
| `payment_value` | Số tiền thanh toán | number | 0 (0.00%) | 595,420 | 389.74 | 331,570.4 | 24,238.3344 | 9 ký tự |
| `installments` | Số kỳ thanh toán | integer | 0 (0.00%) | 5 | 1 | 12 | 3.4483 | 2 ký tự |

### `products.csv`

- **Chức năng:** Danh mục sản phẩm và thuộc tính thương mại như danh mục, kích cỡ, màu, giá và giá vốn.
- **Kích thước tệp:** 195,223 byte; **encoding:** utf-8-sig; **số dòng:** 2,412; **số cột:** 8.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Khác biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `product_id` | Mã sản phẩm | integer | 0 (0.00%) | 2,412 | 1 | 2,412 | 1,206.5 | 4 ký tự |
| `product_name` | Tên sản phẩm | string | 0 (0.00%) | 2,172 | — | — | — | 17 ký tự |
| `category` | Danh mục sản phẩm/nhóm áp dụng | string | 0 (0.00%) | 4 | — | — | — | 10 ký tự |
| `segment` | Phân khúc sản phẩm | string | 0 (0.00%) | 8 | — | — | — | 11 ký tự |
| `size` | Kích cỡ sản phẩm | string | 0 (0.00%) | 4 | — | — | — | 2 ký tự |
| `color` | Màu sản phẩm | string | 0 (0.00%) | 10 | — | — | — | 6 ký tự |
| `price` | Giá bán | number | 0 (0.00%) | 1,990 | 9.0566 | 40,950 | 4,928.2162 | 18 ký tự |
| `cogs` | Giá vốn hàng bán | number | 0 (0.00%) | 2,381 | 5.1838 | 38,902.5 | 3,868.3467 | 18 ký tự |

### `promotions.csv`

- **Chức năng:** Danh mục chương trình khuyến mãi, thời hạn, điều kiện, kênh và mức giảm.
- **Kích thước tệp:** 4,444 byte; **encoding:** utf-8-sig; **số dòng:** 50; **số cột:** 10.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Khác biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `promo_id` | Mã khuyến mãi | string | 0 (0.00%) | 50 | — | — | — | 10 ký tự |
| `promo_name` | Tên chương trình khuyến mãi | string | 0 (0.00%) | 50 | — | — | — | 18 ký tự |
| `promo_type` | Loại hình khuyến mãi | string | 0 (0.00%) | 2 | — | — | — | 10 ký tự |
| `discount_value` | Giá trị hoặc tỷ lệ giảm | number | 0 (0.00%) | 6 | 10 | 50 | 18.5 | 4 ký tự |
| `start_date` | Ngày bắt đầu hiệu lực | date | 0 (0.00%) | 50 | 2013-01-31 | 2022-11-18 | — | 10 ký tự |
| `end_date` | Ngày kết thúc hiệu lực | date | 0 (0.00%) | 50 | 2013-03-01 | 2022-12-31 | — | 10 ký tự |
| `applicable_category` | Danh mục sản phẩm áp dụng | string | 40 (80.00%) | 2 | — | — | — | 10 ký tự |
| `promo_channel` | Kênh áp dụng khuyến mãi | string | 0 (0.00%) | 5 | — | — | — | 12 ký tự |
| `stackable_flag` | Cờ cho biết có thể cộng dồn khuyến mãi | integer | 0 (0.00%) | 2 | 0 | 1 | 0.24 | 1 ký tự |
| `min_order_value` | Giá trị đơn hàng tối thiểu để áp dụng | integer | 0 (0.00%) | 5 | 0 | 200,000 | 46,000 | 6 ký tự |

### `returns.csv`

- **Chức năng:** Các dòng trả hàng theo đơn/sản phẩm, ngày, lý do, số lượng và tiền hoàn.
- **Kích thước tệp:** 2,281,456 byte; **encoding:** utf-8-sig; **số dòng:** 39,939; **số cột:** 7.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Khác biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `return_id` | Mã trả hàng | string | 0 (0.00%) | 39,939 | — | — | — | 10 ký tự |
| `order_id` | Mã đơn hàng | integer | 0 (0.00%) | 36,062 | 2 | 833,351 | 409,061.9842 | 6 ký tự |
| `product_id` | Mã sản phẩm | integer | 0 (0.00%) | 1,286 | 3 | 2,412 | 1,244.2327 | 4 ký tự |
| `return_date` | Ngày trả hàng | date | 0 (0.00%) | 3,806 | 2012-07-11 | 2022-12-31 | — | 10 ký tự |
| `return_reason` | Lý do trả hàng | string | 0 (0.00%) | 5 | — | — | — | 16 ký tự |
| `return_quantity` | Số lượng sản phẩm trả | integer | 0 (0.00%) | 8 | 1 | 8 | 2.7438 | 1 ký tự |
| `refund_amount` | Số tiền hoàn trả | number | 0 (0.00%) | 39,560 | 458.81 | 160,937.94 | 12,784.459 | 9 ký tự |

### `reviews.csv`

- **Chức năng:** Đánh giá sản phẩm gắn với đơn và khách hàng, gồm ngày, điểm và tiêu đề.
- **Kích thước tệp:** 6,791,414 byte; **encoding:** utf-8-sig; **số dòng:** 113,551; **số cột:** 7.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Khác biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `review_id` | Mã đánh giá | string | 0 (0.00%) | 113,551 | — | — | — | 11 ký tự |
| `order_id` | Mã đơn hàng | integer | 0 (0.00%) | 111,369 | 1 | 833,296 | 408,999.5197 | 6 ký tự |
| `product_id` | Mã sản phẩm | integer | 0 (0.00%) | 1,412 | 3 | 2,412 | 1,232.0187 | 4 ký tự |
| `customer_id` | Mã khách hàng | integer | 0 (0.00%) | 48,676 | 2 | 157,563 | 85,694.3428 | 6 ký tự |
| `review_date` | Ngày đánh giá | date | 0 (0.00%) | 3,825 | 2012-07-10 | 2022-12-31 | — | 10 ký tự |
| `rating` | Điểm đánh giá | integer | 0 (0.00%) | 5 | 1 | 5 | 3.936 | 1 ký tự |
| `review_title` | Tiêu đề/nội dung ngắn của đánh giá | string | 0 (0.00%) | 18 | — | — | — | 23 ký tự |

### `shipments_realistic.csv`

- **Chức năng:** Thông tin giao vận theo đơn, kết hợp sự kiện giao hàng với hồ sơ người giao/đơn vị vận chuyển.
- **Kích thước tệp:** 99,635,541 byte; **encoding:** utf-8-sig; **số dòng:** 566,067; **số cột:** 22.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Khác biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `shipper_id` | Mã người/đơn vị giao hàng | string | 0 (0.00%) | 80 | — | — | — | 8 ký tự |
| `order_id` | Mã đơn hàng | integer | 0 (0.00%) | 566,067 | 1 | 834,325 | 415,816.8697 | 6 ký tự |
| `ship_date` | Ngày gửi hàng | date | 0 (0.00%) | 3,831 | 2012-07-04 | 2022-12-29 | — | 10 ký tự |
| `delivery_date` | Ngày giao hàng | date | 0 (0.00%) | 3,831 | 2012-07-06 | 2022-12-31 | — | 10 ký tự |
| `shipping_fee` | Phí vận chuyển | number | 0 (0.00%) | 1,856 | 0 | 32 | 4.9629 | 5 ký tự |
| `shipper_company` | Đơn vị vận chuyển | string | 0 (0.00%) | 8 | — | — | — | 14 ký tự |
| `shipper_vehicle` | Loại phương tiện giao hàng | string | 0 (0.00%) | 3 | — | — | — | 9 ký tự |
| `shipper_experience_years` | Số năm kinh nghiệm người giao hàng | integer | 0 (0.00%) | 12 | 1 | 12 | 7.6285 | 2 ký tự |
| `shipper_rating` | Điểm đánh giá người giao hàng | number | 0 (0.00%) | 9 | 4.2 | 5 | 4.6451 | 3 ký tự |
| `delivery_success_rate` | Tỷ lệ giao hàng thành công (thang dữ liệu hiện có) | number | 0 (0.00%) | 42 | 95.1 | 99.9 | 97.5118 | 4 ký tự |
| `average_delivery_time` | Thời gian giao hàng trung bình theo đơn vị nguồn | integer | 0 (0.00%) | 42 | 20 | 75 | 47.646 | 2 ký tự |
| `working_shift` | Ca làm việc | string | 0 (0.00%) | 3 | — | — | — | 9 ký tự |
| `join_date` | Ngày gia nhập của người giao hàng | date | 0 (0.00%) | 80 | 2018-01-12 | 2026-03-17 | — | 10 ký tự |
| `shipper_name` | Tên người giao hàng | string | 0 (0.00%) | 73 | — | — | — | 18 ký tự |
| `shipper_phone` | Số điện thoại liên hệ người giao hàng | integer | 0 (0.00%) | 80 | 900,482,857 | 999,125,359 | 950,690,098.4743 | 9 ký tự |
| `shipper_gender` | Giới tính người giao hàng | string | 0 (0.00%) | 2 | — | — | — | 6 ký tự |
| `shipper_age` | Tuổi người giao hàng | integer | 0 (0.00%) | 27 | 24 | 55 | 41.7048 | 2 ký tự |
| `shipper_marital_status` | Tình trạng hôn nhân người giao hàng | string | 0 (0.00%) | 2 | — | — | — | 7 ký tự |
| `shipper_education` | Trình độ học vấn người giao hàng | string | 0 (0.00%) | 3 | — | — | — | 11 ký tự |
| `city` | Thành phố | string | 0 (0.00%) | 34 | — | — | — | 19 ký tự |
| `region` | Vùng | string | 0 (0.00%) | 3 | — | — | — | 7 ký tự |
| `district` | Quận/huyện | string | 0 (0.00%) | 35 | — | — | — | 12 ký tự |

### `tf.json`

- **Chức năng:** Tập dữ liệu JSON về lưu lượng truy cập; cần đối chiếu ngày và nguồn với web_traffic.csv trước khi ghép.
- **Kích thước tệp:** 230,151 byte; **encoding:** UTF-8 JSON; **số dòng:** 1,000; **số cột:** 7.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Khác biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `date` | Ngày ghi nhận | mixed | 0 (0.00%) | 1,000 | — | — | — | 10 ký tự |
| `sessions` | Số phiên truy cập | mixed | 1 (0.10%) | 986 | — | — | — | 9 ký tự |
| `unique_visitors` | Số khách truy cập duy nhất | mixed | 0 (0.00%) | 980 | — | — | — | 7 ký tự |
| `page_views` | Số lượt xem trang | integer | 0 (0.00%) | 997 | 31,482 | 275,560 | 109,166.708 | 6 ký tự |
| `bounce_rate` | Tỷ lệ thoát | number | 0 (0.00%) | 258 | 0.0032 | 0.0058 | 0.0045 | 7 ký tự |
| `avg_session_duration_sec` | Thời lượng phiên trung bình (giây) | number | 0 (0.00%) | 834 | 100.2 | 319.8 | 206.5755 | 5 ký tự |
| `traffic_source` | Nguồn truy cập | string | 1 (0.10%) | 999 | — | — | — | 30 ký tự |

### `web_traffic.csv`

- **Chức năng:** Lưu lượng truy cập website theo ngày và nguồn truy cập.
- **Kích thước tệp:** 208,722 byte; **encoding:** utf-8-sig; **số dòng:** 3,652; **số cột:** 7.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Khác biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `date` | Ngày ghi nhận | date | 0 (0.00%) | 3,652 | 2013-01-01 | 2022-12-31 | — | 10 ký tự |
| `sessions` | Số phiên truy cập | integer | 0 (0.00%) | 3,447 | 7,973 | 50,947 | 25,041.7681 | 5 ký tự |
| `unique_visitors` | Số khách truy cập duy nhất | integer | 0 (0.00%) | 3,382 | 6,136 | 40,430 | 19,031.4044 | 5 ký tự |
| `page_views` | Số lượt xem trang | integer | 0 (0.00%) | 3,620 | 30,451 | 275,560 | 108,615.2245 | 6 ký tự |
| `bounce_rate` | Tỷ lệ thoát | number | 0 (0.00%) | 261 | 0.0032 | 0.0058 | 0.0045 | 7 ký tự |
| `avg_session_duration_sec` | Thời lượng phiên trung bình (giây) | number | 0 (0.00%) | 1,771 | 100.1 | 319.9 | 210.2832 | 5 ký tự |
| `traffic_source` | Nguồn truy cập | string | 0 (0.00%) | 6 | — | — | — | 14 ký tự |

## Phạm vi và hạn chế

- Báo cáo mô tả dữ liệu thực tế và áp dụng các kiểm tra cấu trúc, khóa, miền giá trị và thời gian nêu trên; không thể xác nhận ý nghĩa nghiệp vụ nếu chưa có data contract.
- Các tệp JSON `epd.json`, `eprom.json`, `tf.json` có thể là bản trích xuất/biến thể riêng. Khác biệt về số lượng hoặc mã chưa đủ để kết luận tệp nào là nguồn chuẩn.
- Các giá trị thông tin cá nhân như số điện thoại và ví dụ tên/comment không được đưa vào tài liệu.
