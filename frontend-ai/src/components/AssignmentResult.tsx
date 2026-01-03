'use client';

import { motion } from 'framer-motion';
import { CheckCircle2, User, FileText, Sparkles, ChevronDown, ExternalLink } from 'lucide-react';
import { AssignmentResponse, DocumentResponse } from '@/lib/api';
import { useState } from 'react';
import { cn } from '@/lib/utils';

interface Props {
  assignment: AssignmentResponse;
  document: DocumentResponse;
}

export default function AssignmentResult({ assignment, document }: Props) {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-2xl mx-auto"
    >
      <div className="glass-card rounded-2xl overflow-hidden p-1">
        <div className="bg-[rgba(16,185,129,0.1)] p-6 border-b border-[rgba(16,185,129,0.2)] flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-emerald-500 rounded-full text-white shadow-lg shadow-emerald-500/30">
              <CheckCircle2 size={32} />
            </div>
            <div>
              <p className="text-sm text-emerald-400 font-medium uppercase tracking-wider">Assignment Complete</p>
              <h2 className="text-2xl font-bold">Job Assigned Successfully</h2>
            </div>
          </div>
          <div className="text-right hidden sm:block">
            <p className="text-xs text-[var(--text-secondary)]">Document ID</p>
            <p className="text-sm font-mono text-emerald-400">{document.doc_id.slice(0, 8)}...</p>
          </div>
        </div>

        <div className="p-8 space-y-8">
          {/* Main Assignment Info */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
             <div className="flex items-center space-x-6">
               <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white shadow-xl transform rotate-3">
                 <User size={40} />
               </div>
               <div>
                 <p className="text-sm text-[var(--text-secondary)] mb-1">Assigned To</p>
                 <h3 className="text-3xl font-bold">{assignment.employee_name || 'Unknown Employee'}</h3>
                 <div className="flex items-center space-x-2 mt-2">
                   <div className="px-2 py-0.5 rounded text-xs bg-gray-800 text-gray-300 border border-gray-700">
                     {assignment.employee_id}
                   </div>
                 </div>
               </div>
             </div>

             <div className="flex flex-col items-end">
               <div className="text-right mb-2">
                 <p className="text-sm text-[var(--text-secondary)]">AI Confidence</p>
                 <div className="flex items-baseline space-x-1">
                   <span className="text-4xl font-bold text-[var(--color-accent)]">{(assignment.confidence * 100).toFixed(0)}</span>
                   <span className="text-lg text-[var(--color-accent)]">%</span>
                 </div>
               </div>
               <div className="w-32 h-2 bg-gray-800 rounded-full overflow-hidden">
                 <motion.div 
                   initial={{ width: 0 }}
                   animate={{ width: `${assignment.confidence * 100}%` }}
                   transition={{ duration: 1, delay: 0.5 }}
                   className="h-full bg-[var(--color-accent)]"
                 />
               </div>
             </div>
          </div>

          <div className="h-px bg-gray-800" />

          {/* Reasoning Section */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2 text-[var(--color-accent)]">
              <Sparkles size={18} />
              <span className="font-medium">Why was this employee chosen?</span>
            </div>
            
            <div className="relative">
              <div className="p-5 rounded-xl bg-[var(--bg-secondary)] border border-gray-800 leading-relaxed text-gray-300">
                {assignment.reason}
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 text-xs text-gray-500 border-t border-gray-800">
             <div className="flex items-center space-x-4">
               <div className="flex items-center space-x-2">
                 <FileText size={14} />
                 <span>Source: {document.filename}</span>
               </div>
               
               <button 
                 onClick={() => window.open(`http://localhost:8000/api/v1/files/${document.stored_filename?.split(',')[0]}`, '_blank')}
                 className="flex items-center space-x-1 text-[var(--color-accent)] hover:underline"
               >
                 <ExternalLink size={14} />
                 <span>Open Original</span>
               </button>
             </div>

             {/* Inline Preview */}
             {document.stored_filename && (
                <div className="mt-4 w-full">
                  <p className="text-sm font-medium text-gray-400 mb-2">Document Preview</p>
                  <div className="flex gap-2 overflow-x-auto pb-2">
                    {document.stored_filename.split(',').map((filename, idx) => (
                      <div key={idx} className="relative min-w-[200px] h-[280px] rounded-lg overflow-hidden border border-gray-700 bg-black/40">
                         <img 
                           src={`http://localhost:8000/api/v1/files/${filename}`} 
                           alt={`Page ${idx + 1}`}
                           className="w-full h-full object-contain hover:scale-105 transition-transform duration-300"
                           loading="lazy"
                         />
                      </div>
                    ))}
                  </div>
                </div>
             )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
