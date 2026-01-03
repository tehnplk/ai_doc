export const API_BASE = 'http://localhost:8000/api/v1';

export interface DocumentResponse {
  doc_id: string;
  filename: string;
  stored_filename?: string;
  status: 'processing' | 'ready' | 'failed';
}

export interface AssignmentResponse {
  employee_id: string;
  employee_name: string | null;
  confidence: number;
  reason: string;
}

export async function uploadDocument(files: File[]): Promise<DocumentResponse> {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });

  const response = await fetch(`${API_BASE}/ingest`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(error.detail || 'Upload failed');
  }

  return response.json();
}

export async function assignDocument(docId: string): Promise<AssignmentResponse> {
  const response = await fetch(`${API_BASE}/assign/${docId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ force_reassign: false }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Assignment failed' }));
    throw new Error(error.detail || 'Assignment failed');
  }

  return response.json();
}
