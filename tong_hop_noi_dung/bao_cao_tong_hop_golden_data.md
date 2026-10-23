# Báo cáo tổng hợp dữ liệu `DAAI_N1.4/golden_data`

- **Thư mục nguồn:** `D:\TH_DA&AI\DAAI_N1.4\golden_data`
- **Số bảng:** 6
- **Tổng số bản ghi:** 882,976
- **Tổng dung lượng:** 152,861,228 byte (145.78 MiB)
- **Kiểu dữ liệu:** suy luận từ CSV; các tệp không khai báo schema SQL. Mã định danh dạng số nên được xem là khóa/mã, không phải đại lượng đo.

## Khái niệm mô hình và chức năng

Đây là mô hình dữ liệu dạng sao (star schema): các bảng `Dim_*` mô tả thực thể/phân loại dùng để lọc và nhóm phân tích; `Fact_Sales` lưu các giao dịch và chỉ số đo lường.

**Grain (độ chi tiết) dự kiến của Fact_Sales:** một dòng cho một cặp `order_id` + `product_id` trong đơn hàng. Khóa này được kiểm tra như khóa ứng viên.

| Bảng | Khái niệm / chức năng | Grain hoặc khóa ứng viên | Dòng | Cột | Kích thước |
|---|---|---|---:|---:|---:|
| `Dim_Customer.csv` | Dimension khách hàng: hồ sơ khách hàng, ngày đăng ký, nhân khẩu học, kênh thu hút và địa lý. | một dòng / `customer_id` | 121,930 | 9 | 18,814,588 byte (17.94 MiB) |
| `Dim_Date.csv` | Dimension thời gian dạng lịch, cung cấp thuộc tính ngày/tháng/quý/năm để phân tích và lọc theo thời gian. | một dòng / `date_key` | 3,833 | 10 | 393,466 byte (0.38 MiB) |
| `Dim_Employee.csv` | Dimension nhân viên bán hàng: mã nhân viên và một số thông tin hồ sơ phục vụ phân tích kết quả bán hàng. | một dòng / `sales_employee_id` | 200 | 5 | 11,320 byte (0.01 MiB) |
| `Dim_Geography.csv` | Dimension địa lý: ánh xạ ZIP sang thành phố, vùng và quận/huyện. | một dòng / `zip` | 39,948 | 4 | 2,804,564 byte (2.67 MiB) |
| `Dim_Product.csv` | Dimension sản phẩm: tên, danh mục, phân khúc và thuộc tính thương mại của sản phẩm. | một dòng / `product_id` | 2,412 | 8 | 391,700 byte (0.37 MiB) |
| `Fact_Sales.csv` | Fact giao dịch bán hàng ở cấp dòng sản phẩm trong đơn hàng; chứa khóa liên kết đến các dimension và các chỉ số số lượng/giá trị bán. | một dòng / đơn hàng + sản phẩm | 714,653 | 14 | 130,445,590 byte (124.40 MiB) |

### Ý nghĩa chung của các chỉ số bán hàng

- `quantity`: số đơn vị sản phẩm trong dòng giao dịch.
- `unit_price`: đơn giá được ghi nhận cho dòng hàng.
- `gross_amount`: giá trị trước chiết khấu; kiểm tra đối chiếu với `quantity × unit_price`.
- `discount_amount`: số tiền giảm giá.
- `net_amount`: giá trị sau chiết khấu; kiểm tra đối chiếu với `gross_amount − discount_amount`.
- `promo_count` và `has_promotion`: số lượng/cờ khuyến mãi gắn với dòng bán.
- Các diễn giải này dựa trên tên cột và phép đối chiếu số liệu; cần data contract để xác nhận quy tắc kế toán/kinh doanh chính thức.

## Điểm bất thường và kết quả kiểm tra

1. **Cần xác minh — ngày giao dịch trước ngày đăng ký khách hàng:** 531,541/714,653 dòng fact (74.38%) có date_key trước signup_date trong Dim_Customer. Nếu signup_date là ngày tạo hồ sơ lần đầu thì đây là bất nhất thời gian; nếu mang nghĩa khác cần ghi rõ định nghĩa.
2. **Cần xác nhận quy tắc ghi nhận doanh thu:** Fact_Sales có net_amount dương ở các trạng thái không phải `delivered` (`cancelled` 1,466,375,517.73, `created` 184,333,229.67, `paid` 335,066,412.66, `returned` 878,459,482.95, `shipped` 342,548,651.42). Nếu fact được dùng làm doanh thu đã hoàn tất, cần lọc/điều chỉnh trạng thái hoặc xác nhận cách xử lý giao dịch chưa giao/đã hủy/trả.

### Liên kết khóa

| Liên kết | Giá trị mồ côi |
|---|---:|
| `Fact_Sales.csv.customer_id` → `Dim_Customer.csv.customer_id` | 0 |
| `Fact_Sales.csv.date_key` → `Dim_Date.csv.date_key` | 0 |
| `Fact_Sales.csv.sales_employee_id` → `Dim_Employee.csv.sales_employee_id` | 0 |
| `Fact_Sales.csv.zip` → `Dim_Geography.csv.zip` | 0 |
| `Fact_Sales.csv.product_id` → `Dim_Product.csv.product_id` | 0 |
| `Dim_Customer.csv.zip` → `Dim_Geography.csv.zip` | 0 |

### Phân bố trạng thái đơn hàng trong fact

| order_status | Dòng | Tổng net_amount |
|---|---:|---:|
| `cancelled` | 65,673 | 1,466,375,517.73 |
| `created` | 7,993 | 184,333,229.67 |
| `delivered` | 570,874 | 12,698,959,845.42 |
| `paid` | 14,987 | 335,066,412.66 |
| `returned` | 40,032 | 878,459,482.95 |
| `shipped` | 15,094 | 342,548,651.42 |

## Mô tả chi tiết bảng và cột

Trống là chuỗi rỗng trong CSV. Min/max/trung bình được tính trên giá trị hiện có; trung bình với mã định danh chỉ là thống kê kỹ thuật, không mang ý nghĩa nghiệp vụ.

### `Dim_Customer.csv`

- **Chức năng:** Dimension khách hàng: hồ sơ khách hàng, ngày đăng ký, nhân khẩu học, kênh thu hút và địa lý.
- **Số dòng/cột:** 121,930/9; **dung lượng:** 18,814,588 byte; **encoding:** utf-16.
- **Khóa ứng viên:** `customer_id`; **dòng có khóa trống/trùng:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `customer_id` | Mã khách hàng | integer | 0 (0.00%) | 121,930 | 1 | 157,563 | 78,736.8987 | 6 ký tự |
| `zip` | Mã ZIP/khu vực địa lý | integer | 0 (0.00%) | 31,491 | 1,001 | 99,950 | 50,990.1656 | 5 ký tự |
| `signup_date` | Ngày đăng ký khách hàng | date | 0 (0.00%) | 3,941 | 2012-01-17 | 2022-12-31 | — | 10 ký tự |
| `gender` | Giới tính theo hồ sơ | string | 0 (0.00%) | 3 | — | — | — | 10 ký tự |
| `age_group` | Nhóm tuổi khách hàng | string | 0 (0.00%) | 5 | — | — | — | 5 ký tự |
| `acquisition_channel` | Kênh thu hút khách hàng | string | 0 (0.00%) | 6 | — | — | — | 14 ký tự |
| `city` | Thành phố | string | 0 (0.00%) | 42 | — | — | — | 19 ký tự |
| `region` | Vùng | string | 0 (0.00%) | 3 | — | — | — | 7 ký tự |
| `district` | Quận/huyện | string | 0 (0.00%) | 39 | — | — | — | 12 ký tự |

### `Dim_Date.csv`

- **Chức năng:** Dimension thời gian dạng lịch, cung cấp thuộc tính ngày/tháng/quý/năm để phân tích và lọc theo thời gian.
- **Số dòng/cột:** 3,833/10; **dung lượng:** 393,466 byte; **encoding:** utf-16.
- **Khóa ứng viên:** `date_key`; **dòng có khóa trống/trùng:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `date_key` | Khóa ngày theo định dạng YYYY-MM-DD | date | 0 (0.00%) | 3,833 | 2012-07-04 | 2022-12-31 | — | 10 ký tự |
| `year` | Năm | integer | 0 (0.00%) | 11 | 2,012 | 2,022 | 2,017.2405 | 4 ký tự |
| `quarter` | Quý trong năm | integer | 0 (0.00%) | 4 | 1 | 4 | 2.556 | 1 ký tự |
| `month` | Tháng | integer | 0 (0.00%) | 12 | 1 | 12 | 6.6658 | 2 ký tự |
| `month_name` | Tên tháng | string | 0 (0.00%) | 12 | — | — | — | 9 ký tự |
| `day` | Ngày trong tháng | integer | 0 (0.00%) | 31 | 1 | 31 | 15.7438 | 2 ký tự |
| `day_of_week` | Thứ trong tuần theo quy ước của dữ liệu | integer | 0 (0.00%) | 7 | 0 | 6 | 3.0005 | 1 ký tự |
| `day_name` | Tên thứ trong tuần | string | 0 (0.00%) | 7 | — | — | — | 9 ký tự |
| `is_weekend` | Cờ ngày cuối tuần | integer | 0 (0.00%) | 2 | 0 | 1 | 0.2857 | 1 ký tự |
| `year_month` | Khóa tháng theo định dạng YYYY-MM | string | 0 (0.00%) | 126 | — | — | — | 7 ký tự |

### `Dim_Employee.csv`

- **Chức năng:** Dimension nhân viên bán hàng: mã nhân viên và một số thông tin hồ sơ phục vụ phân tích kết quả bán hàng.
- **Số dòng/cột:** 200/5; **dung lượng:** 11,320 byte; **encoding:** utf-8-sig.
- **Khóa ứng viên:** `sales_employee_id`; **dòng có khóa trống/trùng:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `sales_employee_id` | Mã nhân viên bán hàng | string | 0 (0.00%) | 200 | — | — | — | 7 ký tự |
| `name` | Tên nhân viên | string | 0 (0.00%) | 192 | — | — | — | 16 ký tự |
| `years_experience` | Số năm kinh nghiệm | integer | 0 (0.00%) | 20 | 1 | 20 | 10.91 | 2 ký tự |
| `education_level` | Trình độ học vấn | string | 0 (0.00%) | 4 | — | — | — | 11 ký tự |
| `marital_status` | Tình trạng hôn nhân | string | 0 (0.00%) | 2 | — | — | — | 10 ký tự |

### `Dim_Geography.csv`

- **Chức năng:** Dimension địa lý: ánh xạ ZIP sang thành phố, vùng và quận/huyện.
- **Số dòng/cột:** 39,948/4; **dung lượng:** 2,804,564 byte; **encoding:** utf-16.
- **Khóa ứng viên:** `zip`; **dòng có khóa trống/trùng:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `zip` | Mã ZIP/khu vực địa lý | integer | 0 (0.00%) | 39,948 | 1 | 99,950 | 50,895.0847 | 5 ký tự |
| `city` | Thành phố | string | 0 (0.00%) | 42 | — | — | — | 19 ký tự |
| `region` | Vùng | string | 0 (0.00%) | 3 | — | — | — | 7 ký tự |
| `district` | Quận/huyện | string | 0 (0.00%) | 39 | — | — | — | 12 ký tự |

### `Dim_Product.csv`

- **Chức năng:** Dimension sản phẩm: tên, danh mục, phân khúc và thuộc tính thương mại của sản phẩm.
- **Số dòng/cột:** 2,412/8; **dung lượng:** 391,700 byte; **encoding:** utf-16.
- **Khóa ứng viên:** `product_id`; **dòng có khóa trống/trùng:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `product_id` | Mã sản phẩm | integer | 0 (0.00%) | 2,412 | 1 | 2,412 | 1,206.5 | 4 ký tự |
| `product_name` | Tên sản phẩm | string | 0 (0.00%) | 2,172 | — | — | — | 17 ký tự |
| `category` | Danh mục sản phẩm | string | 0 (0.00%) | 4 | — | — | — | 10 ký tự |
| `segment` | Phân khúc sản phẩm | string | 0 (0.00%) | 8 | — | — | — | 11 ký tự |
| `size` | Kích cỡ sản phẩm | string | 0 (0.00%) | 4 | — | — | — | 2 ký tự |
| `color` | Màu sản phẩm | string | 0 (0.00%) | 10 | — | — | — | 6 ký tự |
| `price` | Giá bán niêm yết | number | 0 (0.00%) | 1,990 | 9.0566 | 40,950 | 4,928.2162 | 18 ký tự |
| `cogs` | Giá vốn hàng bán | number | 0 (0.00%) | 2,380 | 5.1838 | 38,902.5 | 3,868.3467 | 18 ký tự |

### `Fact_Sales.csv`

- **Chức năng:** Fact giao dịch bán hàng ở cấp dòng sản phẩm trong đơn hàng; chứa khóa liên kết đến các dimension và các chỉ số số lượng/giá trị bán.
- **Số dòng/cột:** 714,653/14; **dung lượng:** 130,445,590 byte; **encoding:** utf-16.
- **Khóa ứng viên:** `order_id+product_id`; **dòng có khóa trống/trùng:** 0.

| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `order_id` | Mã đơn hàng | integer | 0 (0.00%) | 646,945 | 1 | 834,397 | 411,614.7584 | 6 ký tự |
| `product_id` | Mã sản phẩm | integer | 0 (0.00%) | 1,598 | 1 | 2,412 | 1,234.9269 | 4 ký tự |
| `date_key` | Khóa ngày theo định dạng YYYY-MM-DD | date | 0 (0.00%) | 3,833 | 2012-07-04 | 2022-12-31 | — | 10 ký tự |
| `customer_id` | Mã khách hàng | integer | 0 (0.00%) | 90,246 | 1 | 157,563 | 85,707.6957 | 6 ký tự |
| `sales_employee_id` | Mã nhân viên bán hàng | string | 0 (0.00%) | 200 | — | — | — | 7 ký tự |
| `zip` | Mã ZIP/khu vực địa lý | integer | 0 (0.00%) | 29,932 | 1,001 | 99,950 | 55,905.6434 | 5 ký tự |
| `order_status` | Trạng thái đơn hàng | string | 0 (0.00%) | 6 | — | — | — | 9 ký tự |
| `quantity` | Số lượng sản phẩm trong dòng giao dịch | integer | 0 (0.00%) | 14 | 1 | 15 | 4.4961 | 2 ký tự |
| `unit_price` | Đơn giá trong giao dịch | number | 0 (0.00%) | 492,775 | 392.57 | 15,324.06 | 5,081.5124 | 8 ký tự |
| `discount_amount` | Số tiền chiết khấu | number | 0 (0.00%) | 107,010 | 0 | 4,838.15 | 584.6738 | 7 ký tự |
| `gross_amount` | Giá trị trước chiết khấu | number | 0 (0.00%) | 624,656 | 442.89 | 122,592.48 | 22,841.2698 | 18 ký tự |
| `net_amount` | Giá trị sau chiết khấu | number | 0 (0.00%) | 643,606 | 389.74 | 122,592.48 | 22,256.5961 | 18 ký tự |
| `promo_count` | Số chương trình khuyến mãi áp dụng | integer | 0 (0.00%) | 2 | 0 | 1 | 0.3866 | 1 ký tự |
| `has_promotion` | Cờ cho biết dòng hàng có khuyến mãi | integer | 0 (0.00%) | 2 | 0 | 1 | 0.3866 | 1 ký tự |

## Phạm vi và hạn chế

- Mô hình grain và định nghĩa nghiệp vụ được suy luận từ tên/cấu trúc cột và dữ liệu quan sát; hãy đối chiếu tài liệu thiết kế kho dữ liệu trước khi dùng làm quy tắc chính thức.
- Kiểu dữ liệu báo cáo là kiểu suy luận từ CSV, không phải kiểu vật lý của bảng SQL.
- Báo cáo không phát hành dữ liệu mẫu chứa thông tin cá nhân.
