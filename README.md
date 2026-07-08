# OCR Table Extractor — Công cụ chuyển bảng PDF scan thành Excel

## Giới thiệu

Công cụ này giúp bạn chuyển các **file PDF dạng scan** (ảnh chụp/scan giấy tờ) có chứa **bảng số liệu tiếng Việt** thành file **Excel (.xlsx)**.

**Ví dụ:** Bạn có 1 file PDF scan bảng báo giá 38 trang, thay vì ngồi gõ lại từng số vào Excel, tool này sẽ tự động đọc bảng và xuất ra file Excel chỉ trong vài phút.

> ⚠️ **Lưu ý:** Tool không đúng 100%. Bạn vẫn cần kiểm tra lại kết quả và sửa tay những chỗ sai. Mục tiêu là **giảm công sức**, không phải loại bỏ hoàn toàn việc kiểm tra.

---

## Yêu cầu trước khi cài đặt

- Máy tính Windows (đã test trên Windows 11)
- **Python 3.10 trở lên** (nếu chưa có, tải tại [python.org](https://www.python.org/downloads/) — nhớ tick **"Add Python to PATH"** khi cài)
- **Kết nối Internet** (vì tool dùng Google Gemini API)
- **Tài khoản Google** (để lấy API key miễn phí)

---

## Cài đặt

### Bước 1: Tải code về máy

Tải toàn bộ thư mục dự án này về máy (hoặc clone từ GitHub nếu bạn biết Git).

### Bước 2: Mở Terminal / Command Prompt

- Nhấn `Windows + R`, gõ `cmd`, nhấn Enter.
- Gõ lệnh sau để vào thư mục dự án (thay đường dẫn đúng với máy bạn):

```cmd
cd d:\Working\OCR_PDF_EXCEL
```

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

### Bước 5: Lấy API key Gemini (miễn phí)

1. Vào trang: https://aistudio.google.com/apikey
2. Đăng nhập bằng tài khoản Google của bạn.
3. Nhấn **"Create API Key"** → chọn project (hoặc tạo mới) → copy key.
4. Trong thư mục dự án, tạo file tên là `.env` (dùng Notepad hoặc bất kỳ editor nào).
5. Gõ vào file `.env` nội dung sau (thay `API_KEY_CUA_BAN` bằng key bạn vừa copy):

```
GEMINI_API_KEY=API_KEY_CUA_BAN
```

6. Lưu file lại.

> 🔒 File `.env` chứa key riêng của bạn, **không chia sẻ file này cho người khác**.

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

hoặc với file bạn tự có:

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
├── .env                  # Chứa API key (tự tạo, không commit lên git)
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
├── input/                # Đặt file PDF vào đây
├── debug_output/         # Ảnh & JSON tạm (tự động tạo khi chạy)
└── output/               # File Excel kết quả (tự động tạo khi chạy)
```

---

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Cách xử lý |
|-----|-------------|------------|
| `Không tìm thấy GEMINI_API_KEY` | Chưa tạo file `.env` hoặc sai key | Làm lại Bước 5 ở phần Cài đặt |
| `429 Resource exhausted` | Vượt quá giới hạn request/phút | Đợi 1-2 phút rồi chạy lại |
| `Không tìm thấy file PDF` | Sai đường dẫn | Kiểm tra lại đường dẫn file PDF |
| `Permission denied: output\...xlsx` | File Excel đang mở trong Excel | Đóng file Excel lại, chạy lại |
| File Excel ra nhưng thiếu/ sai dữ liệu | Gemini đọc sai bảng | Sửa tay trong Excel, hoặc sửa file JSON trong `debug_output/` rồi chạy lại (sẽ skip Gemini) |

---

## Mẹo sửa lỗi JSON thủ công

Nếu kết quả Excel ra chưa đúng, bạn có thể:

1. Mở file JSON trong `debug_output/<tên_pdf>/` (dùng Notepad hoặc VS Code)
2. Sửa trực tiếp các giá trị sai trong JSON
3. Chạy lại lệnh — tool sẽ **bỏ qua Bước 1+2** (vì đã có ảnh và JSON), chỉ chạy ghép nối + xuất Excel
4. Xem kết quả mới

---

## Ghi chú

- Tool cần Internet để gọi Gemini API.
- File PDF càng rõ nét, kết quả càng chính xác.
- Nếu bảng bị nghiêng hoặc mờ, tool có deskew tự động (xoay ảnh cho thẳng).
- Mỗi lần chạy, tool ghi đè file Excel cũ trong thư mục `output/`.
- File Excel tốt nhất nên đóng trước khi chạy lại để tránh lỗi Permission denied.