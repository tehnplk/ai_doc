-- Initialize pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    doc_id UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    document_type TEXT,
    status TEXT DEFAULT 'pending',
    upload_date TIMESTAMP DEFAULT NOW()
);

-- Document chunks with embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
    id BIGSERIAL PRIMARY KEY,
    doc_id UUID REFERENCES documents(doc_id) ON DELETE CASCADE,
    page INT,
    chunk_index INT,
    content TEXT,
    embedding VECTOR(768),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Employee profiles
CREATE TABLE IF NOT EXISTS employee_profiles (
    id BIGSERIAL PRIMARY KEY,
    employee_id TEXT UNIQUE NOT NULL,
    name TEXT,
    role TEXT,
    responsibility_description TEXT,
    embedding VECTOR(768),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Assignment audit log
CREATE TABLE IF NOT EXISTS assignment_logs (
    id BIGSERIAL PRIMARY KEY,
    doc_id UUID REFERENCES documents(doc_id) ON DELETE CASCADE,
    employee_id TEXT REFERENCES employee_profiles(employee_id),
    confidence FLOAT,
    reason TEXT,
    is_manual_override BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vector indexes for similarity search
CREATE INDEX IF NOT EXISTS idx_chunk_embedding ON document_chunks
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_employee_embedding ON employee_profiles
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);

-- Useful indexes
CREATE INDEX IF NOT EXISTS idx_doc_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_doc_upload_date ON documents(upload_date DESC);
CREATE INDEX IF NOT EXISTS idx_chunk_doc_id ON document_chunks(doc_id);
CREATE INDEX IF NOT EXISTS idx_assignment_doc_id ON assignment_logs(doc_id);
