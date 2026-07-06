"""
Milestone 6: Ghép toàn bộ pipeline
- Input: 1 file PDF
- Output: 1 file Excel (.xlsx) cùng tên

Cách chạy:
    python src/main.py test-samples/PAGE\ 10+11+12.pdf
"""

import sys
import json
from pathlib import Path

from pdf_to_images import pdf_to_images
from gemini_extractor import extract_table
from stitcher import stitch_pages
from excel_writer import json_to_excel


def process_pdf(pdf_path: str):
    """
    Xử lý 1 file PDF hoàn chỉnh: PDF → ảnh → JSON → ghép → Excel.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"LỖI: Không tìm thấy file PDF: {pdf_path}")
        sys.exit(1)

    pdf_stem = pdf_path.stem
    
    # Đọc config và in thông báo định dạng số
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        decimal_sep = config.get("decimal_separator", ",")
        thousand_sep = config.get("thousand_separator", ".")
        print(f"\n{'='*60}")
        print(f"Đang xử lý: {pdf_path.name}")
        print(f"Định dạng số: dấu '{thousand_sep}' = phân cách nghìn, dấu '{decimal_sep}' = phân cách thập phân")
        print(f"(Chỉnh trong config.json nếu file này dùng định dạng khác)")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print(f"Đang xử lý: {pdf_path.name}")
        print(f"{'='*60}")

    # Bước 1: PDF → ảnh
    print("\n[Bước 1/4] Chuyển PDF → ảnh...")
    image_paths = pdf_to_images(pdf_path, output_dir="debug_output", dpi=300)
    if not image_paths:
        print("LỖI: Không tạo được ảnh nào từ PDF.")
        sys.exit(1)
    print(f"  ✓ Đã tạo {len(image_paths)} ảnh")

    # Bước 2: Gọi Gemini cho từng ảnh
    print("\n[Bước 2/4] Gọi Gemini API trích xuất JSON...")
    json_files = []
    for img_path in image_paths:
        print(f"\n  Đang xử lý: {Path(img_path).name}")
        try:
            result = extract_table(img_path)
            # Lưu JSON
            from gemini_extractor import save_json_output
            json_file = save_json_output(result, img_path, output_base="debug_output")
            json_files.append(json_file)
        except Exception as e:
            print(f"  ⚠ Lỗi khi xử lý {img_path}: {e}")
            print(f"  Bỏ qua trang này và tiếp tục...")
            continue

    if not json_files:
        print("\nLỖI: Không có trang nào xử lý thành công.")
        sys.exit(1)

    print(f"\n  ✓ Đã tạo {len(json_files)} file JSON")

    # Bước 3: Ghép nối các trang (đơn giản: nối chồng theo thứ tự)
    print("\n[Bước 3/4] Ghép nối các trang...")
    stitched_data = stitch_pages(json_files)
    print(f"  ✓ Đã ghép {len(json_files)} trang → {len(stitched_data.get('elements', []))} elements")

    # Bước 4: Xuất Excel
    print("\n[Bước 4/4] Xuất Excel...")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{pdf_stem}.xlsx"

    json_to_excel(stitched_data, str(output_file))

    print(f"\n{'='*60}")
    print(f"✓ HOÀN TẤT!")
    print(f"  File Excel: {output_file}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python src/main.py <đường_dẫn_file_pdf>")
        print("Ví dụ: python src/main.py test-samples/PAGE\\ 10+11+12.pdf")
        sys.exit(1)

    pdf_file = sys.argv[1]
    process_pdf(pdf_file)