# OCR Table Extractor — Công cụ chuyển bảng PDF scan thành Excel

## Giới thiệu

Công cụ này giúp bạn chuyển các **file PDF dạng scan** (ảnh chụp/scan giấy tờ) có chứa **bảng số liệu tiếng Việt (Chưa test file tiếng anh, nhưng khả năng cao vẫn sẽ thành công)** thành file **Excel (.xlsx)**.

> ⚠️ **Độ chính xác:** Tool đạt khoảng **90%** — bạn vẫn cần kiểm tra lại kết quả và sửa tay những chỗ sai. Mục tiêu là **giảm công sức**, không phải loại bỏ hoàn toàn việc kiểm tra.

---

## Yêu cầu trước khi cài đặt

- Máy tính Windows (đã test trên Windows 11)
- **Python 3.10 trở lên** (nếu chưa có, tải tại [python.org](https://www.python.org/downloads/) — nhớ tick **"Add Python to PATH"** khi cài)
- **Kết nối Internet** (vì tool dùng Google Gemini API)
- **Tài khoản Google** (để lấy API key miễn phí)

---

## Cài đặt

### Bước 1: Tải code về máy

Vào trang: <https://github.com/truongtung8197-lang/OCR_PDF_EXCEL>

Nhấn nút xanh "Code" → chọn "Download ZIP" → giải nén ra thư mục nào đó trên máy (ví dụ: D:\Working\OCR_PDF_EXCEL).

Nếu bạn biết Git thì có thể clone:

```
git clone https://github.com/truongtung8197-lang/OCR_PDF_EXCEL.git
```

### Bước 2: Mở Terminal / Command Prompt

Nhấn Windows + R, gõ cmd, nhấn Enter. Sau đó gõ:

```
cd D:\Working\OCR_PDF_EXCEL
```

⚠️ Thay D:\Working\OCR_PDF_EXCEL bằng đường dẫn thật đến thư mục bạn vừa giải nén ở Bước 1.

Cách tìm đường dẫn nhanh: Mở thư mục vừa giải nén bằng File Explorer
→ nhấn vào thanh địa chỉ trên cùng
→ copy đường dẫn hiện ra →
 paste vào sau lệnh cd .

### Bước 3: Tạo môi trường ảo (khuyên dùng)

```cmd
python -m venv venv
venv\Scripts\activate
```

Sau khi chạy, bạn sẽ thấy chữ `(venv)` xuất hiện ở đầu dòng lệnh.

### Bước 4: Cài thư viện

```cmd
pip install -r requirements.txt
```

### Bước 5: Lấy API key Gemini và tạo file `.env`

1. Vào trang: <https://aistudio.google.com/apikey>
2. Đăng nhập bằng tài khoản Google của bạn.
3. Nhấn **"Create API Key"** → chọn project (hoặc tạo mới) → copy key.
4. Trong thư mục dự án đã có sẵn file **`.env.example`** — hãy **copy** hoặc **đổi tên** nó thành `.env` (bỏ đuôi `.example`).
5. Mở file `.env` bằng Notepad và thay `thay_bang_api_key_cua_ban` bằng API key bạn vừa copy:

```ini
GEMINI_API_KEY=AIz... (key thật của bạn)
```

> 🔒 File `.env` chứa key riêng của bạn, **không chia sẻ file này cho người khác**. File `.env` đã được liệt kê trong `.gitignore` nên sẽ không bị đẩy lên GitHub.

---

## Cách chạy

### Chạy nhanh (1 lệnh)

Mở Terminal (đã kích hoạt môi trường ảo `venv`), gõ:

```cmd
python src/main.py "đường_dẫn_file_pdf"
```

**Ví dụ với file mẫu có sẵn trong dự án:**

```cmd
python src/main.py "test-samples/PAGE 10+11+12.pdf"
```

hoặc bạn copy file PDF của mình vào thư mục `input/` rồi chạy:

```cmd
python src/main.py "input/ORIGINAL.pdf"
```

### Kết quả

- Tool sẽ tạo thư mục `output/` và lưu file Excel cùng tên với file PDF.
- Ví dụ: `PAGE 10+11+12.pdf` → `output/PAGE 10+11+12.xlsx`
- File tạm (ảnh trung gian, JSON thô) được lưu trong `debug_output/` — bạn có thể xoá thư mục này nếu không cần.

### Chạy lại lần 2 (nhanh hơn)

Khi chạy lại lần 2, tool sẽ tự động **bỏ qua các bước đã làm**:

- **Bước 1:** Nếu đã có ảnh trong `debug_output/<tên_pdf>/` → bỏ qua, không render PDF lại.
- **Bước 2:** Nếu đã có JSON tương ứng → bỏ qua, không gọi Gemini API.
- Chỉ chạy **ghép nối** và **xuất Excel** — rất nhanh.

Điều này đặc biệt hữu ích khi bạn chỉ muốn sửa lại 1 vài file JSON (sửa tay) và chạy lại.

### Xem tiến trình

Khi chạy, tool sẽ in ra các bước:

```
============================================================
Đang xử lý: ORIGINAL.pdf
Định dạng số: dấu '.' = phân cách nghìn, dấu ',' = phân cách thập phân
============================================================

[Bước 1/4] Chuyển PDF → ảnh...
  ⏭ Bỏ qua: đã có 38 ảnh trong debug_output\ORIGINAL

[Bước 2/4] Gọi Gemini API trích xuất JSON...
  ⏭ Bỏ qua: page_01.png — đã có JSON
  ⏭ Bỏ qua: page_02.png — đã có JSON
  ... (38 trang)
  ✓ Đã tạo 38 file JSON

[Bước 3/4] Ghép nối các trang...
  ✓ Đã ghép 38 trang → 81 elements

[Bước 4/4] Xuất Excel...
  ✓ Đã lưu Excel: output\ORIGINAL.xlsx

============================================================
✓ HOÀN TẤT!
  File Excel: output\ORIGINAL.xlsx
============================================================
```

---

## Giới hạn Gemini API

Tool sử dụng **Google Gemini API bản free** (model `gemini-3.1-flash-lite-preview`).

- **Giới hạn:** Khoảng **10-15 request/phút** và **1.500 request/ngày** (tuỳ theo chính sách của Google).
- Với file PDF 38 trang, bạn chỉ cần gửi 38 request — hoàn toàn trong giới hạn.
- Nếu gặp lỗi `429 Resource exhausted`, hãy **đợi 1-2 phút** rồi chạy lại — tool có cơ chế retry tự động.

> Vì dùng API qua Internet nên tốc độ còn phụ thuộc vào đường truyền của bạn.

---

## Cấu hình định dạng số

File `config.json` trong thư mục dự án cho phép bạn chỉnh cách đọc số Việt Nam:

```json
{
  "decimal_separator": ",",
  "thousand_separator": "."
}
```

- **Mặc định (Việt Nam):** Dấu `,` là thập phân, dấu `.` là phân cách nghìn.
  - Ví dụ: `1.234,56` → số `1234.56`
- **Nếu file PDF của bạn dùng định dạng khác** (ví dụ: dấu `.` là thập phân kiểu Mỹ), bạn sửa 2 dòng này cho phù hợp.

> Tool chỉ parse số cho các cột: **Khối lượng, Đơn giá chi tiết, Đơn giá thành phần, Đơn giá Module**. Các cột khác (STT, Mã, Hàng hóa, Đơn vị) giữ nguyên dạng text.

---

## Cấu trúc thư mục

```
OCR_PDF_EXCEL/
├── .env                  # Chứa API key (tạo từ .env.example, không lên git)
├── .env.example          # Mẫu file .env (có trên git)
├── .gitignore
├── config.json           # Cấu hình định dạng số
├── requirements.txt      # Danh sách thư viện cần cài
├── README.md             # File hướng dẫn này
├── src/                  # Mã nguồn
│   ├── main.py           # Chạy pipeline chính
│   ├── pdf_to_images.py  # Chuyển PDF → ảnh (có deskek tự động)
│   ├── gemini_extractor.py  # Gọi Gemini API → JSON
│   ├── stitcher.py       # Ghép nối nhiều trang (nối chồng)
│   ├── excel_writer.py   # Xuất Excel (merge cell, format số)
│   └── validator.py      # (Không dùng)
├── input/                # Đặt file PDF vào đây (chỉ có .gitkeep trên git)
├── debug_output/         # Ảnh & JSON tạm (tự động tạo khi chạy, không lên git)
└── output/               # File Excel kết quả (tự động tạo, không lên git)
```

---

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Cách xử lý |
|-----|-------------|------------|
| `Không tìm thấy GEMINI_API_KEY` | Chưa tạo file `.env` hoặc sai key | Copy `.env.example` → `.env` và điền API key đúng |
| `429 Resource exhausted` | Vượt quá giới hạn request/phút | Đợi 1-2 phút rồi chạy lại |
| `Không tìm thấy file PDF` | Sai đường dẫn | Kiểm tra lại đường dẫn file PDF trong lệnh chạy |
| `Permission denied: output\...xlsx` | File Excel đang mở trong Excel | Đóng file Excel lại, chạy lại |
| File Excel ra nhưng thiếu/ sai dữ liệu | Gemini đọc sai bảng (~10% lỗi) | Sửa tay trong Excel, hoặc sửa file JSON trong `debug_output/` rồi chạy lại |

---

## Ghi chú

- Tool cần Internet để gọi Gemini API.
- File PDF càng rõ nét, kết quả càng chính xác.
- Nếu bảng bị nghiêng hoặc mờ, tool có deskew tự động (xoay ảnh cho thẳng).
- Mỗi lần chạy, tool ghi đè file Excel cũ trong thư mục `output/`.
- File Excel tốt nhất nên đóng trước khi chạy lại để tránh lỗi Permission denied.
