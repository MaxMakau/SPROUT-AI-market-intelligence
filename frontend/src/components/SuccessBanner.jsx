import { motion } from 'framer-motion';
import { CheckCircle, X } from 'lucide-react';

export default function SuccessBanner({ message, onDismiss }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="bg-green-900/30 border border-green-700 rounded-lg p-4 mb-4 flex items-start gap-3"
      role="status"
    >
      <CheckCircle className="w-5 h-5 text-green-300 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        <p className="text-green-100 text-sm">{message}</p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-slate-400 hover:text-white transition"
          aria-label="Dismiss success"
        >
          <X className="w-5 h-5" />
        </button>
      )}
    </motion.div>
  );
}
