"""
Milestone 1: Chuyển PDF scan → ảnh PNG từng trang (DPI ~300) + deskew nhẹ.

Cách chạy:
    python src/pdf_to_images.py test-samples/test_ocr_page6.pdf
"""

import sys
import os
from pathlib import Path

import cv2
import numpy as np
import fitz  # PyMuPDF


def deskew(image: np.ndarray) -> np.ndarray:
    """
    Xoay ảnh nếu bị nghiêng nhẹ, dùng Hough Line Transform (dạng xác suất).
    Phù hợp với ảnh scan có bảng (nhiều đường kẻ ngang).
    Chỉ xoay nếu góc nghiêng > 0.3 độ, bỏ qua nếu gần thẳng.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Dùng adaptive threshold thay vì Canny — nhạy hơn với scan mờ
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, blockSize=21, C=5
    )

    # Phát hiện đoạn thẳng bằng HoughLinesP (probabilistic) — nhạy hơn HoughLines
    lines = cv2.HoughLinesP(
        binary, rho=1, theta=np.pi / 180,
        threshold=100, minLineLength=100, maxLineGap=20
    )

    if lines is None:
        # Thử lại với threshold thấp hơn
        _, binary2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        lines = cv2.HoughLinesP(
            binary2, rho=1, theta=np.pi / 180,
            threshold=80, minLineLength=80, maxLineGap=20
        )
        if lines is None:
            print("  Không tìm thấy đường thẳng nào (HoughLinesP)")
            return image

    # Tính góc của từng đoạn thẳng, chỉ lấy đoạn gần ngang (deviation < 20 độ)
    angles = []
    for line in lines:
        # OpenCV 5.x HoughLinesP trả về shape (N, 4) — mỗi dòng là [x1, y1, x2, y2]
        # OpenCV 4.x trả về shape (N, 1, 4) — mỗi dòng là [[x1, y1, x2, y2]]
        if line.ndim == 1:
            x1, y1, x2, y2 = line
        else:
            x1, y1, x2, y2 = line[0]
        # Tránh đoạn thẳng quá ngắn (đã lọc ở trên)
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) < 1:
            continue  # đường dọc, bỏ qua
        angle = np.degrees(np.arctan2(dy, dx))  # [-180, 180]
        # Đường gần ngang có |angle| < 20 hoặc |angle - 180| < 20 hoặc |angle + 180| < 20
        if abs(angle) < 20:
            angles.append(angle)
        elif abs(angle - 180) < 20:
            angles.append(angle - 180)
        elif abs(angle + 180) < 20:
            angles.append(angle + 180)

    if len(angles) == 0:
        print("  Không tìm thấy đường ngang nào")
        return image

    # Lấy góc trung vị (median) để tránh nhiễu
    angle = np.median(angles)

    print(f"  Số đường ngang tìm thấy: {len(angles)}, góc nghiêng: {angle:.2f} độ")

    # Chỉ xoay nếu góc đủ lớn (> 0.3 độ)
    if abs(angle) < 0.3:
        print("  → Góc quá nhỏ, bỏ qua deskew")
        return image

    # Xoay ảnh
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    cos = abs(rotation_matrix[0, 0])
    sin = abs(rotation_matrix[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))
    rotation_matrix[0, 2] += (new_w / 2) - center[0]
    rotation_matrix[1, 2] += (new_h / 2) - center[1]

    print(f"  → Đã xoay {angle:.2f} độ")
    rotated = cv2.warpAffine(
        image, rotation_matrix, (new_w, new_h),
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255)
    )
    return rotated


def pdf_to_images(pdf_path: str, output_dir: str = "debug_output", dpi: int = 300) -> list[str]:
    """
    Chuyển PDF scan thành danh sách ảnh PNG (mỗi trang 1 ảnh).
    Trả về danh sách đường dẫn các file ảnh đã tạo.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"LỖI: Không tìm thấy file PDF: {pdf_path}")
        sys.exit(1)

    # Tạo thư mục output: debug_output/<tên_file_pdf>/
    pdf_stem = pdf_path.stem  # tên file không có đuôi .pdf
    out_dir = Path(output_dir) / pdf_stem
    out_dir.mkdir(parents=True, exist_ok=True)

    # Mở PDF
    doc = fitz.open(str(pdf_path))
    scale = dpi / 72  # PyMuPDF mặc định 72 DPI
    matrix = fitz.Matrix(scale, scale)

    image_paths = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        # Render trang thành ảnh bitmap
        pix = page.get_pixmap(matrix=matrix)
        # Chuyển sang numpy array (RGB)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n
        )
        # Nếu là ảnh RGBA (4 kênh) thì chuyển về RGB
        if pix.n == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

        # Deskew
        img_deskewed = deskew(img)

        # Lưu ảnh
        out_path = out_dir / f"page_{page_num + 1:02d}.png"
        cv2.imwrite(str(out_path), cv2.cvtColor(img_deskewed, cv2.COLOR_RGB2BGR))
        image_paths.append(str(out_path))
        print(f"  Đã tạo: {out_path}")

    doc.close()
    return image_paths


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python src/pdf_to_images.py <đường_dẫn_file_pdf>")
        sys.exit(1)

    pdf_file = sys.argv[1]
    print(f"Đang xử lý: {pdf_file}")
    images = pdf_to_images(pdf_file)
    print(f"Hoàn tất! Tổng số trang: {len(images)}")