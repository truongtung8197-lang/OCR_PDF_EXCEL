"""
Milestone 3: Chuyển JSON của 1 trang → file Excel (.xlsx)
- Đúng hàng/cột, merge cell theo rowspan/colspan
- section_header thành hàng merge full-width in đậm
- Format số Việt Nam theo config.json

Cách chạy:
    python src/excel_writer.py debug_output/PAGE\ 3+4/page_01.json
"""

import sys
import json
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

# Đọc config định dạng số
CONFIG_PATH = Path("config.json")
NUMBER_CONFIG = {
    "decimal_separator": ",",
    "thousand_separator": "."
}
if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        user_config = json.load(f)
        NUMBER_CONFIG.update(user_config)

# Cột cần parse thành số (dựa vào tên cột trong header)
NUMERIC_COLUMNS = {
    "khối lượng",
    "đơn giá chi tiết",
    "đơn giá thành phần",
    "đơn giá module"
}


def parse_vn_number(text: str):
    """
    Chuyển chuỗi số Việt Nam thành float dựa trên config.
    - "2.404.844" → 2404844.0 (nếu thousand=".", decimal=",")
    - "1.234,56" → 1234.56 (nếu thousand=".", decimal=",")
    - Trả về None nếu không phải số.
    """
    if not text or not isinstance(text, str):
        return None
    text = text.strip()
    if not text:
        return None

    # Loại bỏ dấu cách
    text = text.replace(" ", "")
    
    thousand_sep = NUMBER_CONFIG.get("thousand_separator", ".")
    decimal_sep = NUMBER_CONFIG.get("decimal_separator", ",")

    # Nếu có cả thousand và decimal
    if thousand_sep in text and decimal_sep in text:
        text = text.replace(thousand_sep, "").replace(decimal_sep, ".")
    # Nếu chỉ có thousand_sep (không có decimal_sep)
    elif thousand_sep in text and decimal_sep not in text:
        # Nếu có nhiều hơn 1 dấu thousand → chắc chắn là phân cách nghìn
        if text.count(thousand_sep) > 1:
            text = text.replace(thousand_sep, "")
        else:
            # 1 dấu → phân cách nghìn (vì không có decimal_sep, đây là quy ước Việt Nam)
            text = text.replace(thousand_sep, "")
    # Nếu chỉ có decimal_sep
    elif decimal_sep in text:
        text = text.replace(decimal_sep, ".")

    try:
        return float(text)
    except ValueError:
        return None


def apply_cell_style(cell, is_header: bool = False, is_section: bool = False):
    """Áp dụng style cho cell."""
    if is_section:
        # Section header: in đậm, merge full-width
        cell.font = Font(bold=True, size=12)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    elif is_header:
        # Table header: in đậm, nền xám nhạt
        cell.font = Font(bold=True, size=11)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
    else:
        # Normal cell
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # Border
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )
    cell.border = thin_border


def write_table(ws, table_data: dict, start_row: int = 1) -> int:
    """
    Ghi 1 bảng vào worksheet.
    Trả về số dòng cuối cùng đã ghi.
    """
    header_rows = table_data.get("header_rows", [])
    rows = table_data.get("rows", [])

    if not header_rows and not rows:
        return start_row

    current_row = start_row
    num_cols = len(header_rows[0]) if header_rows else (len(rows[0]["cells"]) if rows else 0)

    # Xác định cột nào là cột số dựa vào tên header
    numeric_col_indices = set()
    if header_rows:
        # Lấy header row đầu tiên
        first_header = header_rows[0]
        for col_idx, header_text in enumerate(first_header, 1):
            # Chuẩn hóa tên cột: lowercase, bỏ \n, bỏ phần trong ngoặc đơn (vd: "(1)", "(2)")
            header_normalized = " ".join(header_text.replace("\n", " ").split()).lower()
            # Bỏ phần trong ngoặc đơn (vd: "khối lượng (1)" → "khối lượng")
            header_normalized = re.sub(r'\s*\([^)]*\)', '', header_normalized).strip()
            # Kiểm tra xem có phải cột số không
            for numeric_col in NUMERIC_COLUMNS:
                if numeric_col in header_normalized:
                    numeric_col_indices.add(col_idx)
                    break

    # Ghi header rows
    for header_row in header_rows:
        for col_idx, cell_text in enumerate(header_row, 1):
            cell = ws.cell(row=current_row, column=col_idx, value=cell_text)
            apply_cell_style(cell, is_header=True)
        current_row += 1

    # Ghi data rows
    for row_data in rows:
        cells = row_data.get("cells", [])
        col_idx = 1
        cell_idx = 0

        while cell_idx < len(cells):
            cell_info = cells[cell_idx]
            text = cell_info.get("text", "")
            rowspan = cell_info.get("rowspan", 1)
            colspan = cell_info.get("colspan", 1)

            # Chỉ parse số nếu cột này là cột số
            if col_idx in numeric_col_indices and text:
                value = parse_vn_number(text)
            else:
                value = None

            # Ghi cell
            cell = ws.cell(row=current_row, column=col_idx, value=value if value is not None else text)
            apply_cell_style(cell, is_header=False)

            # Merge cell nếu cần
            if rowspan > 1 or colspan > 1:
                ws.merge_cells(
                    start_row=current_row,
                    start_column=col_idx,
                    end_row=current_row + rowspan - 1,
                    end_column=col_idx + colspan - 1
                )

            col_idx += colspan
            cell_idx += 1

        current_row += 1

    return current_row


def json_to_excel(json_data: dict, output_path: str):
    """
    Chuyển JSON của 1 trang thành file Excel.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Trang 1"

    current_row = 1

    # Duyệt qua các elements
    for element in json_data.get("elements", []):
        elem_type = element.get("type")

        if elem_type == "section_header":
            # Ghi section header: merge full-width, in đậm
            text = element.get("text", "")
            num_cols = 8  # Số cột mặc định (có thể điều chỉnh)
            ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=num_cols)
            cell = ws.cell(row=current_row, column=1, value=text)
            apply_cell_style(cell, is_section=True)
            current_row += 1

        elif elem_type == "table":
            # Ghi bảng
            end_row = write_table(ws, element, start_row=current_row)
            current_row = end_row

        elif elem_type == "paragraph":
            # Ghi đoạn văn bản thường
            text = element.get("text", "")
            if text:
                ws.cell(row=current_row, column=1, value=text)
                current_row += 1

    # Auto-adjust column widths
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)  # Giới hạn max 50
        ws.column_dimensions[column].width = adjusted_width

    # Lưu file
    wb.save(output_path)
    print(f"  ✓ Đã lưu Excel: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python src/excel_writer.py <đường_dẫn_file_json>")
        print("Ví dụ: python src/excel_writer.py debug_output/PAGE\\ 3+4/page_01.json")
        sys.exit(1)

    json_file = sys.argv[1]
    json_path = Path(json_file)

    if not json_path.exists():
        print(f"LỖI: Không tìm thấy file JSON: {json_file}")
        sys.exit(1)

    # Đọc JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Tạo tên file output
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{json_path.stem}.xlsx"

    print(f"Đang chuyển JSON → Excel...")
    json_to_excel(data, str(output_file))
    print(f"Hoàn tất! File Excel: {output_file}")