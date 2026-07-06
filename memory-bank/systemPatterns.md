# System Patterns

## Kiến trúc tổng quan — ĐÃ CHỐT (chi tiết đầy đủ xem PLAN.md)
```
PDF scan (input)
   │
   ▼
[1] Chuyển PDF → ảnh từng trang (PyMuPDF) + deskew nhẹ nếu cần
   │
   ▼
[2] Gửi ảnh từng trang cho Gemini API (vision) → JSON có cấu trúc
    (paragraph / section_header / table với rowspan-colspan)
   │
   ▼
[3] Ghi JSON 1 trang → Excel (merge cell, format số) — module riêng, test độc lập
   │
   ▼
[4] Module "ghép nối" nhiều trang: bỏ header lặp, nối dòng bị cắt ngang trang,
    tách section_header ra khỏi bảng dữ liệu
   │
   ▼
[5] (ĐÃ BỎ) Không cần validate công thức — chỉ giữ nguyên số liệu đã scan đúng
   │
   ▼
[6] main.py ghép toàn bộ: 1 PDF → 1 Excel cùng tên
```

Lưu ý: KHÔNG dùng OCR cổ điển (Tesseract/PaddleOCR) — xem lý do trong techContext.md.

## Nguyên tắc thiết kế
- Mỗi bước [1]-[6] nên tách thành 1 hàm/module riêng, có thể test độc lập — để khi bước nào sai, sửa riêng bước đó mà không ảnh hưởng các bước khác.
- Luôn lưu lại kết quả trung gian (ảnh đã xử lý, text OCR thô) ra file tạm để dễ debug khi kết quả cuối sai.
- Không cố "làm cho đúng tất cả trong 1 lần" — build từng bước, test bằng file mẫu thật sau mỗi bước.

## Các quyết định kỹ thuật quan trọng
(Cập nhật dần khi có quyết định mới trong quá trình code, kèm lý do)

- (ví dụ) Chọn PyMuPDF thay vì pdf2image vì không cần cài Poppler riêng trên Windows.

## Pattern xử lý lỗi
- Nếu OCR không nhận diện được bảng nào trong trang → log rõ ràng trang nào lỗi, không dừng toàn bộ chương trình khi xử lý nhiều file.
