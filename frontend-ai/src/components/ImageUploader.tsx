'use client';

import { useState } from 'react';
import { Upload, X, FileImage, FileText, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

interface Props {
  onUpload: (files: File[]) => Promise<void>;
  isUploading: boolean;
}

export default function ImageUploader({ onUpload, isUploading }: Props) {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState<File[]>([]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(Array.from(e.target.files));
    }
  };

  const handleFiles = (newFiles: File[]) => {
    // Filter for images and PDFs
    const validFiles = newFiles.filter(file => 
      file.type.startsWith('image/') || file.type === 'application/pdf'
    );
    setFiles(prev => [...prev, ...validFiles]);
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (files.length > 0) {
      await onUpload(files);
      setFiles([]); // Clear after successful upload
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      <label
        className={cn(
          "relative h-64 rounded-2xl border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center cursor-pointer glass-card overflow-hidden group",
          dragActive 
            ? "border-[var(--color-accent)] bg-[rgba(59,130,246,0.1)]" 
            : "border-gray-700 hover:border-gray-500 hover:bg-[rgba(255,255,255,0.02)]"
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          multiple
          accept="image/*,.pdf"
          className="hidden"
          onChange={handleChange}
        />
        
        <div className="flex flex-col items-center space-y-4 text-center p-6">
          <div className="p-4 rounded-full bg-[rgba(59,130,246,0.1)] text-[var(--color-accent)] group-hover:scale-110 transition-transform duration-300">
            <Upload size={32} />
          </div>
          <div className="space-y-1">
            <p className="text-lg font-medium">Drag & Drop images here</p>
            <p className="text-sm text-[var(--text-secondary)]">or click to browse</p>
          </div>
          <p className="text-xs text-[var(--text-secondary)] pt-2">
            Supports JPG, PNG, WebP, PDF
          </p>
        </div>
      </label>

      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-4"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {files.map((file, idx) => (
                <div
                  key={`${file.name}-${idx}`}
                  className="flex items-center justify-between p-3 rounded-xl glass border border-gray-800"
                >
                  <div className="flex items-center space-x-3 overflow-hidden">
                    <div className="p-2 rounded-lg bg-gray-800 text-gray-400">
                      {file.type === 'application/pdf' ? <FileText size={20} /> : <FileImage size={20} />}
                    </div>
                    <div className="truncate">
                      <p className="text-sm font-medium truncate max-w-[150px]">{file.name}</p>
                      <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(idx)}
                    className="p-1 hover:bg-gray-800 rounded-full transition-colors"
                  >
                    <X size={16} className="text-gray-400" />
                  </button>
                </div>
              ))}
            </div>

            <button
              onClick={handleSubmit}
              disabled={isUploading}
              className="w-full py-4 rounded-xl bg-[var(--color-accent)] hover:brightness-110 transition-all font-medium text-white flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:shadow-[0_0_30px_rgba(59,130,246,0.5)]"
            >
              {isUploading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Upload size={20} />
                  <span>Process {files.length} Document{files.length > 1 ? 's' : ''}</span>
                </>
              )}
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
