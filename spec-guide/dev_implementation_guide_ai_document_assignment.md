# Dev Implementation Guide
## ระบบจำแนกและมอบหมายเอกสารอัตโนมัติด้วย AI (Embedding + LLM Reasoning)

---

## 1. Architecture Overview

```
PDF Upload
 → OCR / Text Extraction
 → Chunking
 → Embedding
 → Vector Search (Employee Candidates)
 → LLM Reasoning (Decision)
 → Assignment + Audit Log
```

แยกบทบาทชัดเจน:
- **Embedding / Vector DB** = Recall (คัดตัวเลือก)
- **LLM** = Precision (ตัดสินใจ)

---

## 2. Repository Structure (Production-ready)

```
ai-doc-routing/
├── backend-ai/              # Python FastAPI (AI Core)
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── ingest.py
│   │   │   └── assign.py
│   │   ├── services/
│   │   │   ├── ocr.py
│   │   │   ├── chunker.py
│   │   │   ├── embedding.py
│   │   │   ├── semantic.py
│   │   │   └── llm_reasoning.py
│   │   ├── db/
│   │   └── models/
│   ├── requirements.txt
│   └── Dockerfile
│
├── backend-api/             # Node.js / NestJS (Business API)
└── frontend/                # Next.js (UI)
```

---

## 3. Core Processing Pipeline

### 3.1 Document Ingestion
- รับไฟล์ PDF (≤ 50MB)
- แยก text-based / scanned PDF
- เก็บ metadata (filename, page)

### 3.2 OCR / Text Extraction
- ใช้ `pdfplumber` สำหรับ text PDF
- ใช้ `Tesseract OCR` สำหรับ scanned PDF

Output:
- Raw text + page markers

---

## 4. Text Chunking

- Chunk size: **300–500 tokens**
- Overlap: **50–100 tokens**
- 1 chunk = 1 vector

วัตถุประสงค์:
- รองรับเอกสารหลายบริบท
- เพิ่มความแม่น semantic search

---

## 5. Embedding Layer

### 5.1 Embedding Model
- Multilingual (รองรับภาษาไทย)
- ใช้ model เดียวกันทั้ง document และ employee profile

### 5.2 Embedding Strategy
- Document: chunk → vector
- Employee: หลาย vector ต่อคน
  - job description
  - responsibility boundary
  - เอกสารที่เคยรับผิดชอบ

---

## 6. Vector Database (Semantic Search)

### 6.1 Database Choice
- ใช้ **PostgreSQL + pgvector** แทน Vector DB แยก (เช่น Qdrant)
- เหมาะกับระบบองค์กรที่ต้องการ
  - โครงสร้าง DB เดียว
  - Backup / Security / Compliance แบบเดิม

### 6.2 Extension
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 6.3 Table Design

**document_chunks**
```sql
CREATE TABLE document_chunks (
  id BIGSERIAL PRIMARY KEY,
  doc_id TEXT,
  page INT,
  content TEXT,
  embedding VECTOR(1536)
);
```

**employee_profiles**
```sql
CREATE TABLE employee_profiles (
  id BIGSERIAL PRIMARY KEY,
  employee_id TEXT,
  role TEXT,
  embedding VECTOR(1536)
);
```

### 6.4 Index (สำคัญ)
```sql
CREATE INDEX idx_doc_embedding ON document_chunks
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_emp_embedding ON employee_profiles
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);
```

---

## 7. Candidate Selection Logic

1. ค้นหา Top-K employee ต่อ chunk
2. รวมผลทุก chunk
3. เลือก Top 3–5 employees

หมายเหตุ:
- **score ใช้เฉพาะ backend**
- ไม่ส่ง score ให้ LLM

---

## 8. LLM Reasoning (Decision Layer)

### 8.1 Input Context
- Document summary
- Relevant excerpts (top chunks)
- Candidate responsibility profiles

### 8.2 Decision Rules
- เลือก owner เพียง 1 คน
- ตัดสินจาก responsibility ไม่ใช่ keyword
- ส่งออก JSON เท่านั้น

### 8.3 Output Schema

```json
{
  "owner": "EMPLOYEE_ID",
  "confidence": 0.0,
  "reason": "textual explanation"
}
```

---

## 9. Assignment & Audit

- บันทึกผลการ assign
- เก็บ confidence และ reason
- รองรับ manual override

### Audit Log Fields
- doc_id
- owner
- confidence
- reason
- created_at

---

## 10. Feedback Loop (Learning)

เมื่อมี manual reassign:
1. เก็บ correction
2. เพิ่ม document vector เข้า employee profile
3. ปรับ semantic space อัตโนมัติ

---

## 11. Error Handling & Fallback

- OCR ล้มเหลว → manual review
- Similarity ต่ำกว่า threshold → manual
- LLM error → fallback semantic-only

---

## 12. Performance & Ops

- Async worker สำหรับ OCR / embedding
- Queue: Redis / RabbitMQ
- Monitor confidence distribution
- Log ทุก LLM decision

---

## 13. Dev Checklist (Ready-to-Implement)

- [ ] OCR pipeline
- [ ] Chunking logic
- [ ] Embedding service
- [ ] Vector DB collections
- [ ] Candidate selection
- [ ] LLM prompt + schema
- [ ] Assignment log
- [ ] Feedback capture

---

**Status:** Dev Implementation Spec  
**Target:** Production-ready MVP → Enterprise

