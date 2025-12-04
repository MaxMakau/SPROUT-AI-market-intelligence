// Theme tokens and design constants
export const colors = {
  primary: '#2563EB',
  primaryGradient: 'from-[#0EA5E9] to-[#7C3AED]',
  accent: '#10B981',
  danger: '#EF4444',
  surface: {
    dark: '#0F172A',
    light: '#0B1220',
  },
  text: {
    primary: '#E6EEF8',
    muted: '#94A3B8',
  },
  border: '#1F2A44',
  transport: {
    lorry: '#065F46',
    pickup: '#B45309',
    motorbike: '#6D28D9',
  }
};

export const typography = {
  h1: { fontSize: '36px', lineHeight: '48px', fontWeight: 600 },
  h2: { fontSize: '28px', lineHeight: '36px', fontWeight: 600 },
  h3: { fontSize: '20px', lineHeight: '28px', fontWeight: 600 },
  body: { fontSize: '16px', lineHeight: '24px', fontWeight: 400 },
  small: { fontSize: '13px', lineHeight: '20px', fontWeight: 400 },
  label: { fontSize: '14px', lineHeight: '20px', fontWeight: 500 },
};

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '12px',
  base: '16px',
  lg: '20px',
  xl: '24px',
  '2xl': '32px',
  '3xl': '40px',
  '4xl': '48px',
};

export const motion = {
  timings: {
    fast: '120ms',
    standard: '240ms',
    slow: '420ms',
  },
  easing: {
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
    smooth: 'cubic-bezier(.2,.9,.2,1)',
  },
};

export const breakpoints = {
  mobile: '640px',
  tablet: '1024px',
  desktop: '1280px',
};

// Transport mode configuration
export const transportModes = {
  motorbike: {
    icon: 'Bike',
    label: 'Motorbike',
    color: '#7C3AED',
    bgColor: '#6D28D9',
    badge: 'badge-purple',
  },
  pickup: {
    icon: 'Car',
    label: 'Pickup',
    color: '#F59E0B',
    bgColor: '#B45309',
    badge: 'badge-amber',
  },
  lorry: {
    icon: 'Truck',
    label: 'Lorry',
    color: '#10B981',
    bgColor: '#065F46',
    badge: 'badge-green',
  },
};

// Market configuration
export const marketDefaults = {
  refreshInterval: 60000, // 1 minute
  cacheTimeout: 5 * 60000, // 5 minutes
};

// Farmer demo data for development
export const demoFarmer = {
  id: 'farmer-1',
  name: 'John Kipchoge',
  location: 'Nairobi',
  quantity_sacks: 5,
  distance_km: 12.4,
  best_market_location: 'Nairobi Central Market',
  market_price: 70, // price per kg
};

// Mock markets for fallback (prices in Kenyan Shillings per kg)
export const mockMarkets = [
  {
    id: 'market-1',
    name: 'Nairobi Central Market',
    latitude: -1.286389,
    longitude: 36.817223,
    latest_price: 70, // sh/kg
    distance_km: 12.4,
  },
  {
    id: 'market-2',
    name: 'Mombasa Port Market',
    latitude: -4.043477,
    longitude: 39.668205,
    latest_price: 65, // sh/kg
    distance_km: 480.0,
  },
  {
    id: 'market-3',
    name: 'Kisumu Market',
    latitude: -0.100655,
    longitude: 34.768066,
    latest_price: 68, // sh/kg
    distance_km: 400.0,
  },
  {
    id: 'market-4',
    name: 'Nakuru Farmers Market',
    latitude: -0.303099,
    longitude: 36.080025,
    latest_price: 72, // sh/kg
    distance_km: 160.0,
  },
  {
    id: 'market-5',
    name: 'Eldoret Central Market',
    latitude: 0.515,
    longitude: 35.28,
    latest_price: 66, // sh/kg
    distance_km: 320.0,
  },
  {
    id: 'market-6',
    name: 'Thika Farmers Cooperative',
    latitude: -1.0338,
    longitude: 37.0833,
    latest_price: 75, // sh/kg
    distance_km: 45.0,
  },
  {
    id: 'market-7',
    name: 'Kitale Grain Market',
    latitude: 1.0191,
    longitude: 35.0021,
    latest_price: 64, // sh/kg
    distance_km: 450.0,
  },
  {
    id: 'market-8',
    name: 'Machakos Town Market',
    latitude: -2.7149,
    longitude: 37.2623,
    latest_price: 69, // sh/kg
    distance_km: 65.0,
  },
];
