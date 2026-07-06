# Tech Context

## Môi trường
- Hệ điều hành: (điền: Windows / macOS / Linux)
- Editor/Agent: VS Code + Cline
- AI Agent model: DeepSeek (qua API key riêng, hoặc DeepSeek local nếu có)
- Ngôn ngữ lập trình: Python (khuyến nghị — nhiều thư viện OCR/Excel hỗ trợ tốt nhất)

## Lựa chọn OCR engine — ĐÃ CHỐT

**Quyết định: Gemini API (model Flash, vision) — free tier.**

Lý do chọn (xem chi tiết trong PLAN.md mục 1):
- Miễn phí, đã có sẵn API key.
- Xử lý tốt ô merge phức tạp và dấu tiếng Việt nhờ hiểu ngữ nghĩa, không chỉ nhận diện ký tự như OCR cổ điển.
- Code tích hợp đơn giản hơn nhiều so với Tesseract/PaddleOCR + tự viết table-detection.

Đánh đổi chấp nhận: cần internet, Google có thể dùng dữ liệu free tier để cải thiện model (dữ liệu người dùng xác nhận không nhạy cảm), giới hạn ~10-15 request/phút — không ảnh hưởng vì dùng theo tuần, khối lượng nhỏ.

Đã loại: Tesseract, PaddleOCR (không cần vì đã có giải pháp free tốt hơn cho use case này), Azure/Google Document AI trả phí (không cần vì free tier Gemini đủ dùng).

## Thư viện dự kiến (Python)
- Xử lý PDF → ảnh: `PyMuPDF (fitz)`
- Gọi Gemini API: `google-genai` (SDK chính thức)
- Ghi Excel: `openpyxl`
- Tiền xử lý ảnh (deskew nhẹ nếu cần): `opencv-python`
- Quản lý API key: `python-dotenv` (không hardcode key trong code)

## Ràng buộc
- Máy cá nhân, không có GPU mạnh → ưu tiên giải pháp không cần train model.
- Người dùng không rành code → mọi script cần có hướng dẫn chạy rõ ràng (README riêng), tránh lệnh phức tạp.

## Cách chạy dự án (cập nhật khi có)
```
(điền lệnh cụ thể, ví dụ: python main.py --input file.pdf --output ket_qua.xlsx)
```
