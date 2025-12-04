import { motion } from 'framer-motion';

export default function AnimatedBackground() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-surface-dark via-surface-dark to-[#1a2a47]" />

      {/* Animated blobs */}
      <motion.svg
        className="absolute inset-0 w-full h-full opacity-30"
        viewBox="0 0 1200 600"
        animate={{
          rotate: 360,
        }}
        transition={{
          duration: 40,
          repeat: Infinity,
          ease: "linear"
        }}
      >
        <defs>
          <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#0EA5E9" />
            <stop offset="100%" stopColor="#7C3AED" />
          </linearGradient>
          <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#7C3AED" />
            <stop offset="100%" stopColor="#10B981" />
          </linearGradient>
        </defs>
        <motion.circle
          cx="300"
          cy="300"
          r="200"
          fill="url(#grad1)"
          animate={{
            cx: [300, 350, 300],
            cy: [300, 280, 300],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          style={{ filter: 'blur(60px)' }}
        />
        <motion.circle
          cx="900"
          cy="300"
          r="150"
          fill="url(#grad2)"
          animate={{
            cx: [900, 850, 900],
            cy: [300, 320, 300],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          style={{ filter: 'blur(60px)' }}
        />
      </motion.svg>

      {/* Fallback gradient for disabled animations */}
      <div
        className="absolute inset-0 bg-gradient-to-br from-[#0EA5E9]/5 via-transparent to-[#7C3AED]/5"
        style={{ pointerEvents: 'none' }}
      />
    </div>
  );
}
