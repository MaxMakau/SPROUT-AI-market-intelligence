import { motion } from 'framer-motion';

const kpiCards = [
  {
    id: 'farmers',
    label: 'Total Farmers',
    value: '2,847',
    change: '+12%',
    icon: '👨‍🌾'
  },
  {
    id: 'shipments',
    label: 'Active Shipments',
    value: '156',
    change: '+8%',
    icon: '🚚'
  },
  {
    id: 'distance',
    label: 'Avg Distance',
    value: '145 km',
    change: '-3%',
    icon: '📍'
  },
  {
    id: 'cost',
    label: 'Avg Transport Cost',
    value: 'KES 2,450',
    change: '-5%',
    icon: '💰'
  },
];

export default function KPIStrip() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {kpiCards.map((kpi, idx) => (
        <motion.div
          key={kpi.id}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.1 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-3">
            <h3 className="card-subtitle">{kpi.label}</h3>
            <span className="text-2xl">{kpi.icon}</span>
          </div>
          <div className="flex items-baseline gap-2">
            <div className="text-2xl font-bold text-text-primary">{kpi.value}</div>
            <span className="text-xs font-medium text-accent">{kpi.change}</span>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
