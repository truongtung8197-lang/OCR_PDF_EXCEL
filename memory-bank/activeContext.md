# Active Context

> File này cập nhật THƯỜNG XUYÊN NHẤT — mỗi khi kết thúc 1 phiên làm việc với Cline, nhờ AI cập nhật lại file này trước khi đóng.

## Đang làm gì (hiện tại)
- Đã hoàn thành toàn bộ pipeline (Milestone 0-7b + fix):
  - M0: Setup môi trường
  - M1: PDF → ảnh (pdf_to_images.py)
  - M2: Gọi Gemini API (gemini_extractor.py)
  - M3: JSON → Excel (excel_writer.py) — **Đã sửa lỗi rowspan lệch cột + MergedCell**
  - M4: Ghép nối nhiều trang (stitcher.py) — nối chồng đơn giản, không merge header
  - M5: ĐÃ BỎ
  - M6: Pipeline hoàn chỉnh (main.py)
  - M7b: Xử lý định dạng số Việt Nam qua config.json
- **Fix skip (mới):** main.py Bước 1 + Bước 2 kiểm tra ảnh/JSON cũ, nếu có → bỏ qua
- **Fix excel_writer (mới):**
  - Rowspan tracking: không ghi lệch cột khi có merge rowspan
  - Post-processing: tự động sửa lỗi Gemini trả rowspan sai ở cột STT (số mà rowspan>1)
  - Chèn cell rỗng nếu dòng con thiếu cell STT
  - Bỏ qua MergedCell khi auto-adjust column widths

## Quyết định gần nhất
- Chọn Gemini API (Flash, vision) thay vì Tesseract/PaddleOCR/Azure.
- Model: `gemini-3.1-flash-lite-preview`.
- Bỏ Milestone 5 (validate công thức).
- Bỏ merge header phức tạp → nối chồng đơn giản.
- Xử lý định dạng số qua config.json (không auto-detect).
- **Thêm post-processing trong excel_writer.py** để tự sửa lỗi Gemini về rowspan (trang 22): nếu cột STT có rowspan>1 và là số → fix về rowspan=1; nếu dòng có ít cells hơn header → chèn cell rỗng.

## Bước tiếp theo
1. Test kỹ hơn với nhiều file PDF thực tế.
2. Fix bug: "KỆ TRÊN TỦ KEM" bị Gemini nhét sai vào bảng thay vì section_header riêng.

## Câu hỏi/vướng mắc đang mở
- Cần lấy thêm 2 trang PDF thật LIỀN NHAU để test ghép nối.
- Mỗi hạng mục 1 sheet Excel hay gộp chung 1 sheet.

## Ghi chú cho AI Agent
- Luôn đọc hết các file trong memory-bank/ trước khi bắt đầu code.
- Sau khi hoàn thành 1 task, cập nhật lại "Đang làm gì", "Quyết định gần nhất", "Bước tiếp theo" trong file này, và cập nhật progress.md.