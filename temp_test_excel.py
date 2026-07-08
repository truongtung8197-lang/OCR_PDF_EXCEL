import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from src.excel_writer import json_to_excel

# Đọc file stitched
with open("debug_output/stitched/ORIGINAL_stitched.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Xuất Excel
output_path = "output/ORIGINAL.xlsx"
Path("output").mkdir(exist_ok=True)
json_to_excel(data, output_path)
print(f"Hoàn tất! File: {output_path}")
