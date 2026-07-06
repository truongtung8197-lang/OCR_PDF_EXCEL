# Progress

## Đã hoạt động (Working)
- Đã hoàn thành Milestone 0-7b: setup môi trường, PDF → ảnh, gọi Gemini API, JSON → Excel, ghép nối trang, pipeline hoàn chỉnh, xử lý định dạng số Việt Nam qua config.json.
- Đã test thành công với 2 file PDF mẫu:
  - `PAGE 3+4.pdf` (2 trang) → JSON + Excel hoạt động tốt, parse số đúng theo config
  - `PAGE 10+11+12.pdf` (3 trang) → đã tạo JSON cho cả 3 trang, ghép nối thành công

## Đang làm / còn dang dở
- Đã hoàn thành M7b: xử lý định dạng số Việt Nam qua config.json.
- Cần test kỹ hơn với nhiều file PDF thực tế để đảm bảo ổn định.

## Chưa làm (Còn thiếu)
- [x] Chuyển PDF → ảnh
- [x] Tiền xử lý ảnh (xoay, khử nhiễu)
- [x] Nhận diện vùng bảng
- [x] OCR nội dung ô
- [x] Ghép nối nhiều trang (đổi sang nối chồng đơn giản, không merge header)
- [x] Xuất Excel
- [x] Xử lý định dạng số Việt Nam qua config.json (M7b)
- [ ] Test với nhiều file mẫu thực tế
- [ ] Viết README hướng dẫn chạy (cho người không rành code)

## Lỗi/vấn đề đã biết (Known Issues)
- File `page_02.json` (PAGE 10+11+12) có lỗi nhỏ: "KỆ TRÊN TỦ KEM" bị Gemini nhét vào bảng thay vì thành section_header riêng — sẽ xử lý sau bằng post-processing hoặc sửa tay.
- Stitcher đã đổi sang nối chồng đơn giản, không merge header (theo yêu cầu người dùng).
- Một số header có dạng "Khối lượng (1)", "Đơn giá chi tiết (2)" — đã xử lý bằng regex để bỏ phần trong ngoặc đơn trước khi so khớp tên cột số.

## Lịch sử thay đổi lớn
- (ngày) — Đổi từ Tesseract sang Gemini API (gemini-3.1-flash-lite-preview) vì độ chính xác dấu tiếng Việt tốt hơn.
- (ngày) — Bỏ Milestone 5 (validate công thức) — người dùng chỉ cần giữ nguyên số liệu đã scan đúng.
- (ngày) — Đổi stitcher từ merge header phức tạp sang nối chồng đơn giản, tránh sai lệch dữ liệu.
- (ngày) — Thêm M7b: xử lý định dạng số Việt Nam qua config.json (không auto-detect, không hỏi người dùng). Chỉ parse số cho các cột số (Khối lượng, Đơn giá chi tiết, Đơn giá thành phần, Đơn giá Module), giữ nguyên text cho các cột khác.