"""
Test: สร้าง Employee, Ingest ใบสั่งซื้อ, และ Auto Assign

สคริปต์นี้ทดสอบ:
1. สร้าง Employee 4 คน (บัญชี, บุคคล, ไอที, จัดซื้อ)
2. อัพโหลดเอกสารใบสั่งซื้อ
3. ทดสอบ auto-assign ว่าเอกสารจะถูกมอบหมายให้ใคร
"""

import requests
from pathlib import Path
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title: str):
    print("\n" + "=" * 60)
    print(f"🔹 {title}")
    print("=" * 60)

def print_response(name: str, response: requests.Response):
    status = "✅" if response.ok else "❌"
    print(f"\n{status} {name}")
    print(f"   Status: {response.status_code}")
    try:
        data = response.json()
        print(f"   Response: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except:
        print(f"   Response: {response.text[:500]}")
    return response

# === ขั้นตอนที่ 1: สร้าง Employee ===
print_section("ขั้นตอนที่ 1: สร้าง Employee")

employees = [
    {
        "employee_id": "EMP001",
        "name": "สมชาย ใจดี",
        "role": "ผู้จัดการฝ่ายบัญชี",
        "responsibility_description": "รับผิดชอบงานบัญชี การเงิน ใบแจ้งหนี้ ใบเสร็จรับเงิน งบประมาณ รายงานทางการเงิน บัญชีเจ้าหนี้ บัญชีลูกหนี้"
    },
    {
        "employee_id": "EMP002", 
        "name": "สมหญิง รักษาสัตย์",
        "role": "ผู้จัดการฝ่ายบุคคล",
        "responsibility_description": "รับผิดชอบงานบุคคล การจ้างงาน สวัสดิการ เอกสารพนักงาน ใบลา การฝึกอบรม ประเมินผลงาน"
    },
    {
        "employee_id": "EMP003",
        "name": "วิชัย เทคโนโลยี",
        "role": "ผู้จัดการฝ่ายไอที",
        "responsibility_description": "รับผิดชอบระบบคอมพิวเตอร์ ซอฟต์แวร์ เครือข่าย ความปลอดภัยข้อมูล การสนับสนุนทางเทคนิค อุปกรณ์คอมพิวเตอร์"
    },
    {
        "employee_id": "EMP004",
        "name": "ณัฐชา จัดซื้อดี",
        "role": "ผู้จัดการฝ่ายจัดซื้อ",
        "responsibility_description": "รับผิดชอบงานจัดซื้อ ใบสั่งซื้อ Purchase Order ใบเสนอราคา สัญญาซื้อขาย ซัพพลายเออร์ การเปรียบเทียบราคา การต่อรองราคา"
    },
]

for emp in employees:
    response = requests.post(
        f"{BASE_URL}/api/v1/employees",
        json=emp,
        headers={"Content-Type": "application/json"}
    )
    print_response(f"สร้าง Employee: {emp['name']}", response)

# ดูรายชื่อ Employee ทั้งหมด
response = requests.get(f"{BASE_URL}/api/v1/employees")
print_response("รายชื่อ Employee ทั้งหมด", response)

# === ขั้นตอนที่ 2: อัพโหลดเอกสารใบสั่งซื้อ ===
print_section("ขั้นตอนที่ 2: อัพโหลดเอกสารใบสั่งซื้อ")

# หาไฟล์ใบสั่งซื้อ
po_file = Path(__file__).parent / "purchase_order.png"
if not po_file.exists():
    # ลองหา test_invoice.png
    po_file = Path(__file__).parent / "test_invoice.png"

if not po_file.exists():
    print("❌ ไม่พบไฟล์รูปภาพสำหรับทดสอบ")
    print(f"   กรุณาวางไฟล์รูปใบสั่งซื้อที่: {Path(__file__).parent}")
    exit(1)

print(f"📄 กำลังอัพโหลด: {po_file.name}")

with open(po_file, "rb") as f:
    files = {"files": (po_file.name, f, "image/png")}
    response = requests.post(
        f"{BASE_URL}/api/v1/ingest",
        files=files,
        timeout=120  # OCR อาจใช้เวลาสักครู่
    )

ingest_result = print_response("อัพโหลดเอกสาร", response)

if not response.ok:
    print("❌ ไม่สามารถอัพโหลดเอกสารได้")
    exit(1)

doc_id = response.json().get("doc_id")
print(f"\n📌 Document ID: {doc_id}")

# รอสักครู่ให้ระบบ process เสร็จ
print("\n⏳ รอระบบ process เอกสาร...")
time.sleep(2)

# ดูสถานะเอกสาร
response = requests.get(f"{BASE_URL}/api/v1/ingest/{doc_id}")
print_response("สถานะเอกสาร", response)

# === ขั้นตอนที่ 3: Auto-Assign เอกสาร ===
print_section("ขั้นตอนที่ 3: Auto-Assign เอกสาร")

print("🤖 กำลังให้ AI วิเคราะห์และมอบหมายเอกสาร...")
print("   (อาจใช้เวลาสักครู่ เนื่องจากใช้ LLM reasoning)")

response = requests.post(
    f"{BASE_URL}/api/v1/assign/{doc_id}",
    json={"force_reassign": False},
    headers={"Content-Type": "application/json"},
    timeout=180  # LLM อาจใช้เวลานาน
)

assign_result = print_response("ผลการมอบหมายเอกสาร", response)

if response.ok:
    data = response.json()
    print("\n" + "=" * 60)
    print("🎯 สรุปผลการมอบหมาย")
    print("=" * 60)
    print(f"   📄 เอกสาร: {doc_id}")
    print(f"   👤 มอบหมายให้: {data.get('employee_name')} ({data.get('employee_id')})")
    print(f"   📊 ความมั่นใจ: {data.get('confidence', 0) * 100:.1f}%")
    print(f"   💬 เหตุผล: {data.get('reason')}")

# ดูประวัติการมอบหมาย
response = requests.get(f"{BASE_URL}/api/v1/assignments/{doc_id}")
print_response("ประวัติการมอบหมาย", response)

print("\n" + "=" * 60)
print("✅ การทดสอบเสร็จสิ้น!")
print("=" * 60)
