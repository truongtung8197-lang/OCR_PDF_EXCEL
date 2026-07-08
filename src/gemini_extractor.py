"""
Milestone 2: Gửi ảnh trang cho Gemini API (Flash, vision) → nhận JSON có cấu trúc.

Cách chạy:
    python src/gemini_extractor.py "debug_output/PAGE 10+11+12/page_02.png"
"""

import sys
import json
import time
import re
from pathlib import Path

from dotenv import load_dotenv
import os
from google import genai
from google.genai import types

# ─── Load API key ───────────────────────────────────────────────────────────
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("LỖI: Không tìm thấy GEMINI_API_KEY trong file .env")
    print("Tạo file .env từ .env.example và điền key của bạn vào.")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)

# ─── Prompt gửi Gemini ──────────────────────────────────────────────────────
PROMPT = """Bạn là công cụ trích xuất dữ liệu từ ảnh scan tài liệu tiếng Việt.

Dưới đây là ảnh 1 trang tài liệu. Trang này có thể chứa:
- Văn bản thường (paragraph)
- Bảng số liệu (table)
- Tiêu đề nhóm (section_header)

NHIỆM VỤ CỦA BẠN:
Trả về CHÍNH XÁC một JSON object theo schema dưới đây. KHÔNG thêm bất kỳ giải thích nào, KHÔNG dùng markdown code fence, CHỈ trả về JSON thuần.

SCHEMA:
{
  "page_number": <số trang nếu biết, nếu không để null>,
  "elements": [
    {
      "type": "paragraph" | "section_header" | "table",
      // Nếu type là "paragraph" hoặc "section_header":
      "text": "nội dung văn bản",
      // Nếu type là "table":
      "header_rows": [
        ["cột 1", "cột 2", ...]  // có thể nhiều dòng header nếu bảng có header phức tạp
      ],
      "rows": [
        {
          "is_continuation_of_previous_page": true | false,
          "cells": [
            { "text": "giá trị ô", "rowspan": 1, "colspan": 1 },
            ...
          ]
        }
      ]
    }
  ]
}

QUY TẮC QUAN TRỌNG:
1. Giữ NGUYÊN số liệu y hệt như trong ảnh, KHÔNG tự làm tròn, KHÔNG tự sửa chính tả.
2. Nếu 1 ô bị merge (kéo dài nhiều dòng hoặc nhiều cột), khai báo đúng rowspan/colspan, KHÔNG lặp lại nội dung ở các ô bị merge.
3. Nếu dòng đầu tiên của bảng trên trang này rõ ràng là phần tiếp nối (không có STT, không có Mã, bắt đầu bằng nội dung dang dở) của dòng cuối trang trước, đánh dấu is_continuation_of_previous_page: true.
4. section_header: dòng tiêu đề nhóm (thường in đậm, nằm giữa các bảng) — trả về dạng section_header RIÊNG BIỆT, KHÔNG gộp vào bảng. Ví dụ: "KỆ TRÊN TỦ KEM" là section_header, không phải là 1 row trong bảng.
5. Cell rỗng (không có dữ liệu) vẫn giữ "text": "" để không lệch cột.
6. Nếu trang chỉ có văn bản thường, không có bảng, trả về elements chứa paragraph.
7. Định dạng số Việt Nam: dấu "." là phân cách nghìn, dấu "," là phân cách thập phân. Giữ nguyên định dạng gốc, không chuyển đổi.
"""


def extract_json_from_response(text: str) -> dict:
    """
    Bóc tách JSON từ response text.
    Xử lý các trường hợp:
    - Gemini trả JSON thuần
    - Gemini trả JSON trong markdown code fence ```json ... ```
    - Gemini trả JSON trong markdown code fence ``` ... ```
    - Có text thừa trước/sau JSON
    """
    # Bước 1: Tìm ```json ... ``` hoặc ``` ... ```
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
    else:
        # Bước 2: Không có code fence, thử tìm { ... } đầu tiên và cuối cùng
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_str = text[start : end + 1]
        else:
            json_str = text.strip()

    # Parse JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"LỖI: Không thể parse JSON từ response.")
        print(f"  Lỗi: {e}")
        print(f"  Response text (500 ký tự đầu): {text[:500]}")
        # Lưu response lỗi ra file để debug
        with open("debug_output/_last_error_response.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("  Đã lưu response lỗi vào debug_output/_last_error_response.txt")
        raise


def extract_table(
    image_path: str, model: str = "gemini-3.1-flash-lite-preview"
) -> dict:
    """
    Gửi 1 ảnh trang cho Gemini API, nhận JSON có cấu trúc.
    Có retry với exponential backoff khi gặp lỗi 429 (rate limit).
    """
    import PIL.Image

    img_path = Path(image_path)
    if not img_path.exists():
        print(f"LỖI: Không tìm thấy ảnh: {img_path}")
        sys.exit(1)

    # Mở ảnh
    img = PIL.Image.open(str(img_path))

    max_retries = 5
    base_delay = 2  # giây

    for attempt in range(1, max_retries + 1):
        try:
            print(f"  Đang gửi request đến Gemini ({model})...")
            response = client.models.generate_content(
                model=model, contents=[PROMPT, img]
            )

            # Kiểm tra response có nội dung không
            if not response.text:
                print("  CẢNH BÁO: Response rỗng, thử lại...")
                raise ValueError("Empty response")

            # Parse JSON
            result = extract_json_from_response(response.text)
            print("  ✓ Nhận được JSON thành công")
            return result

        except Exception as e:
            error_str = str(e).lower()

            # Kiểm tra rate limit (429)
            if (
                "429" in error_str
                or "rate" in error_str
                or "resource_exhausted" in error_str
            ):
                if attempt < max_retries:
                    delay = base_delay * (2 ** (attempt - 1))  # 2, 4, 8, 16, ...
                    print(
                        f"  ⚠ Rate limit (attempt {attempt}/{max_retries}), chờ {delay}s..."
                    )
                    time.sleep(delay)
                    continue
                else:
                    print(f"  LỖI: Rate limit vượt quá số lần retry.")
                    raise
            else:
                # Lỗi khác (API key, network, ...) — không retry
                print(f"  LỖI: {e}")
                raise

    # Không nên tới đây, nhưng phòng trường hợp
    raise RuntimeError("Không thể gọi Gemini API sau nhiều lần thử.")


def save_json_output(
    data: dict, image_path: str, output_base: str = "debug_output"
) -> str:
    """
    Lưu JSON kết quả ra file debug_output/<tên_file>/page_XX.json
    Trả về đường dẫn file đã lưu.
    """
    img_path = Path(image_path)
    # Lấy tên thư mục cha (ví dụ: "PAGE 10+11+12")
    parent_dir = img_path.parent.name
    # Tạo tên file json tương ứng (page_02.json)
    json_name = img_path.stem + ".json"

    out_dir = Path(output_base) / parent_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / json_name
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  Đã lưu JSON: {out_path}")
    return str(out_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python src/gemini_extractor.py <đường_dẫn_ảnh_png>")
        print(
            'Ví dụ: python src/gemini_extractor.py "debug_output/PAGE 10+11+12/page_02.png"'
        )
        sys.exit(1)

    image_file = sys.argv[1]
    print(f"Đang xử lý ảnh: {image_file}")

    result = extract_table(image_file)
    save_json_output(result, image_file)

    # In preview JSON ra terminal (rút gọn)
    print("\n--- Preview JSON ---")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
    print("... (xem file JSON đầy đủ trong debug_output/)")
