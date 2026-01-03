# System Specification
## ระบบจำแนกและมอบหมายเอกสารอัตโนมัติด้วย AI (AI-based Document Assignment System)

---

## 1. วัตถุประสงค์ของระบบ (Objectives)
1. จำแนกเอกสาร PDF ตามความรับผิดชอบของพนักงานโดยอัตโนมัติ
2. ลดภาระงาน manual routing และความผิดพลาดจากมนุษย์
3. รองรับเอกสารหลายประเภท หลายบริบท และภาษาไทย
4. มีเหตุผลการตัดสินใจ (Explainable & Auditable)
5. เรียนรู้และปรับปรุงความแม่นยำจาก feedback การใช้งานจริง

---

## 2. ขอบเขตระบบ (System Scope)
### 2.1 In-Scope
- เอกสาร PDF (text-based และ scan)
- การจำแนกเอกสารตามความรับผิดชอบพนักงาน/ตำแหน่ง
- การใช้ Embedding + LLM Reasoning
- การบันทึกผลการตัดสินใจและเหตุผล

### 2.2 Out-of-Scope
- การอนุมัติเอกสารเชิงกฎหมาย
- การแก้ไขเนื้อหาเอกสาร
- การจัดการ workflow หลังการอนุมัติ

---

## 3. ผู้ใช้งานระบบ (User Roles)
1. **Document Uploader** – อัปโหลดเอกสาร
2. **Employee / Officer** – รับผิดชอบเอกสาร
3. **Administrator** – จัดการโปรไฟล์, rule, audit
4. **System** – AI Decision Engine

---

## 4. Functional Requirements

### 4.1 Document Ingestion
- รองรับ PDF สูงสุด 50 MB ต่อไฟล์
- รองรับทั้ง text PDF และ scanned PDF
- Extract text พร้อม metadata (หน้า, ย่อหน้า)

### 4.2 Text Processing
- Chunk เอกสาร 300–500 tokens ต่อ chunk
- รองรับภาษาไทยและอังกฤษ

### 4.3 Semantic Embedding
- แปลง chunk และ employee profile เป็น vector
- ใช้ embedding model เดียวกันทั้งระบบ

### 4.4 Candidate Selection (Semantic Search)
- ค้นหา Top-K (3–5) พนักงานที่เกี่ยวข้อง
- ใช้ cosine similarity
- มี threshold สำหรับ manual review

### 4.5 LLM Reasoning & Decision
- วิเคราะห์ responsibility boundary
- เลือก primary owner เพียง 1 คน
- ส่งออกผลลัพธ์เป็น JSON (owner, confidence, reason)

### 4.6 Assignment & Audit
- บันทึกผลการ assign
- เก็บเหตุผลและ confidence
- รองรับ manual override

### 4.7 Feedback Loop
- เก็บข้อมูลการแก้ไขโดยมนุษย์
- ใช้ปรับปรุง employee profile embedding

---

## 5. Non-Functional Requirements

### 5.1 Performance
- เวลาประมวลผลต่อเอกสาร < 10 วินาที (ไม่รวม OCR)
- รองรับเอกสารอย่างน้อย 10,000 ไฟล์/เดือน

### 5.2 Scalability
- รองรับการเพิ่มพนักงานและเอกสารโดยไม่ต้อง redesign

### 5.3 Security
- Encrypt เอกสาร at-rest และ in-transit
- Role-based access control (RBAC)
- Audit log ทุกการตัดสินใจของ AI

### 5.4 Explainability
- ทุก decision ต้องมี reason
- ตรวจสอบย้อนหลังได้

---

## 6. System Architecture

### 6.1 High-Level Flow
1. Upload PDF
2. OCR / Text Extract
3. Chunking
4. Embedding
5. Vector Search (Top-K Candidates)
6. LLM Reasoning
7. Assignment + Audit

---

## 7. Data Model (Summary)

### 7.1 Document
- doc_id
- filename
- upload_date
- document_type

### 7.2 DocumentChunk
- chunk_id
- doc_id
- content
- vector

### 7.3 EmployeeProfile
- employee_id
- role
- responsibility_description
- vectors[]

### 7.4 AssignmentLog
- assignment_id
- doc_id
- employee_id
- confidence
- reason
- created_at

---

## 8. AI Model Specification

### 8.1 Embedding Model
- Multilingual embedding (Thai supported)
- Dimension: 768–3072

### 8.2 LLM
- รองรับ reasoning
- รองรับ structured output (JSON)
- จำกัด context เฉพาะ evidence ที่จำเป็น

---

## 9. Error Handling
- OCR failure → manual review
- Low similarity score → manual review
- LLM failure → fallback semantic-only

---

## 10. Logging & Monitoring
- Log OCR errors
- Log embedding drift
- Monitor confidence distribution

---

## 11. Future Enhancements
- Multi-owner assignment
- Active learning
- Department-level routing
- Policy-based override

---

## 12. Acceptance Criteria
- Precision ≥ 85% หลังใช้งานจริง
- ทุก decision มีเหตุผลอธิบายได้
- ผู้ใช้สามารถ override ได้

---

**Document Version:** 1.0
**Status:** Draft for Implementation

