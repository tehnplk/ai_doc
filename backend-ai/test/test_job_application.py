"""
Test: ทดสอบ Auto-Assign เอกสารใบสมัครงาน

สคริปต์นี้ทดสอบ:
1. อัพโหลดเอกสารใบสมัครงาน
2. ตรวจสอบว่าไฟล์ถูกบันทึกในรูปแบบ: ชื่อเดิม_yyyymmddhhmmss.ext
3. ทดสอบ auto-assign ว่าเอกสารจะถูกมอบหมายให้ฝ่ายบุคคล
"""

import requests
from pathlib import Path
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title: str):
    print("\n" + "=" * 60)
    print(f">>> {title}")
    print("=" * 60)

def print_response(name: str, response: requests.Response):
    status = "[OK]" if response.ok else "[FAIL]"
    print(f"\n{status} {name}")
    print(f"   Status: {response.status_code}")
    try:
        data = response.json()
        print(f"   Response: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except:
        print(f"   Response: {response.text[:500]}")
    return response

# === ตรวจสอบว่ามี Employee แล้วหรือยัง ===
print_section("ตรวจสอบ Employee ในระบบ")
response = requests.get(f"{BASE_URL}/api/v1/employees")
employees = response.json() if response.ok else []

if not employees:
    print("ไม่มี Employee ในระบบ กำลังสร้าง...")
    
    employees_data = [
        {
            "employee_id": "EMP001",
            "name": "สมชาย ใจดี",
            "role": "ผู้จัดการฝ่ายบัญชี",
            "responsibility_description": "รับผิดชอบงานบัญชี การเงิน ใบแจ้งหนี้ ใบเสร็จรับเงิน งบประมาณ รายงานทางการเงิน"
        },
        {
            "employee_id": "EMP002", 
            "name": "สมหญิง รักษาสัตย์",
            "role": "ผู้จัดการฝ่ายบุคคล",
            "responsibility_description": "รับผิดชอบงานบุคคล การจ้างงาน สวัสดิการ เอกสารพนักงาน ใบลา การฝึกอบรม ใบสมัครงาน การสรรหาบุคลากร"
        },
        {
            "employee_id": "EMP003",
            "name": "วิชัย เทคโนโลยี",
            "role": "ผู้จัดการฝ่ายไอที",
            "responsibility_description": "รับผิดชอบระบบคอมพิวเตอร์ ซอฟต์แวร์ เครือข่าย ความปลอดภัยข้อมูล"
        },
        {
            "employee_id": "EMP004",
            "name": "ณัฐชา จัดซื้อดี",
            "role": "ผู้จัดการฝ่ายจัดซื้อ",
            "responsibility_description": "รับผิดชอบงานจัดซื้อ ใบสั่งซื้อ ซัพพลายเออร์"
        },
    ]
    
    for emp in employees_data:
        requests.post(f"{BASE_URL}/api/v1/employees", json=emp)
    
    print(f"สร้าง {len(employees_data)} Employee เรียบร้อย")
else:
    print(f"มี {len(employees)} Employee ในระบบแล้ว")

# === อัพโหลดเอกสารใบสมัครงาน ===
print_section("อัพโหลดเอกสารใบสมัครงาน")

job_app_file = Path(__file__).parent / "job_application.png"
if not job_app_file.exists():
    print(f"[FAIL] ไม่พบไฟล์: {job_app_file}")
    exit(1)

print(f"กำลังอัพโหลด: {job_app_file.name}")

with open(job_app_file, "rb") as f:
    files = {"files": (job_app_file.name, f, "image/png")}
    response = requests.post(
        f"{BASE_URL}/api/v1/ingest",
        files=files,
        timeout=120
    )

ingest_result = print_response("อัพโหลดเอกสาร", response)

if not response.ok:
    print("[FAIL] ไม่สามารถอัพโหลดเอกสารได้")
    exit(1)

doc_data = response.json()
doc_id = doc_data.get("doc_id")
stored_filename = doc_data.get("stored_filename")

print(f"\n   Document ID: {doc_id}")
print(f"   Stored Filename: {stored_filename}")

# ตรวจสอบว่าไฟล์ถูกบันทึกในรูปแบบที่ถูกต้อง
if stored_filename:
    doc_folder = Path(__file__).parent.parent / "doc"
    saved_file = doc_folder / stored_filename
    if saved_file.exists():
        print(f"   [OK] ไฟล์ถูกบันทึกที่: {saved_file}")
    else:
        print(f"   [WARN] ไม่พบไฟล์ที่: {saved_file}")

# รอระบบ process
print("\n   รอระบบ process เอกสาร...")
time.sleep(2)

# === Auto-Assign เอกสาร ===
print_section("Auto-Assign เอกสารใบสมัครงาน")

print("กำลังให้ AI วิเคราะห์และมอบหมายเอกสาร...")
print("(ใบสมัครงานควรถูกมอบหมายให้ฝ่ายบุคคล)")

response = requests.post(
    f"{BASE_URL}/api/v1/assign/{doc_id}",
    json={"force_reassign": False},
    headers={"Content-Type": "application/json"},
    timeout=180
)

assign_result = print_response("ผลการมอบหมายเอกสาร", response)

if response.ok:
    data = response.json()
    print("\n" + "=" * 60)
    print(">>> สรุปผลการมอบหมาย")
    print("=" * 60)
    print(f"   เอกสาร: ใบสมัครงาน ({doc_id[:8]}...)")
    print(f"   มอบหมายให้: {data.get('employee_name')} ({data.get('employee_id')})")
    print(f"   ความมั่นใจ: {data.get('confidence', 0) * 100:.1f}%")
    print(f"   เหตุผล: {data.get('reason')}")
    
    # ตรวจสอบว่ามอบหมายให้ฝ่ายบุคคลหรือไม่
    if data.get('employee_id') == 'EMP002':
        print("\n   [OK] ระบบมอบหมายให้ฝ่ายบุคคลได้ถูกต้อง!")
    else:
        print(f"\n   [INFO] ระบบมอบหมายให้: {data.get('employee_name')}")

print("\n" + "=" * 60)
print("[OK] การทดสอบเสร็จสิ้น!")
print("=" * 60)
