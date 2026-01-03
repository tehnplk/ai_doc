"""
API Test Script for AI Document Assignment System

ทดสอบ API endpoints:
- Health check
- Employee management (CRUD)
- Document ingestion
- Document assignment

Usage:
    uv run python test/test_api.py
"""

import requests
from pathlib import Path
import json

# Default base URL
BASE_URL = "http://localhost:8000"


class APITester:
    """API Test Client using requests library."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
    def _url(self, path: str) -> str:
        """Build full URL."""
        return f"{self.base_url}{path}"
    
    def _print_response(self, name: str, response: requests.Response):
        """Print formatted response."""
        status = "✅" if response.ok else "❌"
        print(f"\n{status} {name}")
        print(f"   Status: {response.status_code}")
        try:
            data = response.json()
            print(f"   Response: {json.dumps(data, ensure_ascii=False, indent=2)}")
        except:
            print(f"   Response: {response.text[:500]}")
    
    # === Health Check ===
    def test_health(self):
        """Test health endpoint."""
        response = self.session.get(self._url("/health"))
        self._print_response("GET /health", response)
        return response.ok
    
    def test_root(self):
        """Test root endpoint."""
        response = self.session.get(self._url("/"))
        self._print_response("GET /", response)
        return response.ok
    
    # === Employee Management ===
    def test_create_employee(self, employee_data: dict):
        """Test create employee endpoint."""
        response = self.session.post(
            self._url("/api/v1/employees"), 
            json=employee_data
        )
        self._print_response(f"POST /api/v1/employees ({employee_data['name']})", response)
        return response
    
    def test_list_employees(self):
        """Test list employees endpoint."""
        response = self.session.get(self._url("/api/v1/employees"))
        self._print_response("GET /api/v1/employees", response)
        return response
    
    # === Document Ingestion ===
    def test_ingest_document(self, file_path: str):
        """Test document ingestion with image file."""
        path = Path(file_path)
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        with open(path, "rb") as f:
            files = {"files": (path.name, f, "image/png")}
            # Don't use JSON content-type for multipart
            response = requests.post(
                self._url("/api/v1/ingest"), 
                files=files,
                timeout=60
            )
        
        self._print_response(f"POST /api/v1/ingest ({path.name})", response)
        return response
    
    def test_list_documents(self, skip: int = 0, limit: int = 10):
        """Test list documents endpoint."""
        response = self.session.get(
            self._url("/api/v1/ingest"), 
            params={"skip": skip, "limit": limit}
        )
        self._print_response("GET /api/v1/ingest", response)
        return response
    
    def test_get_document(self, doc_id: str):
        """Test get single document endpoint."""
        response = self.session.get(self._url(f"/api/v1/ingest/{doc_id}"))
        self._print_response(f"GET /api/v1/ingest/{doc_id}", response)
        return response
    
    # === Assignment ===
    def test_assign_document(self, doc_id: str, force_reassign: bool = False):
        """Test document assignment endpoint."""
        response = self.session.post(
            self._url(f"/api/v1/assign/{doc_id}"), 
            json={"force_reassign": force_reassign},
            timeout=120  # LLM calls may take time
        )
        self._print_response(f"POST /api/v1/assign/{doc_id}", response)
        return response
    
    def test_get_assignments(self, doc_id: str):
        """Test get assignments for document."""
        response = self.session.get(self._url(f"/api/v1/assignments/{doc_id}"))
        self._print_response(f"GET /api/v1/assignments/{doc_id}", response)
        return response
    
    # === Feedback ===
    def test_submit_feedback(self, doc_id: str, employee_id: str, reason: str = None):
        """Test submit feedback/override endpoint."""
        data = {
            "doc_id": doc_id,
            "correct_employee_id": employee_id,
            "reason": reason
        }
        response = self.session.post(self._url("/api/v1/feedback"), json=data)
        self._print_response("POST /api/v1/feedback", response)
        return response


# === Sample Data ===
SAMPLE_EMPLOYEES = [
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
        "responsibility_description": "รับผิดชอบงานบุคคล การจ้างงาน สวัสดิการ เอกสารพนักงาน ใบลา การฝึกอบรม"
    },
    {
        "employee_id": "EMP003",
        "name": "วิชัย เทคโนโลยี",
        "role": "ผู้จัดการฝ่ายไอที",
        "responsibility_description": "รับผิดชอบระบบคอมพิวเตอร์ ซอฟต์แวร์ เครือข่าย ความปลอดภัยข้อมูล การสนับสนุนทางเทคนิค"
    },
    {
        "employee_id": "EMP004",
        "name": "ณัฐชา ขายเก่ง",
        "role": "ผู้จัดการฝ่ายขาย",
        "responsibility_description": "รับผิดชอบงานขาย ใบเสนอราคา สัญญาซื้อขาย ลูกค้า ยอดขาย รายงานการขาย"
    },
]


def run_full_test():
    """Run complete API test suite."""
    print("=" * 60)
    print("🧪 AI Document Assignment System - API Test Suite")
    print("=" * 60)
    
    tester = APITester()
    
    # 1. Health checks
    print("\n" + "=" * 40)
    print("📋 1. Health Check Tests")
    print("=" * 40)
    tester.test_root()
    tester.test_health()
    
    # 2. Employee Management
    print("\n" + "=" * 40)
    print("👥 2. Employee Management Tests")
    print("=" * 40)
    
    # Create employees
    for emp in SAMPLE_EMPLOYEES:
        tester.test_create_employee(emp)
    
    # List employees
    tester.test_list_employees()
    
    # 3. Document Ingestion
    print("\n" + "=" * 40)
    print("📄 3. Document Ingestion Tests")
    print("=" * 40)
    
    # Check for test image
    test_image = Path(__file__).parent / "test_invoice.png"
    doc_id = None
    
    if test_image.exists():
        ingest_response = tester.test_ingest_document(str(test_image))
        if ingest_response and ingest_response.ok:
            doc_id = ingest_response.json().get("doc_id")
    else:
        print(f"⚠️  Test image not found: {test_image}")
        print("   Skipping ingestion test...")
    
    # List documents
    tester.test_list_documents()
    
    # 4. Assignment (if we have a document)
    if doc_id:
        print("\n" + "=" * 40)
        print("🎯 4. Document Assignment Tests")
        print("=" * 40)
        
        # Get document detail
        tester.test_get_document(doc_id)
        
        # Assign document
        tester.test_assign_document(doc_id)
        
        # Get assignment history
        tester.test_get_assignments(doc_id)
        
        # 5. Feedback test
        print("\n" + "=" * 40)
        print("💬 5. Feedback Tests")
        print("=" * 40)
        
        tester.test_submit_feedback(
            doc_id=doc_id,
            employee_id="EMP002",
            reason="Manual reassignment test"
        )
        
        # Check updated assignments
        tester.test_get_assignments(doc_id)
    else:
        print("\n⚠️  Skipping assignment tests (no document available)")
    
    print("\n" + "=" * 60)
    print("✅ Test Suite Completed!")
    print("=" * 60)


def run_quick_test():
    """Run quick health check test only."""
    print("🧪 Quick Health Check...")
    tester = APITester()
    success = tester.test_health() and tester.test_root()
    if success:
        print("\n✅ Server is running!")
    else:
        print("\n❌ Server is not responding properly")
    return success


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        run_quick_test()
    else:
        run_full_test()
