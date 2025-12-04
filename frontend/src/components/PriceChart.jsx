import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';

export default function PriceChart({ data = [] }) {
  // Mock data if none provided
  const chartData = data.length > 0 ? data : Array.from({ length: 30 }, (_, i) => ({
    date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short'
    }),
    price: Math.floor(Math.random() * 1000 + 1500)
  }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="card col-span-1 md:col-span-2"
    >
      <h3 className="card-title mb-6">Price Trends (Last 30 Days)</h3>
      <div className="h-80 md:h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1F2A44" />
            <XAxis
              dataKey="date"
              stroke="#94A3B8"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              stroke="#94A3B8"
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => `KES ${(value / 1000).toFixed(1)}k`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0B1220',
                border: '1px solid #1F2A44',
                borderRadius: '8px',
              }}
              labelStyle={{ color: '#E6EEF8' }}
              formatter={(value) => [
                new Intl.NumberFormat('en-KE', {
                  style: 'currency',
                  currency: 'KES',
                  minimumFractionDigits: 0,
                }).format(value),
                'Price',
              ]}
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#0EA5E9"
              strokeWidth={2}
              dot={false}
              isAnimationActive={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
