# Project Brief

## Tên dự án
OCR Table Extractor (Tiếng Việt) — Công cụ chuyển bảng trong file PDF scan tiếng Việt thành file Excel.

## Mục tiêu cốt lõi
Xây dựng một công cụ cá nhân, chạy được trên máy của mình, nhận đầu vào là file PDF scan (ảnh, không có text layer) chứa các bảng dữ liệu tiếng Việt, và xuất ra file Excel (.xlsx) giữ đúng cấu trúc hàng/cột, đúng dấu tiếng Việt.

## Phạm vi (Scope)
- Input: file PDF scan (1 hoặc nhiều trang), có bảng, có thể có văn bản xung quanh bảng.
- Output: file .xlsx, mỗi bảng trong PDF tương ứng với 1 sheet (hoặc gộp — quyết định sau khi test).
- Ưu tiên: độ chính xác của số liệu và dấu tiếng Việt > tốc độ xử lý.
- KHÔNG cần: giao diện web, xử lý hàng loạt hàng nghìn file, deploy server. Đây là tool cá nhân chạy local.

## Đối tượng sử dụng
Chỉ mình mình dùng. Không cần tối ưu cho người dùng khác.

## Định nghĩa "xong việc" (Definition of Done)
- Chạy 1 lệnh (hoặc double-click 1 file) → chọn PDF → ra file Excel đúng cấu trúc bảng gốc, sai số dấu tiếng Việt ở mức chấp nhận được (cần tự kiểm tra lại thủ công vài file mẫu).

## Không thay đổi phần này trừ khi mục tiêu dự án thực sự thay đổi.
