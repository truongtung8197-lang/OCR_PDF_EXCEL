# Active Context

> File này cập nhật THƯỜNG XUYÊN NHẤT — mỗi khi kết thúc 1 phiên làm việc với Cline, nhờ AI cập nhật lại file này trước khi đóng.

## Đang làm gì (hiện tại)
- Đã hoàn thành toàn bộ pipeline (Milestone 0-6):
  - M0: Setup môi trường
  - M1: PDF → ảnh (pdf_to_images.py)
  - M2: Gọi Gemini API (gemini_extractor.py)
  - M3: JSON → Excel (excel_writer.py)
  - M4: Ghép nối nhiều trang (stitcher.py) — **Đã đổi sang nối chồng đơn giản, không merge header**
  - M5: ĐÃ BỎ — không cần validate công thức
  - M6: Pipeline hoàn chỉnh (main.py)
- **M7b (hiện tại):** Đã thêm xử lý định dạng số Việt Nam qua config.json — parse số chỉ áp dụng cho các cột số (Khối lượng, Đơn giá chi tiết, Đơn giá thành phần, Đơn giá Module), giữ nguyên text cho các cột khác (STT, Mã, Hàng hóa, Đơn vị).
- Đã test thành công end-to-end với `PAGE 3+4.pdf` và `PAGE 10+11+12.pdf`

## Quyết định gần nhất
- Chọn Gemini API (Flash, vision) thay vì Tesseract/PaddleOCR/Azure — lý do đầy đủ ở techContext.md.
- Model đang dùng: `gemini-3.1-flash-lite-preview` (có quota riêng, hoạt động tốt).
- **Bỏ Milestone 5 (validate công thức)** — người dùng chỉ cần giữ nguyên số liệu đã scan đúng.
- **Thay đổi M4 (stitcher):** Bỏ logic merge header phức tạp, chỉ đơn giản nối chồng tất cả elements theo thứ tự. Lý do: merge header đang gây sai lệch dữ liệu.
- **M7b: Xử lý định dạng số qua config.json** — không auto-detect, không hỏi người dùng. Người dùng tự sửa config.json nếu cần. Tool chỉ in thông báo định dạng đang dùng.
- File `page_02.json` (PAGE 10+11+12) có lỗi nhỏ: "KỆ TRÊN TỦ KEM" bị Gemini nhét vào bảng — sẽ xử lý sau.

## Bước tiếp theo
1. Đã hoàn thành M7b — cần test kỹ hơn với nhiều file PDF thực tế.
2. Viết README hướng dẫn chạy (cho người không rành code).

## Câu hỏi/vướng mắc đang mở
- Cần lấy thêm 2 trang PDF thật LIỀN NHAU (không cắt rời) để test Milestone 4 (ghép nối) cho chính xác.
- Milestone 6: quyết định mỗi hạng mục 1 sheet Excel hay gộp chung 1 sheet.

## Ghi chú cho AI Agent
- Luôn đọc hết các file trong memory-bank/ trước khi bắt đầu code.
- Sau khi hoàn thành 1 task, cập nhật lại "Đang làm gì", "Quyết định gần nhất", "Bước tiếp theo" trong file này, và cập nhật progress.md.