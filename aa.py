from pathlib import Path
from collections import defaultdict
import pandas as pd


def find_same_name_csv(root_dir):
    """
    Tìm các file CSV có cùng tên trong những thư mục con cùng cấp.
    Chỉ giữ lại tên file xuất hiện từ 2 lần trở lên.
    """
    root = Path(root_dir)

    csv_groups = defaultdict(list)

    for folder in root.iterdir():
        if not folder.is_dir():
            continue

        for csv_file in folder.glob("*.csv"):
            csv_groups[csv_file.name].append(csv_file)

    return {
        filename: paths
        for filename, paths in csv_groups.items()
        if len(paths) >= 2
    }


def read_csv_safe(path):
    """
    Đọc CSV, thử một số encoding phổ biến.
    """
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]

    last_error = None

    for encoding in encodings:
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError as e:
            last_error = e

    raise last_error


def compare_two_csv(file1, file2):
    print("=" * 100)
    print(f"File 1: {file1}")
    print(f"File 2: {file2}")

    try:
        df1 = read_csv_safe(file1)
        df2 = read_csv_safe(file2)

    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        return

    # ---------------------------------------------------------
    # 1. So sánh kích thước
    # ---------------------------------------------------------

    print("\n[1] KÍCH THƯỚC")

    print(f"{file1.parent.name}: {df1.shape}")
    print(f"{file2.parent.name}: {df2.shape}")

    if df1.shape == df2.shape:
        print("OK - Số dòng và số cột giống nhau.")
    else:
        print("KHÁC - Kích thước khác nhau.")

    # ---------------------------------------------------------
    # 2. So sánh tên cột
    # ---------------------------------------------------------

    print("\n[2] CỘT")

    cols1 = list(df1.columns)
    cols2 = list(df2.columns)

    if cols1 == cols2:
        print("OK - Tên và thứ tự cột giống nhau.")

    else:
        print("KHÁC - Cột không giống nhau.")

        only_1 = set(cols1) - set(cols2)
        only_2 = set(cols2) - set(cols1)

        if only_1:
            print("Chỉ file 1 có:", sorted(only_1))

        if only_2:
            print("Chỉ file 2 có:", sorted(only_2))

        if set(cols1) == set(cols2):
            print("Hai file có cùng cột nhưng thứ tự cột khác nhau.")

    # ---------------------------------------------------------
    # 3. So sánh dữ liệu
    # ---------------------------------------------------------

    print("\n[3] DỮ LIỆU")

    if cols1 != cols2:
        print("Không so sánh trực tiếp dữ liệu vì cấu trúc cột khác nhau.")
        return

    if len(df1) != len(df2):
        print("Không thể compare từng dòng trực tiếp vì số dòng khác nhau.")
        return

    # Chuẩn hóa index
    df1 = df1.reset_index(drop=True)
    df2 = df2.reset_index(drop=True)

    if df1.equals(df2):
        print("OK - Hai file GIỐNG HỆT NHAU.")
        return

    print("KHÁC - Có dữ liệu khác nhau.")

    # ---------------------------------------------------------
    # 4. Tìm cell khác nhau
    # ---------------------------------------------------------

    diff_mask = (
        df1.ne(df2) &
        ~(df1.isna() & df2.isna())
    )

    rows_diff = diff_mask.any(axis=1)

    print(f"Số dòng khác nhau: {rows_diff.sum()}")

    # Các cột có khác biệt
    changed_columns = diff_mask.any(axis=0)

    print("\nCác cột có dữ liệu khác:")

    for col in df1.columns[changed_columns]:
        count = diff_mask[col].sum()
        print(f"  - {col}: {count} dòng")

    # ---------------------------------------------------------
    # 5. Hiển thị ví dụ
    # ---------------------------------------------------------

    print("\nVí dụ các dòng khác nhau:")

    indices = df1.index[rows_diff][:10]

    for idx in indices:

        print(f"\n--- Row {idx} ---")

        for col in df1.columns:

            if diff_mask.loc[idx, col]:
                print(
                    f"{col}: "
                    f"{file1.parent.name}={df1.loc[idx, col]!r} | "
                    f"{file2.parent.name}={df2.loc[idx, col]!r}"
                )


def compare_csv_folders(root_dir):
    groups = find_same_name_csv(root_dir)

    if not groups:
        print("Không tìm thấy CSV trùng tên giữa các thư mục.")
        return

    print(f"Tìm thấy {len(groups)} tên CSV cần so sánh.\n")

    for filename, files in sorted(groups.items()):

        print("\n")
        print("#" * 100)
        print(f"CSV: {filename}")
        print("#" * 100)

        # Lấy file đầu làm chuẩn
        base_file = files[0]

        for other_file in files[1:]:
            compare_two_csv(base_file, other_file)


if __name__ == "__main__":

    ROOT_DIR = Path(__file__).resolve().parent

    compare_csv_folders(ROOT_DIR)