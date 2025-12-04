import { motion } from 'framer-motion';

export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        className="w-10 h-10 border-3 border-cyan-600 border-t-transparent rounded-full"
      />
      <p className="mt-4 text-slate-400 text-sm">{message}</p>
    </div>
  );
}
