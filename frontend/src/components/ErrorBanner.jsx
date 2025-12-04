import { motion } from 'framer-motion';
import { AlertCircle, X } from 'lucide-react';

export default function ErrorBanner({ message, onDismiss, type = 'error' }) {
  const bgColor = type === 'error' ? 'bg-red-900/30' : 'bg-amber-900/30';
  const textColor = type === 'error' ? 'text-red-300' : 'text-amber-300';
  const borderColor = type === 'error' ? 'border-red-700' : 'border-amber-700';

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={`${bgColor} border ${borderColor} rounded-lg p-4 mb-4 flex items-start gap-3`}
      role="alert"
    >
      <AlertCircle className={`w-5 h-5 ${textColor} flex-shrink-0 mt-0.5`} />
      <div className="flex-1">
        <p className={`${textColor} text-sm`}>{message}</p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-slate-400 hover:text-white transition"
          aria-label="Dismiss error"
        >
          <X className="w-5 h-5" />
        </button>
      )}
    </motion.div>
  );
}
