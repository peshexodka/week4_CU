#!/usr/bin/env python3
"""Convert the source xlsx to privacy-safe JSON without external packages."""
from pathlib import Path
from datetime import date, timedelta
import json
import re
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = next(ROOT.glob("*.xlsx"))
OUTPUT = ROOT / "src" / "data" / "purchases.json"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def value(cell):
    if cell.attrib.get("t") == "inlineStr":
        return "".join(cell.itertext())
    node = cell.find("m:v", NS)
    return node.text if node is not None else None


def excel_date(serial):
    return (date(1899, 12, 30) + timedelta(days=float(serial))).isoformat()


with zipfile.ZipFile(SOURCE) as archive:
    root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))

rows = []
for xml_row in root.findall(".//m:row", NS):
    cells = [None] * 13
    for cell in xml_row.findall("m:c", NS):
        letters = re.match(r"[A-Z]+", cell.attrib["r"]).group()
        index = 0
        for letter in letters:
            index = index * 26 + ord(letter) - 64
        cells[index - 1] = value(cell)
    rows.append(cells)

order_ids = {}
public_rows = []
for row in rows[1:]:
    if row[2] != "доставлен":
        continue
    if row[0] not in order_ids:
        order_ids[row[0]] = f"O{len(order_ids) + 1:04d}"
    public_rows.append({
        "o": order_ids[row[0]],
        "d": excel_date(row[1]),
        "n": row[6],
        "c": row[7],
        "b": float(row[8]),
        "p": float(row[9]),
        "x": float(row[10]),
        "q": int(float(row[11])),
        "s": float(row[12]),
    })

goods = [row for row in public_rows if row["c"] != "Услуги Лавки"]
checks = {
    "orders": len({row["o"] for row in public_rows}),
    "spend": sum(row["s"] for row in public_rows),
    "goodsSpend": sum(row["s"] for row in goods),
    "goodsQuantity": sum(row["q"] for row in goods),
    "savings": sum(row["x"] * row["q"] for row in goods),
}
expected = {"orders": 944, "spend": 1278791, "goodsSpend": 1236462, "goodsQuantity": 5244, "savings": 25543}
if checks != expected:
    raise RuntimeError(f"Control totals differ: {checks} != {expected}")

payload = {
    "meta": {
        "through": "2026-08-29",
        "sourceRows": len(rows) - 1,
        "deliveredRows": len(public_rows),
        "checks": checks,
        "privacy": "Адреса и точное время удалены; номера заказов заменены локальными идентификаторами.",
    },
    "rows": public_rows,
}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"Wrote {len(public_rows)} rows to {OUTPUT.relative_to(ROOT)}")
print(checks)
