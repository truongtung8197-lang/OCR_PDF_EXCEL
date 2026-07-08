# Progress

## Đã hoạt động (Working)
- Đã hoàn thành Milestone 0-7b: setup môi trường, PDF → ảnh, gọi Gemini API, JSON → Excel, ghép nối trang, pipeline hoàn chỉnh, xử lý định dạng số Việt Nam qua config.json.
- Đã test thành công với 3 file PDF mẫu:
  - `PAGE 3+4.pdf` (2 trang) → JSON + Excel hoạt động tốt
  - `PAGE 10+11+12.pdf` (3 trang) → ghép nối thành công
  - `ORIGINAL.pdf` (38 trang) → **chạy thành công end-to-end, skip ảnh+JSON cũ, fix lỗi rowspan + MergedCell**

## Đã sửa
- **Skip Bước 1 (ảnh):** main.py kiểm tra thư mục ảnh tồn tại → bỏ qua tạo ảnh mới.
- **Skip Bước 2 (JSON):** main.py kiểm tra JSON tồn tại → bỏ qua gọi Gemini API.
- **Fix rowspan lệch cột (excel_writer.py):** Thêm active_rowspans tracking + post-processing tự sửa lỗi Gemini trả STT sai rowspan.
- **Fix MergedCell (excel_writer.py):** Bỏ qua MergedCell khi auto-adjust column widths.

## Chưa làm (Còn thiếu)
- [x] Chuyển PDF → ảnh
- [x] Tiền xử lý ảnh (xoay, khử nhiễu)
- [x] Nhận diện vùng bảng
- [x] OCR nội dung ô
- [x] Ghép nối nhiều trang (nối chồng đơn giản)
- [x] Xuất Excel
- [x] Xử lý định dạng số Việt Nam qua config.json
- [x] Viết README hướng dẫn chạy
- [x] Skip Bước 1+2 nếu có ảnh/JSON cũ
- [x] Fix rowspan lệch cột + MergedCell
- [ ] Test với nhiều file mẫu thực tế
- [ ] Fix bug: "KỆ TRÊN TỦ KEM" bị Gemini nhét sai vào bảng

## Lỗi/vấn đề đã biết (Known Issues)
- Một số trang Gemini không nhận diện được merge cell (vd trang 32: "Giá kệ để hàng" + "4 tầng đợt" đáng lẽ merge 4 dòng nhưng Gemini trả từng dòng riêng).
- File `page_02.json` (PAGE 10+11+12): "KỆ TRÊN TỦ KEM" bị Gemini nhét vào bảng.
- Stitcher dùng nối chồng đơn giản, không merge header.
- Header có dạng "Khối lượng (1)" đã xử lý bằng regex bỏ ngoặc đơn.

## Lịch sử thay đổi lớn
- Đổi từ Tesseract → Gemini API (gemini-3.1-flash-lite-preview).
- Bỏ Milestone 5 (validate công thức).
- Đổi stitcher từ merge header → nối chồng đơn giản.
- Thêm M7b: xử lý định dạng số Việt Nam qua config.json.
- **Fix pipeline:** thêm skip Bước 1+2 nếu đã có ảnh/JSON.
- **Fix excel_writer:** rowspan tracking + post-processing STT + MergedCell.