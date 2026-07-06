# PLAN.md — Kế hoạch phát triển chi tiết
## OCR Table Extractor (PDF scan tiếng Việt → Excel)

> File này là bản kế hoạch tổng, dùng để giao việc từng phần cho Cline + DeepSeek.
> Khi bắt đầu 1 phiên code mới, nói với Cline: "Đọc PLAN.md và memory-bank/, chúng ta đang ở Milestone X".

---

## 1. Quyết định kiến trúc (đã chốt)

**Engine OCR/trích xuất: Gemini API (model Flash, vision), KHÔNG dùng Tesseract/PaddleOCR.**

Lý do:
- Miễn phí (free tier), đã có sẵn API key.
- Xử lý được ô merge phức tạp bằng cách hiểu ngữ nghĩa bảng, không chỉ nhận diện ký tự.
- Tiếng Việt (dấu thanh) được model ngôn ngữ lớn xử lý tốt hơn OCR cổ điển.
- Code để gọi API đơn giản hơn nhiều so với dựng pipeline table-detection + OCR riêng.

Đánh đổi cần chấp nhận:
- Cần internet khi chạy (không offline 100%).
- Free tier của Google có thể dùng dữ liệu gửi lên để cải thiện model (đã xác nhận dữ liệu của bạn không nhạy cảm nên chấp nhận được).
- Có giới hạn tốc độ (~10-15 request/phút) → cần code có cơ chế chờ/retry, không phải vấn đề với khối lượng dùng mỗi tuần của bạn.
- Vẫn có rủi ro hallucination (model "bịa" số) → bắt buộc phải có bước validate ở Milestone 5.

DeepSeek (qua Cline) chỉ đóng vai trò viết code, KHÔNG dùng để OCR.

---

## 2. Kiến trúc pipeline

```
[PDF file]
    │
    ▼
(M1) Tách từng trang PDF → ảnh (PyMuPDF, DPI cao ~300)
    │  + deskew nhẹ nếu ảnh bị nghiêng (OpenCV)
    ▼
(M2) Gửi từng ảnh trang → Gemini API, nhận về JSON có cấu trúc
     (mỗi trang: đoạn văn thường / bảng / tiêu đề nhóm)
    ▼
(M3) Ghi JSON của 1 trang → Excel (merge cell, format số) — thử với bảng đơn giản trước
    ▼
(M4) Module "ghép nối" nhiều trang:
     - Nhận diện & bỏ header lặp lại
     - Nối dòng bị cắt ngang trang
     - Tách tiêu đề nhóm ra khỏi bảng dữ liệu
    ▼
(M5) Module validate số liệu: kiểm tra công thức (3)=(1)×(2),
     đánh dấu màu các ô nghi ngờ sai để bạn rà tay
    ▼
(M6) Ghép toàn bộ pipeline: 1 file PDF (nhiều trang, có cả trang 1 dạng văn bản)
     → 1 file Excel cùng tên
    ▼
(M7) Test với file thật, đo tỷ lệ đúng, tinh chỉnh prompt & logic ghép nối
```

---

## 3. Cấu trúc dữ liệu trung gian (JSON) — mỗi trang trả về dạng này

```json
{
  "page_number": 6,
  "elements": [
    { "type": "paragraph", "text": "Nội dung văn bản thường (nếu có)" },
    { "type": "section_header", "text": "KỆ TRÊN TỦ KEM" },
    {
      "type": "table",
      "header_rows": [
        ["STT", "Mã", "Hàng hóa (đơn vị kích thước: mm)", "Đơn vị", "Khối lượng", "Đơn giá chi tiết", "Đơn giá thành phần", "Đơn giá Module"]
      ],
      "rows": [
        {
          "is_continuation_of_previous_page": true,
          "cells": [
            { "text": "", "rowspan": 1, "colspan": 1 },
            { "text": "", "rowspan": 1, "colspan": 1 },
            { "text": "lập - WiN/Urban", "rowspan": 1, "colspan": 1 }
          ]
        },
        {
          "is_continuation_of_previous_page": false,
          "cells": [
            { "text": "1", "rowspan": 1, "colspan": 1 },
            { "text": "KD-90.35.200-DL-RR", "rowspan": 1, "colspan": 1 }
          ]
        }
      ]
    }
  ]
}
```

Ghi chú quan trọng:
- `is_continuation_of_previous_page`: đánh dấu để module M4 biết cần nối dòng này với dòng cuối cùng của trang trước, không tạo dòng Excel mới.
- `section_header`: dòng tiêu đề nhóm (merge toàn bộ chiều ngang bảng) — ghi ra Excel dưới dạng 1 hàng merge full-width, in đậm.
- Cell rỗng (không có dữ liệu) vẫn giữ `text: ""` để không lệch cột khi ghép.

---

## 4. Xử lý số liệu (rất quan trọng, dễ sai)

- Định dạng số Việt Nam: dấu `.` là phân cách nghìn, dấu `,` là phân cách thập phân (ngược với chuẩn US/Excel mặc định).
  - `2.404.844` → số 2404844 (integer)
  - Nếu gặp `1.234,56` → số 1234.56
- Viết 1 hàm `parse_vn_number(text: str) -> float | None` dùng chung cho toàn bộ pipeline, test riêng hàm này với nhiều case trước khi dùng.
- Cột có công thức: **Đơn giá thành phần (cột 3) = Khối lượng (cột 1) × Đơn giá chi tiết (cột 2)**. Dùng công thức này ở Milestone 5 để validate — không phải để tính lại giá trị, mà để PHÁT HIỆN ô mà Gemini đọc sai số.

---

## 5. Milestones — giao việc từng phần cho Cline

### M0 — Setup môi trường
- Tạo virtual env Python 3.12, `requirements.txt` (pymupdf, opencv-python, openpyxl, google-genai, python-dotenv).
- Tạo `.env` chứa `GEMINI_API_KEY` (KHÔNG commit file này lên git — thêm vào `.gitignore`).
- Cấu trúc thư mục:
  ```
  project/
  ├── .env
  ├── .gitignore
  ├── .clinerules
  ├── memory-bank/
  ├── test-samples/         ← để 2 file PDF mẫu vào đây
  ├── src/
  │   ├── pdf_to_images.py
  │   ├── gemini_extractor.py
  │   ├── stitcher.py        (module ghép nối M4)
  │   ├── validator.py       (module M5)
  │   ├── excel_writer.py
  │   └── main.py
  ├── debug_output/          ← ảnh trung gian, JSON thô để debug
  └── output/                ← file Excel kết quả
  ```

### M1 — PDF → ảnh
- Input: 1 file PDF. Output: ảnh PNG từng trang, lưu vào `debug_output/`.
- Thử deskew đơn giản bằng OpenCV, so sánh trước/sau bằng mắt.
- Test bằng 2 file mẫu đã có.

### M2 — Gọi Gemini trích xuất 1 trang
- Viết prompt chi tiết (xem mục 6) yêu cầu Gemini trả về đúng JSON schema ở mục 3.
- Test với `test_ocr_page6.pdf` và `test_ocr_page11.pdf` → in JSON ra, tự kiểm tra bằng mắt so với ảnh gốc.
- Xử lý lỗi: retry khi gặp 429 (rate limit), parse lỗi JSON (model đôi khi trả thêm text thừa quanh JSON).

### M3 — JSON → Excel (1 trang đơn giản)
- Viết hàm nhận JSON 1 trang, ghi ra Excel: đúng hàng/cột, merge cell theo `rowspan`/`colspan`, section_header thành hàng merge full-width in đậm.
- Test với trang 11 (không có dòng bị cắt ngang trang) trước vì đơn giản hơn trang 6.

### M4 — Ghép nối nhiều trang (đã đơn giản hóa)
- **Đã đổi sang nối chồng đơn giản:** chỉ nối tất cả elements theo thứ tự, KHÔNG merge header, KHÔNG chỉnh sửa gì.
- Lý do: merge header đang gây sai lệch dữ liệu khi các trang có cấu trúc khác nhau.

### M5 — (ĐÃ BỎ) Không cần validate công thức
- Người dùng chỉ cần giữ nguyên số liệu đã scan đúng, không cần kiểm tra công thức (3)=(1)×(2).
- Bỏ qua milestone này, chuyển thẳng sang M6.

### M6 — Ghép toàn bộ pipeline
- `main.py`: nhận đường dẫn 1 file PDF → chạy hết M1-M5 → xuất `output/<tên_file>.xlsx`.
- Xử lý trang 1 (văn bản thường): trích xuất text, ghi vào 1 sheet riêng tên "Trang 1" hoặc để đầu file Excel.
- Trang bảng: có thể gộp tất cả bảng vào 1 sheet chính, hoặc mỗi "hạng mục" (section) 1 sheet — cần bạn quyết định khi tới bước này (Cline nên hỏi bạn lúc này thay vì tự quyết).

### M7 — Xử lý định dạng số Việt Nam + test thật
- **Xử lý định dạng số:** Hỏi người dùng dấu nào là thập phân (chấm hay phẩy), từ đó suy ra dấu còn lại là phân cách nghìn. Format lại số cho đúng trước khi ghi vào Excel.
- Chạy với file PDF thật nhiều trang (5-50 trang).
- Đối chiếu tay, ghi lại % dòng đúng vào `progress.md`.
- Nếu Gemini đọc sai nhiều ở 1 dạng cụ thể (vd: số có nhiều chữ số, mã sản phẩm có ký tự lạ) → tinh chỉnh lại prompt ở M2, không cần sửa toàn bộ pipeline.

---

## 6. Khung prompt gửi Gemini (bản nháp — Cline sẽ tinh chỉnh khi code M2)

Yêu cầu prompt cần nêu rõ:
- Đây là ảnh 1 trang tài liệu tiếng Việt, có thể là văn bản thường hoặc bảng số liệu.
- Nếu là bảng: trả về CHÍNH XÁC theo JSON schema đã định nghĩa (đưa schema mẫu vào prompt).
- Giữ nguyên số liệu y hệt như trong ảnh, không tự làm tròn, không tự sửa chính tả.
- Nếu 1 ô bị merge (kéo dài nhiều dòng hoặc nhiều cột), khai báo đúng `rowspan`/`colspan`, không lặp lại nội dung ở các ô bị merge.
- Nếu dòng đầu tiên của bảng trên trang này rõ ràng là phần tiếp nối (không có STT, không có Mã) của dòng cuối trang trước, đánh dấu `is_continuation_of_previous_page: true`.
- Chỉ trả về JSON thuần, không thêm giải thích, không thêm markdown code fence.

---

## 7. Rủi ro đã biết & phương án dự phòng

| Rủi ro | Phương án dự phòng |
|---|---|
| Gemini hallucinate số liệu | Validate bằng công thức (3)=(1)×(2) ở M5; rà tay đến khi đạt >90% |
| Free tier bị giới hạn/ngừng đột ngột | Có thể chuyển sang model Gemini khác cùng free tier, hoặc tạo project Google Cloud mới; ghi lại trong techContext.md nếu xảy ra |
| Cấu trúc bảng quá đa dạng, logic ghép nối (M4) không bao quát hết | Chấp nhận xử lý dần theo từng loại file thực tế gặp phải, không cố tổng quát hoá trước khi thấy đủ ví dụ thật |
| Ảnh scan quá mờ ở 1 số file | Thêm bước tiền xử lý ảnh (tăng tương phản) chỉ khi thực sự gặp file mờ, không làm trước khi cần |

---

## 8. Câu hỏi còn mở (quyết định khi tới milestone liên quan)
- M6: Mỗi hạng mục 1 sheet Excel, hay gộp chung 1 sheet?
- Cần lấy thêm 2 trang PDF thật LIỀN NHAU (không cắt rời) để test M4 cho chính xác.
