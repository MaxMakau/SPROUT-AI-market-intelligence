import { motion } from 'framer-motion';
import { Menu, X } from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: 'BarChart3' },
  { id: 'logistics', label: 'Logistics', icon: 'Truck' },
  { id: 'markets', label: 'Markets', icon: 'Store' },
  { id: 'forecast', label: 'Forecast', icon: 'TrendingUp' },
  { id: 'settings', label: 'Settings', icon: 'Settings' },
];

export default function TopNav({ onNavClick, activeNav = 'dashboard' }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="nav-sticky">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-2"
          >
            <div className="w-8 h-8 bg-gradient-to-br from-[#0EA5E9] to-[#7C3AED] rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">🌾</span>
            </div>
            <span className="hidden sm:block text-lg font-semibold bg-gradient-to-r from-[#0EA5E9] to-[#7C3AED] bg-clip-text text-transparent">
              SPROUT AI
            </span>
          </motion.div>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8">
            {navItems.map((item) => (
              <motion.button
                key={item.id}
                onClick={() => onNavClick?.(item.id)}
                whileHover={{ y: -2 }}
                whileTap={{ y: 0 }}
                className={`text-sm font-medium transition-colors pb-2 border-b-2 ${
                  activeNav === item.id
                    ? 'border-primary-600 text-text-primary'
                    : 'border-transparent text-text-muted hover:text-text-primary'
                }`}
              >
                {item.label}
              </motion.button>
            ))}
          </div>

          {/* Desktop Actions */}
          <div className="hidden md:flex items-center gap-4">
            <button
              className="p-2 hover:bg-surface-light rounded-lg transition-colors"
              aria-label="Notifications"
            >
              <svg className="w-5 h-5 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </button>
            <button
              className="p-2 hover:bg-surface-light rounded-lg transition-colors"
              aria-label="User profile"
            >
              <svg className="w-5 h-5 text-text-muted" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
              </svg>
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="md:hidden pb-4 border-t border-border-default"
          >
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  onNavClick?.(item.id);
                  setMobileMenuOpen(false);
                }}
                className={`block w-full text-left px-4 py-2 text-sm font-medium transition-colors ${
                  activeNav === item.id
                    ? 'text-primary-600'
                    : 'text-text-muted hover:text-text-primary'
                }`}
              >
                {item.label}
              </button>
            ))}
          </motion.div>
        )}
      </div>
    </nav>
  );
}
