import csv
import math
from collections import Counter
from datetime import date, timedelta
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "golden_data"
OUTPUT_DIR = PROJECT_DIR.parent / "tong_hop_noi_dung"
REPORT_PATH = OUTPUT_DIR / "bao_cao_tong_hop_golden_data.md"

TABLE_DESCRIPTIONS = {
    "Dim_Customer.csv": (
        "Dimension khách hàng: hồ sơ khách hàng, ngày đăng ký, nhân khẩu học, "
        "kênh thu hút và địa lý."
    ),
    "Dim_Date.csv": (
        "Dimension thời gian dạng lịch, cung cấp thuộc tính ngày/tháng/quý/năm "
        "để phân tích và lọc theo thời gian."
    ),
    "Dim_Employee.csv": (
        "Dimension nhân viên bán hàng: mã nhân viên và một số thông tin hồ sơ "
        "phục vụ phân tích kết quả bán hàng."
    ),
    "Dim_Geography.csv": (
        "Dimension địa lý: ánh xạ ZIP sang thành phố, vùng và quận/huyện."
    ),
    "Dim_Product.csv": (
        "Dimension sản phẩm: tên, danh mục, phân khúc và thuộc tính thương mại "
        "của sản phẩm."
    ),
    "Fact_Sales.csv": (
        "Fact giao dịch bán hàng ở cấp dòng sản phẩm trong đơn hàng; chứa khóa "
        "liên kết đến các dimension và các chỉ số số lượng/giá trị bán."
    ),
}

PRIMARY_KEYS = {
    "Dim_Customer.csv": ("customer_id",),
    "Dim_Date.csv": ("date_key",),
    "Dim_Employee.csv": ("sales_employee_id",),
    "Dim_Geography.csv": ("zip",),
    "Dim_Product.csv": ("product_id",),
    "Fact_Sales.csv": ("order_id", "product_id"),
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
    "date_key": "Khóa ngày theo định dạng YYYY-MM-DD",
    "year": "Năm",
    "quarter": "Quý trong năm",
    "month": "Tháng",
    "month_name": "Tên tháng",
    "day": "Ngày trong tháng",
    "day_of_week": "Thứ trong tuần theo quy ước của dữ liệu",
    "day_name": "Tên thứ trong tuần",
    "is_weekend": "Cờ ngày cuối tuần",
    "year_month": "Khóa tháng theo định dạng YYYY-MM",
    "sales_employee_id": "Mã nhân viên bán hàng",
    "name": "Tên nhân viên",
    "years_experience": "Số năm kinh nghiệm",
    "education_level": "Trình độ học vấn",
    "marital_status": "Tình trạng hôn nhân",
    "product_id": "Mã sản phẩm",
    "product_name": "Tên sản phẩm",
    "category": "Danh mục sản phẩm",
    "segment": "Phân khúc sản phẩm",
    "size": "Kích cỡ sản phẩm",
    "color": "Màu sản phẩm",
    "price": "Giá bán niêm yết",
    "cogs": "Giá vốn hàng bán",
    "order_id": "Mã đơn hàng",
    "order_status": "Trạng thái đơn hàng",
    "quantity": "Số lượng sản phẩm trong dòng giao dịch",
    "unit_price": "Đơn giá trong giao dịch",
    "discount_amount": "Số tiền chiết khấu",
    "gross_amount": "Giá trị trước chiết khấu",
    "net_amount": "Giá trị sau chiết khấu",
    "promo_count": "Số chương trình khuyến mãi áp dụng",
    "has_promotion": "Cờ cho biết dòng hàng có khuyến mãi",
}

FOREIGN_KEYS = [
    ("Fact_Sales.csv", "customer_id", "Dim_Customer.csv", "customer_id"),
    ("Fact_Sales.csv", "date_key", "Dim_Date.csv", "date_key"),
    ("Fact_Sales.csv", "sales_employee_id", "Dim_Employee.csv", "sales_employee_id"),
    ("Fact_Sales.csv", "zip", "Dim_Geography.csv", "zip"),
    ("Fact_Sales.csv", "product_id", "Dim_Product.csv", "product_id"),
    ("Dim_Customer.csv", "zip", "Dim_Geography.csv", "zip"),
]


def detect_encoding(path):
    with path.open("rb") as file:
        prefix = file.read(4)
    if prefix[:2] in (bytes([255, 254]), bytes([254, 255])):
        return "utf-16"
    return "utf-8-sig"


def read_csv(path):
    encoding = detect_encoding(path)
    with path.open("r", encoding=encoding, newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError(f"CSV rỗng hoặc thiếu header: {path}")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f"Header có tên cột trùng lặp: {path}")
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
    columns = None
    row_count = 0
    stats = {}
    key_seen = set()
    key_duplicates = 0
    key_fields = PRIMARY_KEYS[path.name]

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
                    "samples": [],
                }
                for name in columns
            }
        row_count += 1
        key = tuple(row[field].strip() for field in key_fields)
        if any(not part for part in key) or key in key_seen:
            key_duplicates += 1
        else:
            key_seen.add(key)

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
            if len(column["samples"]) < 3 and value not in column["samples"]:
                column["samples"].append(value)
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
            "samples": column["samples"],
        })

    return {
        "name": path.name,
        "rows": row_count,
        "columns": column_profiles,
        "file_size": path.stat().st_size,
        "encoding": detect_encoding(path),
        "key_fields": key_fields,
        "key_duplicates": key_duplicates,
        "key_values": key_seen,
    }


def load_key_values(path, field):
    return {
        row[field].strip()
        for row in read_csv(path)
        if row[field].strip()
    }


def format_value(value):
    if value == "":
        return "—"
    if isinstance(value, float):
        return f"{value:,.4f}".rstrip("0").rstrip(".")
    return str(value)


def validate_data(profiles):
    by_name = {profile["name"]: profile for profile in profiles}
    key_values = {
        (profile["name"], field): {key[index] for key in profile["key_values"]}
        for profile in profiles
        for index, field in enumerate(profile["key_fields"])
    }
    foreign_key_results = []
    for child, child_field, parent, parent_field in FOREIGN_KEYS:
        parent_keys = key_values[(parent, parent_field)]
        missing = sum(
            1 for row in read_csv(DATA_DIR / child)
            if row[child_field].strip() and row[child_field].strip() not in parent_keys
        )
        foreign_key_results.append((child, child_field, parent, parent_field, missing))

    customer_geography = {
        row["zip"]: (row["city"], row["region"], row["district"])
        for row in read_csv(DATA_DIR / "Dim_Geography.csv")
    }
    customer_geo_mismatches = sum(
        1 for row in read_csv(DATA_DIR / "Dim_Customer.csv")
        if customer_geography.get(row["zip"]) != (row["city"], row["region"], row["district"])
    )

    dates = {row["date_key"]: row for row in read_csv(DATA_DIR / "Dim_Date.csv")}
    date_attribute_mismatches = Counter()
    customer_signup_mismatches = 0
    status_counts = Counter()
    status_net_amounts = Counter()
    for row in read_csv(DATA_DIR / "Fact_Sales.csv"):
        date_row = dates.get(row["date_key"])
        if date_row is not None:
            for field, expected in (
                ("year", int(row["date_key"][:4])),
                ("month", int(row["date_key"][5:7])),
                ("day", int(row["date_key"][8:10])),
                ("day_of_week", date.fromisoformat(row["date_key"]).weekday()),
            ):
                if int(date_row[field]) != expected:
                    date_attribute_mismatches[field] += 1
            expected_weekend = int(date.fromisoformat(row["date_key"]).weekday() >= 5)
            if int(date_row["is_weekend"]) != expected_weekend:
                date_attribute_mismatches["is_weekend"] += 1

    fact_metrics = Counter()
    customers = {
        row["customer_id"]: row["signup_date"]
        for row in read_csv(DATA_DIR / "Dim_Customer.csv")
    }
    for row in read_csv(DATA_DIR / "Fact_Sales.csv"):
        quantity = float(row["quantity"])
        unit_price = float(row["unit_price"])
        discount = float(row["discount_amount"])
        gross = float(row["gross_amount"])
        net = float(row["net_amount"])
        status_counts[row["order_status"]] += 1
        status_net_amounts[row["order_status"]] += net
        if row["date_key"] < customers[row["customer_id"]]:
            customer_signup_mismatches += 1
        if quantity <= 0:
            fact_metrics["nonpositive_quantity"] += 1
        if discount < 0:
            fact_metrics["negative_discount"] += 1
        if gross < 0 or net < 0:
            fact_metrics["negative_amount"] += 1
        if not math.isclose(gross, quantity * unit_price, rel_tol=1e-5, abs_tol=0.011):
            fact_metrics["gross_formula_mismatch"] += 1
        if not math.isclose(net, gross - discount, rel_tol=1e-5, abs_tol=0.011):
            fact_metrics["net_formula_mismatch"] += 1
        if row["has_promotion"] not in {"0", "1"}:
            fact_metrics["invalid_promotion_flag"] += 1
        elif (row["has_promotion"] == "1") != (int(row["promo_count"]) > 0):
            fact_metrics["promotion_count_mismatch"] += 1

    date_keys = sorted(dates)
    date_gaps = []
    for previous, current in zip(date_keys, date_keys[1:]):
        previous_date = date.fromisoformat(previous)
        current_date = date.fromisoformat(current)
        if current_date - previous_date != timedelta(days=1):
            date_gaps.append((previous, current))

    findings = []
    for profile in profiles:
        if profile["key_duplicates"]:
            findings.append(
                f"**Khóa chính ứng viên trùng/thiếu — {profile['name']}:** "
                f"{profile['key_duplicates']:,} dòng có khóa `{'+'.join(profile['key_fields'])}` "
                "bị trống hoặc trùng."
            )
    for child, child_field, parent, parent_field, missing in foreign_key_results:
        if missing:
            findings.append(
                f"**Khóa ngoại mồ côi:** {missing:,} giá trị "
                f"`{child}.{child_field}` không có trong `{parent}.{parent_field}`."
            )
    if customer_geo_mismatches:
        findings.append(
            f"**Địa lý khách hàng không khớp:** {customer_geo_mismatches:,} dòng Dim_Customer "
            "có city/region/district khác Dim_Geography theo ZIP."
        )
    if customer_signup_mismatches:
        findings.append(
            f"**Cần xác minh — ngày giao dịch trước ngày đăng ký khách hàng:** "
            f"{customer_signup_mismatches:,}/{by_name['Fact_Sales.csv']['rows']:,} dòng fact "
            f"({customer_signup_mismatches / by_name['Fact_Sales.csv']['rows'] * 100:.2f}%) "
            "có date_key trước signup_date trong Dim_Customer. Nếu signup_date là ngày tạo hồ sơ "
            "lần đầu thì đây là bất nhất thời gian; nếu mang nghĩa khác cần ghi rõ định nghĩa."
        )
    non_delivered_statuses = {
        status: amount
        for status, amount in status_net_amounts.items()
        if status != "delivered" and amount > 0
    }
    if non_delivered_statuses:
        status_summary = ", ".join(
            f"`{status}` {amount:,.2f}"
            for status, amount in sorted(non_delivered_statuses.items())
        )
        findings.append(
            "**Cần xác nhận quy tắc ghi nhận doanh thu:** Fact_Sales có net_amount dương ở các trạng thái "
            f"không phải `delivered` ({status_summary}). Nếu fact được dùng làm doanh thu đã hoàn tất, "
            "cần lọc/điều chỉnh trạng thái hoặc xác nhận cách xử lý giao dịch chưa giao/đã hủy/trả."
        )
    if date_gaps:
        findings.append(
            f"**Lịch Dim_Date bị khuyết ngày:** có {len(date_gaps):,} khoảng cách giữa các ngày liên tiếp; "
            f"ví dụ {date_gaps[0][0]} → {date_gaps[0][1]}."
        )
    for field, count in date_attribute_mismatches.items():
        findings.append(
            f"**Thuộc tính ngày không khớp:** {count:,} dòng Fact_Sales có {field} trong Dim_Date "
            "khác thành phần tương ứng của date_key."
        )
    for metric, count in fact_metrics.items():
        if count:
            findings.append(f"**Chỉ số Fact_Sales bất thường — {metric}:** {count:,} dòng.")

    if not findings:
        findings.append(
            "Không phát hiện khóa thiếu/trùng, khóa ngoại mồ côi, sai khớp địa lý/ngày hoặc "
            "sai công thức các chỉ số trong các kiểm tra đã chạy."
        )

    return {
        "foreign_keys": foreign_key_results,
        "customer_geo_mismatches": customer_geo_mismatches,
        "date_attribute_mismatches": date_attribute_mismatches,
        "date_gaps": date_gaps,
        "fact_metrics": fact_metrics,
        "status_counts": status_counts,
        "status_net_amounts": status_net_amounts,
        "customer_signup_mismatches": customer_signup_mismatches,
        "findings": findings,
    }


def make_report(profiles, checks):
    total_rows = sum(profile["rows"] for profile in profiles)
    total_size = sum(profile["file_size"] for profile in profiles)
    lines = [
        "# Báo cáo tổng hợp dữ liệu `DAAI_N1.4/golden_data`",
        "",
        f"- **Thư mục nguồn:** `{DATA_DIR}`",
        f"- **Số bảng:** {len(profiles)}",
        f"- **Tổng số bản ghi:** {total_rows:,}",
        f"- **Tổng dung lượng:** {total_size:,} byte ({total_size / (1024 ** 2):,.2f} MiB)",
        "- **Kiểu dữ liệu:** suy luận từ CSV; các tệp không khai báo schema SQL. "
        "Mã định danh dạng số nên được xem là khóa/mã, không phải đại lượng đo.",
        "",
        "## Khái niệm mô hình và chức năng",
        "",
        "Đây là mô hình dữ liệu dạng sao (star schema): các bảng `Dim_*` mô tả thực thể/phân loại "
        "dùng để lọc và nhóm phân tích; `Fact_Sales` lưu các giao dịch và chỉ số đo lường.",
        "",
        "**Grain (độ chi tiết) dự kiến của Fact_Sales:** một dòng cho một cặp "
        "`order_id` + `product_id` trong đơn hàng. Khóa này được kiểm tra như khóa ứng viên.",
        "",
        "| Bảng | Khái niệm / chức năng | Grain hoặc khóa ứng viên | Dòng | Cột | Kích thước |",
        "|---|---|---|---:|---:|---:|",
    ]
    for profile in profiles:
        key = " + ".join(profile["key_fields"])
        grain = f"`{key}`"
        if profile["name"].startswith("Dim_"):
            grain = f"một dòng / {grain}"
        elif profile["name"] == "Fact_Sales.csv":
            grain = "một dòng / đơn hàng + sản phẩm"
        lines.append(
            f"| `{profile['name']}` | {TABLE_DESCRIPTIONS[profile['name']]} | {grain} | "
            f"{profile['rows']:,} | {len(profile['columns'])} | "
            f"{profile['file_size']:,} byte ({profile['file_size'] / (1024 ** 2):.2f} MiB) |"
        )

    lines.extend([
        "",
        "### Ý nghĩa chung của các chỉ số bán hàng",
        "",
        "- `quantity`: số đơn vị sản phẩm trong dòng giao dịch.",
        "- `unit_price`: đơn giá được ghi nhận cho dòng hàng.",
        "- `gross_amount`: giá trị trước chiết khấu; kiểm tra đối chiếu với `quantity × unit_price`.",
        "- `discount_amount`: số tiền giảm giá.",
        "- `net_amount`: giá trị sau chiết khấu; kiểm tra đối chiếu với `gross_amount − discount_amount`.",
        "- `promo_count` và `has_promotion`: số lượng/cờ khuyến mãi gắn với dòng bán.",
        "- Các diễn giải này dựa trên tên cột và phép đối chiếu số liệu; cần data contract để xác nhận quy tắc kế toán/kinh doanh chính thức.",
        "",
        "## Điểm bất thường và kết quả kiểm tra",
        "",
    ])
    lines.extend(f"{index}. {finding}" for index, finding in enumerate(checks["findings"], start=1))
    lines.extend([
        "",
        "### Liên kết khóa",
        "",
        "| Liên kết | Giá trị mồ côi |",
        "|---|---:|",
    ])
    for child, child_field, parent, parent_field, missing in checks["foreign_keys"]:
        lines.append(
            f"| `{child}.{child_field}` → `{parent}.{parent_field}` | {missing:,} |"
        )

    lines.extend([
        "",
        "### Phân bố trạng thái đơn hàng trong fact",
        "",
        "| order_status | Dòng | Tổng net_amount |",
        "|---|---:|---:|",
    ])
    for status, count in sorted(checks["status_counts"].items()):
        lines.append(
            f"| `{status}` | {count:,} | "
            f"{checks['status_net_amounts'][status]:,.2f} |"
        )

    lines.extend([
        "",
        "## Mô tả chi tiết bảng và cột",
        "",
        "Trống là chuỗi rỗng trong CSV. Min/max/trung bình được tính trên giá trị hiện có; "
        "trung bình với mã định danh chỉ là thống kê kỹ thuật, không mang ý nghĩa nghiệp vụ.",
        "",
    ])
    for profile in profiles:
        lines.extend([
            f"### `{profile['name']}`",
            "",
            f"- **Chức năng:** {TABLE_DESCRIPTIONS[profile['name']]}",
            f"- **Số dòng/cột:** {profile['rows']:,}/{len(profile['columns'])}; "
            f"**dung lượng:** {profile['file_size']:,} byte; **encoding:** {profile['encoding']}.",
            f"- **Khóa ứng viên:** `{'+'.join(profile['key_fields'])}`; "
            f"**dòng có khóa trống/trùng:** {profile['key_duplicates']:,}.",
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
        "- Mô hình grain và định nghĩa nghiệp vụ được suy luận từ tên/cấu trúc cột và dữ liệu quan sát; "
        "hãy đối chiếu tài liệu thiết kế kho dữ liệu trước khi dùng làm quy tắc chính thức.",
        "- Kiểu dữ liệu báo cáo là kiểu suy luận từ CSV, không phải kiểu vật lý của bảng SQL.",
        "- Báo cáo không phát hành dữ liệu mẫu chứa thông tin cá nhân.",
        "",
    ])
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_PATH


def main():
    if not DATA_DIR.is_dir():
        raise FileNotFoundError(f"Không tìm thấy thư mục golden_data: {DATA_DIR}")
    paths = sorted(DATA_DIR.glob("*.csv"))
    if not paths:
        raise FileNotFoundError(f"Không tìm thấy CSV trong {DATA_DIR}")
    expected_tables = set(TABLE_DESCRIPTIONS)
    actual_tables = {path.name for path in paths}
    if actual_tables != expected_tables:
        missing = sorted(expected_tables - actual_tables)
        extra = sorted(actual_tables - expected_tables)
        raise ValueError(f"Danh sách bảng khác dự kiến; thiếu={missing}, thừa={extra}")

    profiles = [profile_file(path) for path in paths]
    checks = validate_data(profiles)
    report_path = make_report(profiles, checks)
    print(f"Đã phân tích {len(profiles)} bảng, {sum(p['rows'] for p in profiles):,} bản ghi.")
    print(f"Đã xuất báo cáo tổng hợp: {report_path}")


if __name__ == "__main__":
    main()
