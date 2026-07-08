"""
Milestone 4: Module ghép nối nhiều trang
- Bỏ header lặp khi ghép 2 trang liên tiếp của cùng 1 bảng
- Xử lý dòng is_continuation_of_previous_page: nối vào dòng cuối của trang trước
- Tách section_header ra khỏi bảng dữ liệu

Cách chạy:
    python src/stitcher.py "debug_output/PAGE 10+11+12/page_01.json" "debug_output/PAGE 10+11+12/page_02.json" "debug_output/PAGE 10+11+12/page_03.json"
"""

import sys
import json
from pathlib import Path


def normalize_header(header: list) -> list:
    """Chuẩn hóa header: bỏ \n, bỏ khoảng trắng thừa, lowercase để so sánh."""
    normalized = []
    for cell in header:
        # Bỏ \n, \r, tab; gộp nhiều khoảng trắng thành 1; lowercase
        normalized.append(
            " ".join(
                cell.replace("\n", " ").replace("\r", " ").replace("\t", " ").split()
            ).lower()
        )
    return normalized


def are_headers_equal(header1: list, header2: list) -> bool:
    """So sánh 2 header rows có giống nhau không (đã chuẩn hóa)."""
    if len(header1) != len(header2):
        return False
    norm1 = normalize_header(header1)
    norm2 = normalize_header(header2)
    for cell1, cell2 in zip(norm1, norm2):
        if cell1 != cell2:
            return False
    return True


def stitch_pages(json_files: list[str]) -> dict:
    """
    Ghép nhiều file JSON của các trang liên tiếp thành 1 JSON duy nhất.
    Đơn giản: nối chồng tất cả elements theo thứ tự, không merge hay chỉnh sửa gì.
    """
    if not json_files:
        return {"elements": []}

    # Đọc tất cả các trang và nối chồng lại
    result = {"elements": []}
    for json_file in json_files:
        path = Path(json_file)
        if not path.exists():
            print(f"  ⚠ Không tìm thấy file: {json_file}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            elements = data.get("elements", [])
            result["elements"].extend(elements)

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python src/stitcher.py <file_json_1> <file_json_2> ...")
        print(
            'Ví dụ: python src/stitcher.py "debug_output/PAGE 10+11+12/page_01.json" "debug_output/PAGE 10+11+12/page_02.json"'
        )
        sys.exit(1)

    json_files = sys.argv[1:]
    print(f"Đang ghép {len(json_files)} trang...")

    result = stitch_pages(json_files)

    # Lưu kết quả
    output_dir = Path("debug_output/stitched")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Tạo tên file output từ tên thư mục
    if json_files:
        first_path = Path(json_files[0])
        parent_dir = first_path.parent.name
        output_file = output_dir / f"{parent_dir}_stitched.json"
    else:
        output_file = output_dir / "stitched.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"  ✓ Đã lưu kết quả ghép: {output_file}")
    print(f"  Tổng số elements: {len(result.get('elements', []))}")
