'use client';

import { Loader2, CheckCircle, BrainCircuit, UserCheck, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface Props {
  status: 'uploading' | 'processing' | 'assigning' | 'complete' | 'error';
  error?: string;
}

export default function ProcessingStatus({ status, error }: Props) {
  const steps = [
    {
      id: 'uploading',
      label: 'Uploading',
      icon: Loader2,
      activeStates: ['uploading', 'processing', 'assigning', 'complete'],
    },
    {
      id: 'processing',
      label: 'OCR Extracting',
      icon: BrainCircuit,
      activeStates: ['processing', 'assigning', 'complete'],
    },
    {
      id: 'assigning',
      label: 'AI Assigning',
      icon: UserCheck,
      activeStates: ['assigning', 'complete'],
    },
  ];

  if (status === 'error') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl mx-auto p-4 rounded-xl bg-[rgba(239,68,68,0.1)] border border-[var(--color-error)] text-[var(--color-error)] flex items-center space-x-3"
      >
        <AlertCircle size={24} />
        <div>
          <p className="font-semibold">Processing Failed</p>
          <p className="text-sm opacity-90">{error || 'An unknown error occurred'}</p>
        </div>
      </motion.div>
    );
  }

  // Find current step index
  const currentStepIndex = steps.findIndex(s => s.id === status);
  if (currentStepIndex === -1 && status !== 'complete') return null;

  return (
    <div className="w-full max-w-2xl mx-auto py-8">
      <div className="relative flex justify-between">
        {/* Progress Bar Background */}
        <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-800 -z-10 rounded-full" />
        
        {/* Active Progress Bar */}
        <motion.div 
          className="absolute top-1/2 left-0 h-1 bg-[var(--color-accent)] -z-10 rounded-full"
          initial={{ width: '0%' }}
          animate={{ 
            width: status === 'complete' 
              ? '100%' 
              : `${(currentStepIndex / (steps.length - 1)) * 100}%` 
          }}
          transition={{ duration: 0.5 }}
        />

        {steps.map((step, idx) => {
          const isActive = step.activeStates.includes(status);
          const isCompleted = idx < currentStepIndex || status === 'complete';
          const isCurrent = step.id === status;

          return (
            <div key={step.id} className="flex flex-col items-center space-y-3 relative bg-[var(--bg-primary)] px-2">
              <motion.div
                initial={false}
                animate={{
                  backgroundColor: isActive ? 'var(--color-accent)' : 'var(--bg-secondary)',
                  scale: isCurrent ? 1.1 : 1,
                }}
                className={cn(
                  "w-12 h-12 rounded-full flex items-center justify-center border-4 border-[var(--bg-primary)] transition-colors duration-500",
                  isActive ? "text-white shadow-[0_0_20px_rgba(59,130,246,0.4)]" : "text-gray-600"
                )}
              >
                {isCompleted ? (
                   <CheckCircle size={20} />
                ) : (
                   <step.icon size={20} className={cn(isCurrent && "animate-spin")} />
                )}
              </motion.div>
              <p className={cn(
                "text-sm font-medium transition-colors duration-300",
                isActive ? "text-[var(--text-primary)]" : "text-[var(--text-secondary)]"
              )}>
                {step.label}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
