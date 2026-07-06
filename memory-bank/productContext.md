# Product Context

## Vấn đề đang gặp phải
Có nhiều file PDF là bản scan (ảnh chụp/scan giấy) chứa bảng số liệu tiếng Việt, cần nhập lại vào Excel để xử lý/tính toán. Nhập tay tốn thời gian và dễ sai sót.

## Vì sao cần tool này
- Tiết kiệm thời gian nhập liệu thủ công.
- Giảm sai sót khi gõ lại số liệu từ bảng scan.
- Tái sử dụng được cho nhiều file có cấu trúc bảng tương tự nhau.

## Trải nghiệm mong muốn
- Đơn giản nhất có thể: 1 script hoặc 1 tool nhỏ, không cần thao tác phức tạp.
- Có thể xem lại/so sánh kết quả OCR với bản gốc để sửa tay những chỗ sai (không kỳ vọng OCR đúng 100%).
- Dễ chạy lại nhiều lần khi có file mới, không cần cài đặt lại từ đầu mỗi lần.

## Rủi ro/điều cần lưu ý
- OCR tiếng Việt dễ sai dấu thanh (ví dụ: à/á/ả/ã/ạ) — cần có bước kiểm tra/so sánh.
- Bảng bị nghiêng, mờ, hoặc kẻ ô không rõ ràng sẽ làm sai cấu trúc hàng/cột.
- Không tự động hoá 100% — mục tiêu là giảm công sức, không phải loại bỏ hoàn toàn việc kiểm tra của con người.
