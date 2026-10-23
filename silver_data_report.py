import csv
import math
from collections import Counter
from datetime import date
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "silver_data"
OUTPUT_DIR = PROJECT_DIR / "tong_hop_noi_dung"
REPORT_PATH = OUTPUT_DIR / "bao_cao_tong_hop_silver_data.md"

TABLE_DESCRIPTIONS = {
    "CUSTOMER_silver.csv": (
        "Hồ sơ khách hàng đã chuẩn hóa, gồm địa chỉ ZIP, ngày đăng ký, nhóm nhân khẩu học "
        "và kênh thu hút khách hàng."
    ),
    "geography.csv": "Danh mục địa lý ánh xạ ZIP sang thành phố, vùng và quận/huyện.",
    "inventory_silver.csv": (
        "Ảnh chụp tồn kho theo ngày và sản phẩm; gồm lượng tồn/nhập/bán, chỉ số cung ứng, "
        "thuộc tính sản phẩm và các cờ outlier đã tạo trong xử lý silver."
    ),
    "ORDER_ITEM_PROMOTION_silver.csv": (
        "Bảng liên kết giữa dòng đơn hàng/sản phẩm và chương trình khuyến mãi được áp dụng."
    ),
    "ORDER_ITEMS_silver.csv": (
        "Chi tiết dòng hàng theo đơn và sản phẩm, gồm số lượng, đơn giá và chiết khấu."
    ),
    "ORDER_silver.csv": (
        "Thông tin đơn hàng ở cấp một dòng/đơn; bao gồm ngày, khách hàng, trạng thái, "
        "kênh/thiết bị, nhân viên bán hàng và comment."
    ),
    "payment.csv": "Thông tin thanh toán theo đơn hàng, phương thức, giá trị và số kỳ.",
    "product.csv": "Danh mục sản phẩm cùng phân loại và thuộc tính thương mại.",
    "promotion.csv": "Danh mục chương trình khuyến mãi, thời gian, điều kiện và kênh áp dụng.",
    "returns.csv": "Sự kiện/dòng trả hàng gồm đơn, sản phẩm, ngày, lý do, số lượng và tiền hoàn.",
    "reviews.csv": "Đánh giá sản phẩm theo đơn, gồm mã đánh giá, ngày, điểm và tiêu đề.",
    "sales_employee.csv": "Danh mục nhân viên bán hàng và thông tin hồ sơ liên quan.",
    "shipment.csv": "Thông tin vận chuyển theo đơn, gồm shipper, ngày gửi/giao và phí vận chuyển.",
    "shipper.csv": "Hồ sơ người/đơn vị giao hàng, thông tin nhân khẩu học, năng lực và khu vực.",
    "web_traffic_silver.csv": (
        "Lưu lượng website theo ngày và nguồn; gồm phiên, khách truy cập, lượt xem và cờ outlier."
    ),
}

KEYS = {
    "CUSTOMER_silver.csv": [("customer_id",)],
    "geography.csv": [("zip",)],
    "inventory_silver.csv": [("snapshot_date", "product_id")],
    "ORDER_ITEM_PROMOTION_silver.csv": [("order_id", "product_id", "promo_id")],
    "ORDER_ITEMS_silver.csv": [("order_id", "product_id")],
    "ORDER_silver.csv": [("order_id",)],
    "payment.csv": [("order_id",)],
    "product.csv": [("product_id",)],
    "promotion.csv": [("promo_id",)],
    "returns.csv": [("return_id",)],
    "reviews.csv": [("review_id",)],
    "sales_employee.csv": [("sales_employee_id",)],
    "shipment.csv": [("order_id",)],
    "shipper.csv": [("shipper_id",)],
    "web_traffic_silver.csv": [("date",)],
}

INDEX_FIELDS = {
    "CUSTOMER_silver.csv": {"customer_id", "zip", "signup_date"},
    "geography.csv": {"zip"},
    "ORDER_silver.csv": {"order_id", "customer_id", "zip", "order_date", "sales_employee_id"},
    "ORDER_ITEMS_silver.csv": {"order_id", "product_id"},
    "ORDER_ITEM_PROMOTION_silver.csv": {"order_id", "product_id", "promo_id"},
    "payment.csv": {"order_id", "payment_method"},
    "product.csv": {"product_id"},
    "promotion.csv": {"promo_id"},
    "returns.csv": {"return_id", "order_id", "product_id"},
    "reviews.csv": {"review_id", "order_id", "rating"},
    "sales_employee.csv": {"sales_employee_id"},
    "shipment.csv": {"order_id", "shipper_id", "ship_date", "delivery_date"},
    "shipper.csv": {"shipper_id", "join_date", "zip"},
    "inventory_silver.csv": {"product_id"},
    "web_traffic_silver.csv": {"date"},
}

FIELD_MEANINGS = {
    "customer_id": "Mã khách hàng",
    "zip": "Mã ZIP/khu vực địa lý",
    "signup_date": "Ngày đăng ký khách hàng",
    "gender": "Giới tính theo hồ sơ",
    "age_group": "Nhóm tuổi khách hàng",
    "acquisition_channel": "Kênh thu hút khách hàng",
    "city": "Thành phố",
    "region": "Vùng",
    "district": "Quận/huyện",
    "snapshot_date": "Ngày chụp số liệu tồn kho",
    "product_id": "Mã sản phẩm",
    "stock_on_hand": "Lượng hàng tồn",
    "units_received": "Lượng hàng nhập",
    "units_sold": "Lượng hàng bán",
    "stockout_days": "Số ngày hết hàng",
    "days_of_supply": "Số ngày tồn kho đủ cung ứng",
    "fill_rate": "Tỷ lệ đáp ứng nhu cầu",
    "stockout_flag": "Cờ cảnh báo hết hàng",
    "overstock_flag": "Cờ cảnh báo tồn quá mức",
    "reorder_flag": "Cờ đề nghị đặt hàng lại",
    "sell_through_rate": "Tỷ lệ bán hết hàng",
    "stock_on_hand_is_outlier": "Cờ đánh dấu tồn kho là outlier",
    "units_received_is_outlier": "Cờ đánh dấu lượng nhập là outlier",
    "units_sold_is_outlier": "Cờ đánh dấu lượng bán là outlier",
    "days_of_supply_is_outlier": "Cờ đánh dấu ngày cung ứng là outlier",
    "year": "Năm của kỳ ghi nhận",
    "month": "Tháng của kỳ ghi nhận",
    "order_id": "Mã đơn hàng",
    "promo_id": "Mã chương trình khuyến mãi",
    "quantity": "Số lượng sản phẩm trong dòng đơn hàng",
    "unit_price": "Đơn giá sản phẩm trong đơn hàng",
    "discount_amount": "Số tiền chiết khấu",
    "order_date": "Ngày đặt hàng",
    "order_status": "Trạng thái đơn hàng",
    "device_type": "Loại thiết bị dùng để đặt hàng",
    "order_source": "Nguồn phát sinh đơn hàng",
    "sales_employee_id": "Mã nhân viên bán hàng",
    "comment": "Nội dung phản hồi gắn với đơn hàng",
    "payment_method": "Phương thức thanh toán",
    "payment_value": "Số tiền thanh toán",
    "installments": "Số kỳ thanh toán",
    "product_name": "Tên sản phẩm",
    "category": "Danh mục sản phẩm/nhóm áp dụng",
    "segment": "Phân khúc sản phẩm",
    "size": "Kích cỡ sản phẩm",
    "color": "Màu sản phẩm",
    "price": "Giá bán niêm yết",
    "cogs": "Giá vốn hàng bán",
    "promo_name": "Tên chương trình khuyến mãi",
    "promo_type": "Loại hình khuyến mãi",
    "discount_value": "Giá trị hoặc tỷ lệ giảm",
    "start_date": "Ngày bắt đầu hiệu lực",
    "end_date": "Ngày kết thúc hiệu lực",
    "applicable_category": "Danh mục sản phẩm áp dụng",
    "promo_channel": "Kênh áp dụng khuyến mãi",
    "stackable_flag": "Cờ cho biết có thể cộng dồn khuyến mãi",
    "min_order_value": "Giá trị đơn hàng tối thiểu để áp dụng",
    "return_id": "Mã sự kiện trả hàng",
    "return_date": "Ngày trả hàng",
    "return_reason": "Lý do trả hàng",
    "return_quantity": "Số lượng sản phẩm trả",
    "refund_amount": "Số tiền hoàn trả",
    "review_id": "Mã đánh giá",
    "review_date": "Ngày đánh giá",
    "rating": "Điểm đánh giá",
    "review_title": "Tiêu đề/ngắn gọn của đánh giá",
    "name": "Tên nhân viên",
    "marital_status": "Tình trạng hôn nhân",
    "education_level": "Trình độ học vấn",
    "years_experience": "Số năm kinh nghiệm",
    "shipper_id": "Mã người/đơn vị giao hàng",
    "ship_date": "Ngày gửi hàng",
    "delivery_date": "Ngày giao hàng",
    "shipping_fee": "Phí vận chuyển",
    "shipper_name": "Tên người giao hàng",
    "shipper_phone": "Số điện thoại liên hệ người giao hàng",
    "shipper_gender": "Giới tính người giao hàng",
    "shipper_age": "Tuổi người giao hàng",
    "shipper_marital_status": "Tình trạng hôn nhân người giao hàng",
    "shipper_education": "Trình độ học vấn người giao hàng",
    "shipper_company": "Đơn vị vận chuyển",
    "shipper_vehicle": "Loại phương tiện giao hàng",
    "shipper_experience_years": "Số năm kinh nghiệm người giao hàng",
    "shipper_rating": "Điểm đánh giá người giao hàng",
    "delivery_success_rate": "Tỷ lệ giao hàng thành công theo thang nguồn",
    "average_delivery_time": "Thời gian giao hàng trung bình theo đơn vị nguồn",
    "working_shift": "Ca làm việc",
    "join_date": "Ngày gia nhập người giao hàng",
    "date": "Ngày ghi nhận",
    "sessions": "Số phiên truy cập",
    "unique_visitors": "Số khách truy cập duy nhất",
    "page_views": "Số lượt xem trang",
    "bounce_rate": "Tỷ lệ thoát",
    "avg_session_duration_sec": "Thời lượng phiên trung bình (giây)",
    "traffic_source": "Nguồn truy cập",
    "page_views_is_outlier": "Cờ đánh dấu lượt xem trang là outlier",
}

RELATIONSHIPS = [
    ("ORDER_silver.csv", "customer_id", "CUSTOMER_silver.csv", "customer_id"),
    ("ORDER_silver.csv", "zip", "geography.csv", "zip"),
    ("ORDER_silver.csv", "sales_employee_id", "sales_employee.csv", "sales_employee_id"),
    ("ORDER_ITEMS_silver.csv", "order_id", "ORDER_silver.csv", "order_id"),
    ("ORDER_ITEMS_silver.csv", "product_id", "product.csv", "product_id"),
    ("ORDER_ITEM_PROMOTION_silver.csv", "order_id", "ORDER_silver.csv", "order_id"),
    ("ORDER_ITEM_PROMOTION_silver.csv", "product_id", "product.csv", "product_id"),
    ("ORDER_ITEM_PROMOTION_silver.csv", "promo_id", "promotion.csv", "promo_id"),
    ("payment.csv", "order_id", "ORDER_silver.csv", "order_id"),
    ("returns.csv", "order_id", "ORDER_silver.csv", "order_id"),
    ("returns.csv", "product_id", "product.csv", "product_id"),
    ("reviews.csv", "order_id", "ORDER_silver.csv", "order_id"),
    ("shipment.csv", "order_id", "ORDER_silver.csv", "order_id"),
    ("shipment.csv", "shipper_id", "shipper.csv", "shipper_id"),
    ("shipper.csv", "zip", "geography.csv", "zip"),
    ("inventory_silver.csv", "product_id", "product.csv", "product_id"),
]


def detect_encoding(path):
    with path.open("rb") as file:
        prefix = file.read(4)
    if prefix[:2] in (bytes([255, 254]), bytes([254, 255])):
        return "utf-16"
    return "utf-8-sig"


def read_csv(path):
    with path.open("r", encoding=detect_encoding(path), newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError(f"CSV rỗng hoặc thiếu header: {path}")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f"Header có tên cột trùng: {path}")
        for line_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"Dòng có nhiều trường hơn header tại {path.name}:{line_number}")
            yield row


def infer_type(value):
    value = value.strip()
    if not value:
        return "empty"
    if value.lower() in {"true", "false"}:
        return "boolean"
    if value.lstrip("+-").isdigit():
        return "integer"
    try:
        number = float(value)
        if math.isfinite(number):
            return "number"
    except ValueError:
        pass
    try:
        date.fromisoformat(value)
        return "date"
    except ValueError:
        return "string"


def normalize_type(types):
    if not types:
        return "empty"
    if types <= {"integer", "number"}:
        return "integer" if types == {"integer"} else "number"
    return next(iter(types)) if len(types) == 1 else "mixed"


def profile_file(path):
    row_count = 0
    columns = None
    stats = {}
    key_sets = {fields: set() for fields in KEYS[path.name]}
    key_duplicates = Counter()
    indexes = {name: set() for name in INDEX_FIELDS.get(path.name, set())}

    for row in read_csv(path):
        if columns is None:
            columns = list(row)
            stats = {
                name: {
                    "types": set(),
                    "values": set(),
                    "null_count": 0,
                    "max_length": 0,
                    "numeric_min": None,
                    "numeric_max": None,
                    "numeric_sum": 0.0,
                    "numeric_count": 0,
                    "date_min": None,
                    "date_max": None,
                }
                for name in columns
            }
        row_count += 1
        for fields, seen in key_sets.items():
            key = tuple(row[field].strip() for field in fields)
            if any(not part for part in key) or key in seen:
                key_duplicates[fields] += 1
            else:
                seen.add(key)
        for field, values in indexes.items():
            value = row[field].strip()
            if value:
                values.add(value)

        for name, raw_value in row.items():
            column = stats[name]
            value = raw_value.strip()
            if not value:
                column["null_count"] += 1
                continue
            kind = infer_type(value)
            column["types"].add(kind)
            column["values"].add(value)
            column["max_length"] = max(column["max_length"], len(raw_value))
            if kind in {"integer", "number"}:
                number = float(value)
                column["numeric_min"] = number if column["numeric_min"] is None else min(column["numeric_min"], number)
                column["numeric_max"] = number if column["numeric_max"] is None else max(column["numeric_max"], number)
                column["numeric_sum"] += number
                column["numeric_count"] += 1
            elif kind == "date":
                column["date_min"] = value if column["date_min"] is None else min(column["date_min"], value)
                column["date_max"] = value if column["date_max"] is None else max(column["date_max"], value)

    if columns is None:
        raise ValueError(f"Không có bản ghi dữ liệu trong {path}")
    column_profiles = []
    for name in columns:
        column = stats[name]
        kind = normalize_type(column["types"])
        minimum = maximum = average = ""
        if kind in {"integer", "number"} and column["numeric_count"]:
            minimum = column["numeric_min"]
            maximum = column["numeric_max"]
            average = column["numeric_sum"] / column["numeric_count"]
        elif kind == "date":
            minimum, maximum = column["date_min"], column["date_max"]
        column_profiles.append({
            "name": name,
            "type": kind,
            "null_count": column["null_count"],
            "null_pct": column["null_count"] / row_count * 100 if row_count else 0,
            "distinct": len(column["values"]),
            "min": minimum,
            "max": maximum,
            "average": average,
            "max_length": column["max_length"],
        })

    return {
        "name": path.name,
        "rows": row_count,
        "columns": column_profiles,
        "file_size": path.stat().st_size,
        "encoding": detect_encoding(path),
        "key_fields": list(key_sets),
        "key_duplicates": key_duplicates,
        "indexes": indexes,
    }


def profile_values(profiles, filename, field):
    profile = next(item for item in profiles if item["name"] == filename)
    return profile["indexes"].get(field, set())


def count_orphans(child_file, child_field, parent_values):
    return sum(
        1 for row in read_csv(DATA_DIR / child_file)
        if row[child_field].strip() and row[child_field].strip() not in parent_values
    )


def count_rows(path, predicate):
    return sum(1 for row in read_csv(path) if predicate(row))


def format_value(value):
    if value == "":
        return "—"
    if isinstance(value, float):
        return f"{value:,.4f}".rstrip("0").rstrip(".")
    return str(value)


def run_checks(profiles):
    by_name = {profile["name"]: profile for profile in profiles}
    foreign_keys = []
    for child, child_field, parent, parent_field in RELATIONSHIPS:
        missing = count_orphans(
            child,
            child_field,
            profile_values(profiles, parent, parent_field),
        )
        foreign_keys.append((child, child_field, parent, parent_field, missing))

    customers = {
        row["customer_id"]: row["signup_date"]
        for row in read_csv(DATA_DIR / "CUSTOMER_silver.csv")
    }
    orders_before_signup = count_rows(
        DATA_DIR / "ORDER_silver.csv",
        lambda row: row["order_date"] < customers[row["customer_id"]],
    )

    shippers = {
        row["shipper_id"]: row["join_date"]
        for row in read_csv(DATA_DIR / "shipper.csv")
    }
    shipments_after_join = count_rows(
        DATA_DIR / "shipment.csv",
        lambda row: row["ship_date"] < shippers[row["shipper_id"]],
    )
    delivery_before_ship = count_rows(
        DATA_DIR / "shipment.csv",
        lambda row: row["delivery_date"] < row["ship_date"],
    )

    rating_out_of_range = count_rows(
        DATA_DIR / "reviews.csv",
        lambda row: not 1 <= int(row["rating"]) <= 5,
    )
    outlier_flags = {}
    for filename, field in (
        ("inventory_silver.csv", "stock_on_hand_is_outlier"),
        ("inventory_silver.csv", "units_received_is_outlier"),
        ("inventory_silver.csv", "units_sold_is_outlier"),
        ("inventory_silver.csv", "days_of_supply_is_outlier"),
        ("web_traffic_silver.csv", "page_views_is_outlier"),
    ):
        outlier_flags[f"{filename}.{field}"] = count_rows(
            DATA_DIR / filename,
            lambda row, field=field: row[field].strip().lower() in {"true", "1", "yes"},
        )

    rate_checks = [
        ("inventory_silver.csv", "fill_rate", 0, 1),
        ("inventory_silver.csv", "sell_through_rate", 0, 1),
        ("web_traffic_silver.csv", "bounce_rate", 0, 1),
        ("shipper.csv", "shipper_rating", 0, 5),
        ("shipper.csv", "delivery_success_rate", 0, 100),
        ("reviews.csv", "rating", 1, 5),
    ]
    invalid_ranges = {}
    for filename, field, lower, upper in rate_checks:
        invalid_ranges[f"{filename}.{field}"] = count_rows(
            DATA_DIR / filename,
            lambda row, field=field, lower=lower, upper=upper: (
                not row[field].strip()
                or float(row[field]) < lower
                or float(row[field]) > upper
            ),
        )

    findings = []
    for profile in profiles:
        for fields, count in profile["key_duplicates"].items():
            if count:
                findings.append(
                    f"**Khóa ứng viên trùng/thiếu — `{profile['name']}`:** "
                    f"{count:,} dòng có khóa `{'+'.join(fields)}` trống hoặc trùng."
                )
    for child, child_field, parent, parent_field, count in foreign_keys:
        if count:
            findings.append(
                f"**Khóa ngoại mồ côi:** {count:,} giá trị `{child}.{child_field}` "
                f"không có trong `{parent}.{parent_field}`."
            )
    if orders_before_signup:
        findings.append(
            f"**Cần xác minh ngày khách hàng:** {orders_before_signup:,}/"
            f"{by_name['ORDER_silver.csv']['rows']:,} đơn "
            f"({orders_before_signup / by_name['ORDER_silver.csv']['rows'] * 100:.2f}%) "
            "có `order_date` trước `signup_date`. Nếu signup_date là ngày tạo hồ sơ đầu tiên, "
            "đây là bất nhất thời gian; không nên tự ý sửa hoặc loại đơn nếu chưa xác nhận nghiệp vụ."
        )
    if shipments_after_join:
        findings.append(
            f"**Cần xác minh ngày gia nhập shipper:** {shipments_after_join:,}/"
            f"{by_name['shipment.csv']['rows']:,} chuyến "
            f"({shipments_after_join / by_name['shipment.csv']['rows'] * 100:.2f}%) "
            "có `ship_date` trước `join_date` trong hồ sơ shipper."
        )
    if delivery_before_ship:
        findings.append(f"**Ngày giao trước ngày gửi:** {delivery_before_ship:,} chuyến.")
    if rating_out_of_range:
        findings.append(f"**Điểm review ngoài thang 1–5:** {rating_out_of_range:,} dòng.")
    for field, count in invalid_ranges.items():
        if count:
            findings.append(f"**Ngoài miền giá trị dự kiến — `{field}`:** {count:,} dòng.")
    if not findings:
        findings.append(
            "Không phát hiện khóa thiếu/trùng, khóa ngoại mồ côi hoặc bất thường trong các quy tắc đã kiểm tra."
        )

    return {
        "foreign_keys": foreign_keys,
        "orders_before_signup": orders_before_signup,
        "shipments_after_join": shipments_after_join,
        "delivery_before_ship": delivery_before_ship,
        "rating_out_of_range": rating_out_of_range,
        "outlier_flags": outlier_flags,
        "invalid_ranges": invalid_ranges,
        "findings": findings,
    }


def make_report(profiles, checks):
    total_rows = sum(profile["rows"] for profile in profiles)
    total_bytes = sum(profile["file_size"] for profile in profiles)
    lines = [
        "# Báo cáo tổng hợp dữ liệu `DAAI_N1.4/silver_data`",
        "",
        f"- **Thư mục nguồn:** `{DATA_DIR}`",
        f"- **Số bảng:** {len(profiles)}",
        f"- **Tổng số bản ghi:** {total_rows:,}",
        f"- **Tổng dung lượng:** {total_bytes:,} byte ({total_bytes / (1024 ** 2):,.2f} MiB)",
        "- **Kiểu dữ liệu:** suy luận từ nội dung CSV; không phải kiểu vật lý SQL. Mã định danh "
        "dạng số nên được xem như mã, không phải đại lượng đo.",
        "",
        "## Khái niệm và chức năng dữ liệu",
        "",
        "Silver là lớp dữ liệu đã được chuẩn hóa/làm sạch hơn nguồn thô, được chia thành các bảng "
        "theo nghiệp vụ. Bảng đơn hàng/dòng hàng mô tả giao dịch; các bảng khách hàng, sản phẩm, "
        "nhân viên, địa lý và shipper mô tả thực thể; các bảng thanh toán, trả hàng, đánh giá, "
        "khuyến mãi, tồn kho và web traffic ghi nhận sự kiện/chỉ số liên quan.",
        "",
        "| Bảng | Khái niệm / chức năng | Grain hoặc khóa ứng viên | Dòng | Cột | Dung lượng |",
        "|---|---|---|---:|---:|---:|",
    ]
    for profile in profiles:
        key = " + ".join("+".join(fields) for fields in profile["key_fields"])
        grain = f"một dòng / `{key}`"
        lines.append(
            f"| `{profile['name']}` | {TABLE_DESCRIPTIONS[profile['name']]} | {grain} | "
            f"{profile['rows']:,} | {len(profile['columns'])} | "
            f"{profile['file_size']:,} byte ({profile['file_size'] / (1024 ** 2):.2f} MiB) |"
        )

    lines.extend([
        "",
        "### Diễn giải một số khái niệm",
        "",
        "- `ORDER_silver` là bảng đơn ở cấp order; `ORDER_ITEMS_silver` ghi chi tiết sản phẩm trong đơn.",
        "- `ORDER_ITEM_PROMOTION_silver` là bảng liên kết nhiều-nhiều giữa dòng hàng và promotion.",
        "- `inventory_silver` là ảnh chụp tồn kho theo thời điểm, không phải giao dịch bán đơn lẻ.",
        "- Cột có hậu tố `_is_outlier` là cờ do quy trình xử lý tạo ra; đây là dấu hiệu cần xem xét, "
        "không đồng nghĩa bản ghi sai hoặc phải xóa.",
        "- `reviews` và `ORDER_silver.comment` có thể đại diện cho các dạng phản hồi khác nhau; "
        "không nên coi comment là rating khách hàng nếu chưa có quy tắc nghiệp vụ.",
        "",
        "## Bất thường và điểm cần xác minh",
        "",
    ])
    lines.extend(f"{i}. {finding}" for i, finding in enumerate(checks["findings"], start=1))
    lines.extend([
        "",
        "### Kiểm tra khóa và liên kết giữa bảng",
        "",
        "| Liên kết | Bản ghi không tìm thấy khóa cha |",
        "|---|---:|",
    ])
    for child, child_field, parent, parent_field, count in checks["foreign_keys"]:
        lines.append(
            f"| `{child}.{child_field}` → `{parent}.{parent_field}` | {count:,} |"
        )
    lines.extend([
        "",
        "",
        "### Kiểm tra miền giá trị và cờ outlier",
        "",
        "| Trường | Ngoài phạm vi dự kiến |",
        "|---|---:|",
    ])
    for field, count in checks["invalid_ranges"].items():
        lines.append(f"| `{field}` | {count:,} |")
    lines.extend([
        "",
        "| Cờ outlier | Số dòng được đánh dấu |",
        "|---|---:|",
    ])
    for field, count in checks["outlier_flags"].items():
        lines.append(f"| `{field}` | {count:,} |")
    lines.extend([
        "",
        "## Mô tả chi tiết bảng và cột",
        "",
        "Trống là chuỗi rỗng trong CSV. Min/max/trung bình là thống kê trên dữ liệu quan sát; "
        "trung bình của mã định danh không mang ý nghĩa nghiệp vụ.",
        "",
    ])
    for profile in profiles:
        lines.extend([
            f"### `{profile['name']}`",
            "",
            f"- **Chức năng:** {TABLE_DESCRIPTIONS[profile['name']]}",
            f"- **Số dòng/cột:** {profile['rows']:,}/{len(profile['columns'])}; "
            f"**dung lượng:** {profile['file_size']:,} byte; **encoding:** {profile['encoding']}.",
            f"- **Khóa ứng viên:** {'; '.join(' + '.join(fields) for fields in profile['key_fields'])}; "
            f"**dòng thiếu/trùng khóa:** {sum(profile['key_duplicates'].values()):,}.",
            "",
            "| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Phân biệt | Min | Max | Trung bình | Dài tối đa |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|",
        ])
        for column in profile["columns"]:
            meaning = FIELD_MEANINGS.get(
                column["name"],
                "Thuộc tính dữ liệu; kiểu và phạm vi được suy luận từ giá trị thực tế.",
            )
            lines.append(
                f"| `{column['name']}` | {meaning} | {column['type']} | "
                f"{column['null_count']:,} ({column['null_pct']:.2f}%) | "
                f"{column['distinct']:,} | {format_value(column['min'])} | "
                f"{format_value(column['max'])} | {format_value(column['average'])} | "
                f"{column['max_length']} ký tự |"
            )
        lines.append("")

    lines.extend([
        "## Phạm vi và hạn chế",
        "",
        "- Kiểu dữ liệu, grain và ý nghĩa được suy luận từ tên cột/cấu trúc và giá trị quan sát; "
        "cần đối chiếu data contract để xác nhận định nghĩa chính thức.",
        "- Cờ outlier được báo cáo như nhãn có sẵn; không đánh giá lại thuật toán phát hiện outlier.",
        "- Báo cáo không đưa các ví dụ chứa dữ liệu cá nhân như tên, điện thoại hoặc comment.",
        "",
    ])
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_PATH


def main():
    if not DATA_DIR.is_dir():
        raise FileNotFoundError(f"Không tìm thấy thư mục silver_data: {DATA_DIR}")
    paths = sorted(DATA_DIR.glob("*.csv"))
    expected = set(TABLE_DESCRIPTIONS)
    actual = {path.name for path in paths}
    if actual != expected:
        raise ValueError(
            f"Danh sách bảng khác dự kiến; thiếu={sorted(expected - actual)}, "
            f"thừa={sorted(actual - expected)}"
        )

    profiles = [profile_file(path) for path in paths]
    checks = run_checks(profiles)
    report = make_report(profiles, checks)
    print(f"Đã phân tích {len(profiles)} bảng, {sum(p['rows'] for p in profiles):,} bản ghi.")
    print(f"Đã xuất báo cáo tổng hợp: {report}")


if __name__ == "__main__":
    main()
