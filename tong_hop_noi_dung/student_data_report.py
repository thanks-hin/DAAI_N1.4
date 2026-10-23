import csv
import json
import math
from collections import Counter
from datetime import date
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR.parent / "student_data"
OUTPUT_DIR = PROJECT_DIR.parent / "tong_hop_noi_dung"
REPORT_PATH = OUTPUT_DIR / "bao_cao_tong_hop_student_data.md"

TABLE_DESCRIPTIONS = {
    "customers.csv": "Hồ sơ khách hàng: mã khách hàng, địa chỉ/địa lý, ngày đăng ký và nhóm nhân khẩu học/kênh tiếp cận.",
    "geography.csv": "Danh mục địa lý ánh xạ mã ZIP đến thành phố, vùng và quận/huyện.",
    "inventory.csv": "Ảnh chụp tồn kho theo ngày và sản phẩm; có số lượng, chỉ số cung ứng và cờ cảnh báo.",
    "order_items.csv": "Chi tiết dòng hàng trong đơn: sản phẩm, số lượng, đơn giá, chiết khấu và mã khuyến mãi.",
    "orders_enriched.csv": "Bảng đơn hàng đã làm giàu thông tin khách hàng, địa lý, thanh toán, nhân viên, trạng thái và phản hồi.",
    "payments.csv": "Thông tin thanh toán theo đơn, gồm phương thức, số tiền và số kỳ thanh toán.",
    "products.csv": "Danh mục sản phẩm và thuộc tính thương mại như danh mục, kích cỡ, màu, giá và giá vốn.",
    "promotions.csv": "Danh mục chương trình khuyến mãi, thời hạn, điều kiện, kênh và mức giảm.",
    "returns.csv": "Các dòng trả hàng theo đơn/sản phẩm, ngày, lý do, số lượng và tiền hoàn.",
    "reviews.csv": "Đánh giá sản phẩm gắn với đơn và khách hàng, gồm ngày, điểm và tiêu đề.",
    "shipments_realistic.csv": "Thông tin giao vận theo đơn, kết hợp sự kiện giao hàng với hồ sơ người giao/đơn vị vận chuyển.",
    "web_traffic.csv": "Lưu lượng truy cập website theo ngày và nguồn truy cập.",
    "epd.json": "Tập dữ liệu JSON có cấu trúc thuộc tính sản phẩm; cần đối chiếu phiên bản với products.csv trước khi ghép.",
    "eprom.json": "Tập dữ liệu JSON về chương trình khuyến mãi; cần đối chiếu phiên bản với promotions.csv trước khi ghép.",
    "tf.json": "Tập dữ liệu JSON về lưu lượng truy cập; cần đối chiếu ngày và nguồn với web_traffic.csv trước khi ghép.",
}

KEYS = {
    "customers.csv": [("customer_id",)],
    "geography.csv": [("zip",)],
    "inventory.csv": [("snapshot_date", "product_id")],
    "order_items.csv": [("order_id", "product_id")],
    "orders_enriched.csv": [("order_id",)],
    "payments.csv": [("order_id",)],
    "products.csv": [("product_id",)],
    "promotions.csv": [("promo_id",)],
    "returns.csv": [("return_id",)],
    "reviews.csv": [("review_id",)],
    "shipments_realistic.csv": [("order_id",)],
    "web_traffic.csv": [("date",)],
    "epd.json": [("product_id",)],
    "eprom.json": [("promo_id",)],
    "tf.json": [("date",)],
}

INDEX_FIELDS = {
    "customers.csv": {"customer_id"},
    "geography.csv": {"zip"},
    "orders_enriched.csv": {"order_id", "customer_id", "zip"},
    "products.csv": {"product_id"},
    "promotions.csv": {"promo_id"},
}

FIELD_MEANINGS = {
    "customer_id": "Mã khách hàng",
    "gender": "Giới tính theo hồ sơ",
    "age_group": "Nhóm tuổi khách hàng",
    "order_id": "Mã đơn hàng",
    "product_id": "Mã sản phẩm",
    "product_name": "Tên sản phẩm",
    "category": "Danh mục sản phẩm/nhóm áp dụng",
    "segment": "Phân khúc sản phẩm",
    "size": "Kích cỡ sản phẩm",
    "color": "Màu sản phẩm",
    "promo_id": "Mã khuyến mãi",
    "promo_id_2": "Mã khuyến mãi bổ sung",
    "promo_name": "Tên chương trình khuyến mãi",
    "promo_type": "Loại hình khuyến mãi",
    "discount_value": "Giá trị hoặc tỷ lệ giảm",
    "start_date": "Ngày bắt đầu hiệu lực",
    "end_date": "Ngày kết thúc hiệu lực",
    "applicable_category": "Danh mục sản phẩm áp dụng",
    "promo_channel": "Kênh áp dụng khuyến mãi",
    "stackable_flag": "Cờ cho biết có thể cộng dồn khuyến mãi",
    "min_order_value": "Giá trị đơn hàng tối thiểu để áp dụng",
    "return_id": "Mã trả hàng",
    "review_id": "Mã đánh giá",
    "shipper_id": "Mã người/đơn vị giao hàng",
    "sales_employee_id": "Mã nhân viên bán hàng",
    "sales_employee_name": "Tên nhân viên bán hàng",
    "zip": "Mã ZIP/khu vực địa lý",
    "order_date": "Ngày đặt hàng",
    "signup_date": "Ngày đăng ký khách hàng",
    "snapshot_date": "Ngày chụp số liệu tồn kho",
    "return_date": "Ngày trả hàng",
    "review_date": "Ngày đánh giá",
    "ship_date": "Ngày gửi hàng",
    "delivery_date": "Ngày giao hàng",
    "join_date": "Ngày gia nhập của người giao hàng",
    "date": "Ngày ghi nhận",
    "quantity": "Số lượng sản phẩm",
    "unit_price": "Đơn giá",
    "price": "Giá bán",
    "cogs": "Giá vốn hàng bán",
    "discount_amount": "Số tiền chiết khấu",
    "shipping_fee": "Phí vận chuyển",
    "score": "Điểm số",
    "tone": "Sắc thái phản hồi",
    "comment": "Nội dung phản hồi",
    "marital_status": "Tình trạng hôn nhân trong hồ sơ",
    "education_level": "Trình độ học vấn trong hồ sơ",
    "years_experience": "Số năm kinh nghiệm",
    "name": "Tên nhân viên",
    "payment_value": "Số tiền thanh toán",
    "installments": "Số kỳ thanh toán",
    "return_reason": "Lý do trả hàng",
    "return_quantity": "Số lượng sản phẩm trả",
    "refund_amount": "Số tiền hoàn trả",
    "review_title": "Tiêu đề/nội dung ngắn của đánh giá",
    "rating": "Điểm đánh giá",
    "shipper_company": "Đơn vị vận chuyển",
    "shipper_vehicle": "Loại phương tiện giao hàng",
    "shipper_experience_years": "Số năm kinh nghiệm người giao hàng",
    "shipper_rating": "Điểm đánh giá người giao hàng",
    "delivery_success_rate": "Tỷ lệ giao hàng thành công (thang dữ liệu hiện có)",
    "average_delivery_time": "Thời gian giao hàng trung bình theo đơn vị nguồn",
    "working_shift": "Ca làm việc",
    "shipper_name": "Tên người giao hàng",
    "shipper_phone": "Số điện thoại liên hệ người giao hàng",
    "shipper_gender": "Giới tính người giao hàng",
    "shipper_age": "Tuổi người giao hàng",
    "shipper_marital_status": "Tình trạng hôn nhân người giao hàng",
    "shipper_education": "Trình độ học vấn người giao hàng",
    "year": "Năm của kỳ ghi nhận tồn kho",
    "month": "Tháng của kỳ ghi nhận tồn kho",
    "city": "Thành phố",
    "region": "Vùng",
    "district": "Quận/huyện",
    "order_status": "Trạng thái đơn hàng",
    "payment_method": "Phương thức thanh toán",
    "device_type": "Loại thiết bị",
    "order_source": "Nguồn đơn hàng",
    "acquisition_channel": "Kênh thu hút khách hàng",
    "traffic_source": "Nguồn truy cập",
    "sessions": "Số phiên truy cập",
    "unique_visitors": "Số khách truy cập duy nhất",
    "page_views": "Số lượt xem trang",
    "bounce_rate": "Tỷ lệ thoát",
    "avg_session_duration_sec": "Thời lượng phiên trung bình (giây)",
    "stock_on_hand": "Lượng hàng tồn",
    "units_received": "Lượng hàng nhập",
    "units_sold": "Lượng hàng bán",
    "stockout_days": "Số ngày hết hàng",
    "days_of_supply": "Số ngày tồn kho đủ cung ứng",
    "fill_rate": "Tỷ lệ đáp ứng nhu cầu",
    "sell_through_rate": "Tỷ lệ bán hết hàng",
    "stockout_flag": "Cờ cảnh báo hết hàng",
    "overstock_flag": "Cờ cảnh báo tồn quá mức",
    "reorder_flag": "Cờ đề nghị đặt hàng lại",
}


def detect_encoding(path):
    with path.open("rb") as file:
        prefix = file.read(4)
    if prefix[:2] in (bytes([255, 254]), bytes([254, 255])):
        return "utf-16"
    return "utf-8-sig"


def read_records(path):
    if path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError(f"JSON phải chứa danh sách bản ghi: {path}")
        if any(not isinstance(row, dict) for row in data):
            raise ValueError(f"Mọi phần tử JSON phải là object: {path}")
        yield from data
        return

    encoding = detect_encoding(path)
    with path.open("r", encoding=encoding, newline="") as file:
        reader = csv.reader(file)
        headers = next(reader, None)
        if not headers:
            raise ValueError(f"CSV rỗng hoặc thiếu header: {path}")
        if len(headers) != len(set(headers)):
            raise ValueError(f"Header có tên cột trùng lặp: {path}")
        for line_number, values in enumerate(reader, start=2):
            if len(values) != len(headers):
                raise ValueError(f"Số trường không đúng tại {path.name}:{line_number}")
            yield dict(zip(headers, values))


def infer_type(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number" if math.isfinite(value) else "non-finite number"
    if not isinstance(value, str):
        return type(value).__name__
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
    nonempty = types - {"empty", "null"}
    if not nonempty:
        return "empty"
    if nonempty <= {"integer", "number"}:
        return "integer" if nonempty == {"integer"} else "number"
    return next(iter(nonempty)) if len(nonempty) == 1 else "mixed"


def display(value):
    if value is None:
        return ""
    return str(value)


def profile_file(path):
    profiles = {}
    row_count = 0
    key_sets = {fields: set() for fields in KEYS.get(path.name, [])}
    duplicate_keys = Counter()
    indexes = {field: set() for field in INDEX_FIELDS.get(path.name, set())}

    for row in read_records(path):
        row_count += 1
        for fields, seen in key_sets.items():
            key = tuple(display(row.get(field)) for field in fields)
            if any(not value.strip() for value in key):
                duplicate_keys[fields] += 1
            elif key in seen:
                duplicate_keys[fields] += 1
            else:
                seen.add(key)

        for field, values in indexes.items():
            value = display(row.get(field)).strip()
            if value:
                values.add(value)

        for name, raw_value in row.items():
            stats = profiles.setdefault(name, {
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
            })
            value_type = infer_type(raw_value)
            value = display(raw_value).strip()
            if value_type in {"null", "empty"}:
                stats["null_count"] += 1
                continue
            stats["types"].add(value_type)
            stats["values"].add(value)
            stats["max_length"] = max(stats["max_length"], len(display(raw_value)))
            if value_type in {"integer", "number"}:
                number = float(raw_value)
                stats["numeric_min"] = number if stats["numeric_min"] is None else min(stats["numeric_min"], number)
                stats["numeric_max"] = number if stats["numeric_max"] is None else max(stats["numeric_max"], number)
                stats["numeric_sum"] += number
                stats["numeric_count"] += 1
            elif value_type == "date":
                stats["date_min"] = value if stats["date_min"] is None else min(stats["date_min"], value)
                stats["date_max"] = value if stats["date_max"] is None else max(stats["date_max"], value)

    columns = []
    for name, stats in profiles.items():
        kind = normalize_type(stats["types"])
        minimum = maximum = mean = ""
        if kind in {"integer", "number"} and stats["numeric_count"]:
            minimum = stats["numeric_min"]
            maximum = stats["numeric_max"]
            mean = stats["numeric_sum"] / stats["numeric_count"]
        elif kind == "date":
            minimum, maximum = stats["date_min"], stats["date_max"]
        columns.append({
            "name": name,
            "type": kind,
            "null_count": stats["null_count"],
            "null_pct": stats["null_count"] / row_count * 100 if row_count else 0,
            "distinct": len(stats["values"]),
            "min": minimum,
            "max": maximum,
            "mean": mean,
            "max_length": stats["max_length"],
        })

    return {
        "name": path.name,
        "rows": row_count,
        "columns": columns,
        "file_size": path.stat().st_size,
        "encoding": detect_encoding(path) if path.suffix.lower() == ".csv" else "UTF-8 JSON",
        "key_duplicates": duplicate_keys,
        "indexes": indexes,
    }


def count_orphans(child_path, child_field, parent_values):
    return sum(
        1 for row in read_records(child_path)
        if display(row.get(child_field)).strip()
        and display(row.get(child_field)).strip() not in parent_values
    )


def count_condition(path, predicate):
    return sum(1 for row in read_records(path) if predicate(row))


def indexed_values(profiles, filename, field):
    return by_profile_name(profiles, filename)["indexes"].get(field, set())


def by_profile_name(profiles, filename):
    return next(profile for profile in profiles if profile["name"] == filename)


def fmt_number(value):
    if value == "":
        return "—"
    if isinstance(value, float):
        return f"{value:,.4f}".rstrip("0").rstrip(".")
    return str(value)


def field_meaning(name):
    return FIELD_MEANINGS.get(name, "Thuộc tính dữ liệu; kiểu và phạm vi được suy luận từ giá trị thực tế.")


def make_report(profiles):
    by_name = {profile["name"]: profile for profile in profiles}
    total_rows = sum(item["rows"] for item in profiles)
    total_bytes = sum(item["file_size"] for item in profiles)
    findings = []

    customer_dates = {
        row["customer_id"]: row["signup_date"]
        for row in read_records(DATA_DIR / "customers.csv")
    }
    orders_before_signup = count_condition(
        DATA_DIR / "orders_enriched.csv",
        lambda row: row["order_date"] < customer_dates[row["customer_id"]],
    )
    if orders_before_signup:
        findings.append(
            f"**Cao — thời gian đăng ký khách hàng:** {orders_before_signup:,}/"
            f"{by_name['orders_enriched.csv']['rows']:,} đơn hàng "
            f"({orders_before_signup / by_name['orders_enriched.csv']['rows'] * 100:.2f}%) "
            "có ngày đặt trước `signup_date` của khách hàng. Điều này không nhất quán nếu `signup_date` "
            "là ngày tạo hồ sơ lần đầu; cần xác minh ý nghĩa cột hoặc nguồn ngày."
        )

    shipper_join_after_ship = count_condition(
        DATA_DIR / "shipments_realistic.csv",
        lambda row: row["join_date"] > row["ship_date"],
    )
    if shipper_join_after_ship:
        findings.append(
            f"**Cao — thời gian nhân viên giao hàng:** {shipper_join_after_ship:,}/"
            f"{by_name['shipments_realistic.csv']['rows']:,} lô giao hàng "
            f"({shipper_join_after_ship / by_name['shipments_realistic.csv']['rows'] * 100:.2f}%) "
            "có `join_date` của shipper sau `ship_date`. Phạm vi ngày gia nhập kéo đến 2026 trong khi "
            "sự kiện giao hàng kết thúc năm 2022; cần xác minh đây là ngày tham chiếu của hồ sơ hay lỗi ghép."
        )

    epd = list(read_records(DATA_DIR / "epd.json"))
    epd_invalid_ids = sum(
        1 for row in epd if row.get("product_id") is None or not str(row.get("product_id")).strip()
    )
    products_csv = indexed_values(profiles, "products.csv", "product_id")
    epd_ids = {
        str(row.get("product_id")).strip()
        for row in epd
        if row.get("product_id") is not None and str(row.get("product_id")).strip()
    }
    product_overlap = len(products_csv & epd_ids)
    if epd_invalid_ids:
        findings.append(
            f"**Cao — mã sản phẩm trong epd.json:** có {epd_invalid_ids} bản ghi thiếu/để trống "
            "`product_id`; các bản ghi này không thể liên kết tin cậy theo mã."
        )
    if product_overlap != len(epd_ids) or len(products_csv) != len(epd_ids):
        findings.append(
            f"**Trung bình — phiên bản danh mục sản phẩm:** products.csv có {len(products_csv):,} mã khác nhau, "
            f"epd.json có {len(epd_ids):,} mã hợp lệ; giao nhau {product_overlap:,}. "
            "Hai tệp không phải hai bản sao cùng phạm vi, không nên thay thế/ghép toàn bộ nếu chưa xác định phiên bản."
        )

    promotions_csv = indexed_values(profiles, "promotions.csv", "promo_id")
    eprom_ids = {
        str(row.get("promo_id", "")).strip()
        for row in read_records(DATA_DIR / "eprom.json")
        if str(row.get("promo_id", "")).strip()
    }
    if not (promotions_csv & eprom_ids):
        findings.append(
            f"**Trung bình — phiên bản khuyến mãi:** promotions.csv có {len(promotions_csv):,} mã, "
            f"eprom.json có {len(eprom_ids):,} mã hợp lệ và không có mã giao nhau. "
            "Không dùng hai nguồn như cùng một danh mục khuyến mãi nếu chưa chuẩn hóa/mapping mã."
        )

    traffic_csv_dates = {
        display(row.get("date")).strip()
        for row in read_records(DATA_DIR / "web_traffic.csv")
        if display(row.get("date")).strip()
    }
    traffic_json_dates = {
        str(row.get("date", "")).strip()
        for row in read_records(DATA_DIR / "tf.json")
        if str(row.get("date", "")).strip()
    }
    invalid_traffic_dates = sum(
        1 for row in read_records(DATA_DIR / "tf.json")
        if infer_type(row.get("date")) != "date"
    )
    traffic_overlap = len(traffic_csv_dates & traffic_json_dates)
    if invalid_traffic_dates or len(traffic_csv_dates) != len(traffic_json_dates):
        findings.append(
            f"**Trung bình — phiên bản lưu lượng truy cập:** web_traffic.csv có "
            f"{len(traffic_csv_dates):,} ngày, tf.json có {len(traffic_json_dates):,} giá trị ngày "
            f"({traffic_overlap:,} giá trị trùng); tf.json có {invalid_traffic_dates} giá trị `date` "
            "không phân tích được thành ngày. Hai tệp có phạm vi khác nhau."
        )

    repeated_pairs = by_name["order_items.csv"]["key_duplicates"][("order_id", "product_id")]
    if repeated_pairs:
        findings.append(
            f"**Cần xác nhận — dòng hàng lặp cặp đơn/sản phẩm:** có {repeated_pairs:,} dòng vượt "
            "số khóa duy nhất cho cặp "
            "`(order_id, product_id)` xuất hiện nhiều lần trong order_items.csv. "
            "Điều này không nhất thiết là lỗi nếu một đơn có nhiều dòng/giá cho cùng sản phẩm; "
            "cần xác nhận khóa nghiệp vụ của bảng chi tiết."
        )

    inventory_products = {
        display(row.get("product_id")).strip()
        for row in read_records(DATA_DIR / "inventory.csv")
        if display(row.get("product_id")).strip()
    }
    product_coverage = len(inventory_products & products_csv)
    findings.append(
        f"**Phạm vi tồn kho:** inventory.csv có {len(inventory_products):,} mã sản phẩm khác nhau, "
        f"trong đó {product_coverage:,}/{len(products_csv):,} mã thuộc products.csv. "
        "Phần danh mục không có bản ghi tồn kho có thể là sản phẩm không được theo dõi trong giai đoạn này."
    )

    relation_specs = [
        ("orders_enriched.csv", "customer_id", "customers.csv", "customer_id"),
        ("orders_enriched.csv", "zip", "geography.csv", "zip"),
        ("order_items.csv", "order_id", "orders_enriched.csv", "order_id"),
        ("order_items.csv", "product_id", "products.csv", "product_id"),
        ("order_items.csv", "promo_id", "promotions.csv", "promo_id"),
        ("order_items.csv", "promo_id_2", "promotions.csv", "promo_id"),
        ("payments.csv", "order_id", "orders_enriched.csv", "order_id"),
        ("returns.csv", "order_id", "orders_enriched.csv", "order_id"),
        ("returns.csv", "product_id", "products.csv", "product_id"),
        ("reviews.csv", "order_id", "orders_enriched.csv", "order_id"),
        ("reviews.csv", "product_id", "products.csv", "product_id"),
        ("reviews.csv", "customer_id", "customers.csv", "customer_id"),
        ("shipments_realistic.csv", "order_id", "orders_enriched.csv", "order_id"),
        ("inventory.csv", "product_id", "products.csv", "product_id"),
    ]
    relation_results = []
    for child, child_field, parent, parent_field in relation_specs:
        parent_values = indexed_values(profiles, parent, parent_field)
        orphan_count = count_orphans(DATA_DIR / child, child_field, parent_values)
        relation_results.append((child, child_field, parent, parent_field, orphan_count))

    geography = {
        row["zip"]: (row["city"], row["region"], row["district"])
        for row in read_records(DATA_DIR / "geography.csv")
    }
    geography_mismatches = count_condition(
        DATA_DIR / "orders_enriched.csv",
        lambda row: (row["city"], row["region"], row["district"]) != geography[row["zip"]],
    )
    payment_methods = {
        row["order_id"]: row["payment_method"]
        for row in read_records(DATA_DIR / "payments.csv")
    }
    payment_method_mismatches = count_condition(
        DATA_DIR / "orders_enriched.csv",
        lambda row: row["payment_method"] != payment_methods[row["order_id"]],
    )

    range_checks = [
        ("reviews.csv", "rating", 1, 5),
        ("inventory.csv", "fill_rate", 0, 1),
        ("inventory.csv", "sell_through_rate", 0, 1),
        ("web_traffic.csv", "bounce_rate", 0, 1),
        ("order_items.csv", "quantity", 1, None),
        ("order_items.csv", "unit_price", 0, None),
        ("order_items.csv", "discount_amount", 0, None),
        ("payments.csv", "payment_value", 0, None),
        ("payments.csv", "installments", 1, None),
        ("products.csv", "price", 0, None),
        ("products.csv", "cogs", 0, None),
        ("returns.csv", "return_quantity", 1, None),
        ("returns.csv", "refund_amount", 0, None),
        ("shipments_realistic.csv", "shipping_fee", 0, None),
        ("shipments_realistic.csv", "shipper_rating", 0, 5),
        ("shipments_realistic.csv", "delivery_success_rate", 0, 100),
        ("shipments_realistic.csv", "shipper_age", 18, 100),
    ]
    range_results = []
    for filename, field, lower, upper in range_checks:
        invalid = count_condition(
            DATA_DIR / filename,
            lambda row, field=field, lower=lower, upper=upper: (
                not row[field].strip()
                or float(row[field]) < lower
                or (upper is not None and float(row[field]) > upper)
            ),
        )
        range_results.append((filename, field, lower, upper, invalid))
        if invalid:
            range_label = f"{lower}–{upper}" if upper is not None else f"≥ {lower}"
            findings.append(
                f"**Cao — miền giá trị `{filename}.{field}`:** {invalid:,} bản ghi nằm ngoài "
                f"phạm vi kiểm tra {range_label}."
            )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Báo cáo tổng hợp dữ liệu `student_data`",
        "",
        f"- **Thư mục nguồn:** `{DATA_DIR}`",
        f"- **Số tệp dữ liệu:** {len(profiles)} ({sum(p['name'].endswith('.csv') for p in profiles)} CSV, "
        f"{sum(p['name'].endswith('.json') for p in profiles)} JSON)",
        f"- **Tổng số bản ghi:** {total_rows:,}",
        f"- **Tổng dung lượng tệp:** {total_bytes:,} byte ({total_bytes / (1024 ** 2):,.2f} MiB)",
        "- **Lưu ý kiểu dữ liệu:** CSV/JSON không khai báo schema SQL; kiểu dưới đây được suy luận từ nội dung. "
        "Các mã định danh dạng số vẫn nên được lưu như chuỗi nếu cần giữ định dạng/ý nghĩa mã.",
        "",
        "## Khái niệm và chức năng các tập dữ liệu",
        "",
        "| Tệp | Khái niệm / chức năng | Bản ghi | Cột | Kích thước |",
        "|---|---|---:|---:|---:|",
    ]

    for profile in profiles:
        lines.append(
            f"| `{profile['name']}` | {TABLE_DESCRIPTIONS.get(profile['name'], 'Tập dữ liệu nguồn.')}"
            f" | {profile['rows']:,} | {len(profile['columns'])} | "
            f"{profile['file_size']:,} byte ({profile['file_size'] / (1024 ** 2):.2f} MiB) |"
        )

    lines.extend([
        "",
        "### Nhóm dữ liệu theo nghiệp vụ",
        "",
        "- **Khách hàng và địa lý:** `customers.csv`, `geography.csv`.",
        "- **Đơn hàng và bán hàng:** `orders_enriched.csv`, `order_items.csv`, `payments.csv`.",
        "- **Danh mục và khuyến mãi:** `products.csv`, `promotions.csv`.",
        "- **Hậu mãi:** `returns.csv`, `reviews.csv`.",
        "- **Vận hành:** `inventory.csv`, `shipments_realistic.csv`.",
        "- **Phân tích kênh số:** `web_traffic.csv`.",
        "- **Các bản JSON song song:** `epd.json`, `eprom.json`, `tf.json`; cần kiểm tra phiên bản/phạm vi trước khi ghép với các CSV tên tương ứng.",
        "",
        "## Bất thường và điểm cần xác minh",
        "",
    ])
    if findings:
        lines.extend(f"{index}. {finding}" for index, finding in enumerate(findings, start=1))
    else:
        lines.append("Không phát hiện bất thường theo các quy tắc đã kiểm tra.")

    lines.extend([
        "",
        "### Kiểm tra liên kết giữa các bảng",
        "",
        "| Liên kết | Bản ghi không tìm thấy khóa cha |",
        "|---|---:|",
    ])
    for child, child_field, parent, parent_field, orphan_count in relation_results:
        lines.append(
            f"| `{child}.{child_field}` → `{parent}.{parent_field}` | {orphan_count:,} |"
        )
    lines.append(
        f"\nĐối chiếu các trường địa lý được làm giàu trong orders_enriched.csv với geography.csv: "
        f"{geography_mismatches:,} dòng không khớp."
    )
    lines.append(
        f"Đối chiếu `payment_method` giữa orders_enriched.csv và payments.csv: "
        f"{payment_method_mismatches:,} dòng không khớp."
    )
    lines.extend([
        "",
        "### Kiểm tra miền giá trị cơ bản",
        "",
        "| Trường | Phạm vi kiểm tra | Ngoài phạm vi |",
        "|---|---:|---:|",
    ])
    for filename, field, lower, upper, invalid in range_results:
        range_label = f"{lower}–{upper}" if upper is not None else f"≥ {lower}"
        lines.append(f"| `{filename}.{field}` | {range_label} | {invalid:,} |")

    lines.extend([
        "",
        "## Mô tả chi tiết cột",
        "",
        "Các số min/max/trung bình chỉ có ý nghĩa thống kê theo giá trị hiện có; không thay thế định nghĩa nghiệp vụ. "
        "Tỷ lệ trống tính trên số bản ghi của tệp.",
        "",
    ])
    for profile in profiles:
        lines.extend([
            f"### `{profile['name']}`",
            "",
            f"- **Chức năng:** {TABLE_DESCRIPTIONS.get(profile['name'], 'Tập dữ liệu nguồn.')}",
            f"- **Kích thước tệp:** {profile['file_size']:,} byte; **encoding:** {profile['encoding']}; "
            f"**số dòng:** {profile['rows']:,}; **số cột:** {len(profile['columns'])}.",
        ])
        for fields, duplicate_count in profile["key_duplicates"].items():
            key_name = " + ".join(fields)
            lines.append(f"- **Khóa ứng viên `{key_name}` thiếu/trùng:** {duplicate_count:,}.")
        lines.extend([
            "",
            "| Cột | Ý nghĩa khái quát | Kiểu suy luận | Trống | Khác biệt | Min | Max | Trung bình | Dài tối đa |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|",
        ])
        for column in profile["columns"]:
            lines.append(
                f"| `{column['name']}` | {field_meaning(column['name'])} | {column['type']} | "
                f"{column['null_count']:,} ({column['null_pct']:.2f}%) | {column['distinct']:,} | "
                f"{fmt_number(column['min'])} | {fmt_number(column['max'])} | "
                f"{fmt_number(column['mean'])} | {column['max_length']} ký tự |"
            )
        lines.append("")

    lines.extend([
        "## Phạm vi và hạn chế",
        "",
        "- Báo cáo mô tả dữ liệu thực tế và áp dụng các kiểm tra cấu trúc, khóa, miền giá trị và thời gian nêu trên; "
        "không thể xác nhận ý nghĩa nghiệp vụ nếu chưa có data contract.",
        "- Các tệp JSON `epd.json`, `eprom.json`, `tf.json` có thể là bản trích xuất/biến thể riêng. "
        "Khác biệt về số lượng hoặc mã chưa đủ để kết luận tệp nào là nguồn chuẩn.",
        "- Các giá trị thông tin cá nhân như số điện thoại và ví dụ tên/comment không được đưa vào tài liệu.",
        "",
    ])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return profiles, relation_results, geography_mismatches, REPORT_PATH


def main():
    if not DATA_DIR.is_dir():
        raise FileNotFoundError(f"Không tìm thấy thư mục dữ liệu: {DATA_DIR}")
    data_paths = sorted(
        path for path in DATA_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in {".csv", ".json"}
    )
    if not data_paths:
        raise FileNotFoundError(f"Không có CSV/JSON trong {DATA_DIR}")

    profiles = [profile_file(path) for path in data_paths]
    _, _, _, report_path = make_report(profiles)
    print(f"Đã phân tích {len(profiles)} tệp, {sum(p['rows'] for p in profiles):,} bản ghi.")
    print(f"Đã xuất tài liệu tổng hợp: {report_path}")


if __name__ == "__main__":
    main()
