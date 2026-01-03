'use client';

import { useState } from 'react';
import ImageUploader from '@/components/ImageUploader';
import ProcessingStatus from '@/components/ProcessingStatus';
import AssignmentResult from '@/components/AssignmentResult';
import { uploadDocument, assignDocument, DocumentResponse, AssignmentResponse } from '@/lib/api';
import { Brain, Sparkles, RefreshCcw } from 'lucide-react';

type FlowStatus = 'uploading' | 'processing' | 'assigning' | 'complete' | 'error';

export default function Home() {
  const [status, setStatus] = useState<FlowStatus>('uploading');
  const [error, setError] = useState<string | undefined>();
  const [currentDoc, setCurrentDoc] = useState<DocumentResponse | null>(null);
  const [assignment, setAssignment] = useState<AssignmentResponse | null>(null);

  const handleUpload = async (files: File[]) => {
    try {
      setStatus('processing');
      setError(undefined);

      // 1. Upload Document (Includes OCR + Embedding)
      const doc = await uploadDocument(files);
      setCurrentDoc(doc);
      
      if (doc.status === 'failed') {
        throw new Error('Document processing failed at OCR stage');
      }

      // 2. Assign Document
      setStatus('assigning');
      setTimeout(async () => { // Artificial delay for better UX transition
        try {
          const result = await assignDocument(doc.doc_id);
          setAssignment(result);
          setStatus('complete');
        } catch (err: any) {
          setStatus('error');
          setError(err.message || 'Assignment failed');
        }
      }, 1500);

    } catch (err: any) {
      console.error(err);
      setStatus('error');
      setError(err.message || 'Something went wrong');
    }
  };

  const handleReset = () => {
    setStatus('uploading');
    setError(undefined);
    setCurrentDoc(null);
    setAssignment(null);
  };

  return (
    <main className="min-h-screen p-8 md:p-24 relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-0 left-0 w-full h-[500px] bg-gradient-to-b from-[var(--bg-secondary)] to-transparent -z-10" />
      <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[120px] -z-10" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[100px] -z-10" />

      <div className="max-w-5xl mx-auto space-y-12">
        
        {/* Header */}
        <div className="flex flex-col items-center text-center space-y-4">
          <div className="p-3 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-white/5 shadow-2xl backdrop-blur-sm mb-4">
             <Brain size={48} className="text-[var(--color-accent)]" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
            AI Job Assignment
          </h1>
          <p className="text-lg text-[var(--text-secondary)] max-w-2xl">
            Upload document images to automatically analyze content and assign them to the right employee.
          </p>
        </div>

        {/* Status Indicator */}
        <ProcessingStatus status={status} error={error} />

        {/* Main Content Area */}
        <div className="min-h-[400px]">
          {status === 'uploading' && (
            <ImageUploader onUpload={handleUpload} isUploading={false} />
          )}

          {(status === 'processing' || status === 'assigning') && (
            <div className="flex flex-col items-center justify-center p-12 text-center text-[var(--text-secondary)] animate-pulse">
               <Sparkles className="mb-4 text-[var(--color-accent)]" size={32} />
               <p className="text-xl font-medium text-white">AI is analyzing your document...</p>
               <p className="mt-2 text-sm">Extracting text, understanding context, and finding the best match.</p>
            </div>
          )}

          {status === 'complete' && assignment && currentDoc && (
            <div className="space-y-8">
              <AssignmentResult assignment={assignment} document={currentDoc} />
              <div className="flex justify-center">
                <button
                  onClick={handleReset}
                  className="px-6 py-3 rounded-xl bg-[var(--bg-secondary)] border border-gray-700 hover:bg-gray-800 transition-colors flex items-center space-x-2 text-sm font-medium"
                >
                  <RefreshCcw size={16} />
                  <span>Process Another Document</span>
                </button>
              </div>
            </div>
          )}

          {status === 'error' && (
             <div className="flex justify-center mt-8">
               <button
                  onClick={handleReset}
                  className="px-6 py-3 rounded-xl bg-[var(--color-accent)] text-white hover:brightness-110 transition-all font-medium"
                >
                  Try Again
                </button>
             </div>
          )}
        </div>
      </div>
    </main>
  );
}
