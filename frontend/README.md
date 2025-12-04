# SPROUT AI Frontend

A production-ready React frontend for the SPROUT AI Agri-Market Advisor system. Built with Vite, React 18, Tailwind CSS, Framer Motion, and integrates with the FastAPI backend for market recommendations and logistics optimization.

## Features

✨ **Core Features**
- **Dashboard**: Real-time KPI metrics, price trends, and market overview
- **Logistics Management**: AI-powered transport mode recommendations (motorbike, pickup, lorry)
- **Market Exploration**: Interactive map with market locations and pricing
- **Price Analytics**: Historical price trends with recharts visualization
- **Responsive Design**: Mobile-first, fully responsive on all devices
- **Accessibility**: WCAG AA compliant with keyboard navigation
- **Animations**: Smooth Framer Motion transitions and micro-interactions

## Tech Stack

- **Frontend Framework**: React 18.3.1
- **Build Tool**: Vite 5.1.6
- **Styling**: Tailwind CSS 3.4.1
- **Animations**: Framer Motion 10.16.20
- **Charts**: Recharts 2.10.3
- **Icons**: Lucide React 0.344.0
- **Maps**: Mapbox GL JS 3.0.1 (optional)
- **Testing**: Vitest + React Testing Library
- **Package Manager**: npm/yarn

## Project Structure

```
frontend/
├── src/
│   ├── components/              # Reusable UI components
│   │   ├── AnimatedBackground.jsx
│   │   ├── TopNav.jsx
│   │   ├── LoadingSpinner.jsx
│   │   ├── ErrorBanner.jsx
│   │   ├── LogisticsCard.jsx     # Main logistics UI
│   │   ├── LogisticsModal.jsx
│   │   ├── MarketCard.jsx
│   │   ├── MapPanel.jsx
│   │   ├── PriceChart.jsx
│   │   └── KPIStrip.jsx
│   ├── lib/
│   │   ├── apiClient.js          # API client with retry logic
│   │   └── constants.js          # Design tokens & config
│   ├── tests/
│   │   ├── LogisticsCard.test.jsx
│   │   └── apiClient.test.js
│   ├── App.jsx                   # Main app component
│   ├── main.jsx                  # Entry point
│   └── index.css                 # Global styles
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── vite.config.ts
├── vitest.config.js
├── .env.example
└── README.md
```

## Getting Started

### Prerequisites
- Node.js 18.0.0 or higher
- npm or yarn

### Installation

1. **Clone and navigate to frontend:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Set up environment variables:**
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_MAPBOX_TOKEN=your_mapbox_token_here
VITE_API_TOKEN=your_api_token_here
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Production Build

```bash
npm run build
```

Output is in `dist/` directory, ready for deployment.

### Preview Production Build

```bash
npm run preview
```

### Run Tests

```bash
npm run test
```

Watch mode:
```bash
npm run test -- --watch
```

UI mode:
```bash
npm run test:ui
```

## API Integration

The frontend consumes these backend endpoints:

### POST /api/logistics/recommend
Get transport recommendation and cost calculation.

**Request:**
```json
{
  "quantity_sacks": 5,
  "distance_km": 12.4,
  "best_market_location": "Nairobi Central Market",
  "market_price": 2400.0
}
```

**Response:**
```json
{
  "transport_mode": "pickup",
  "transport_cost_kes": 3500,
  "distance_km": 12.4,
  "best_market_location": "Nairobi Central Market",
  "market_price": 2400.0
}
```

### GET /api/predict/markets
Get list of available markets with pricing.

### GET /api/price-history
Get historical price data for charts.

### POST /api/shipments
Create a new shipment with logistics details.

See `src/lib/apiClient.js` for all API client methods.

## Design System

### Color Palette

```javascript
Primary Gradient: #0EA5E9 → #7C3AED
Primary Solid: #2563EB
Accent: #10B981
Danger: #EF4444
Surface Dark: #0F172A
Surface Light: #0B1220
Text Primary: #E6EEF8
Text Muted: #94A3B8
Border: #1F2A44
```

### Typography

- **Headings (h1-h3)**: Inter 600, 36-20px
- **Body Text**: Inter 400, 16px
- **Small Text**: Inter 400, 13px
- **Labels**: Inter 500, 14px

### Spacing

Grid-based on multiples of 4px: 4, 8, 12, 16, 20, 24, 32, 40, 48

### Motion

- **Fast**: 120ms ease-out
- **Standard**: 240ms cubic-bezier(.2,.9,.2,1)
- **Slow**: 420ms ease-in-out

## Component Examples

### LogisticsCard

Displays logistics recommendation with transport mode, cost, and actions:

```jsx
import LogisticsCard from './components/LogisticsCard';

<LogisticsCard
  farmer={{
    quantity_sacks: 5,
    distance_km: 12.4,
    best_market_location: 'Nairobi Central Market',
    market_price: 2400.0,
  }}
  onCreateShipment={(plan) => console.log(plan)}
/>
```

### PriceChart

Displays 30-day price trends:

```jsx
import PriceChart from './components/PriceChart';

<PriceChart data={priceHistory} />
```

### MapPanel

Shows market locations and farmer location:

```jsx
import MapPanel from './components/MapPanel';

<MapPanel
  markets={markets}
  farmerLocation="Nairobi"
  onMarketClick={(market) => console.log(market)}
/>
```

## Accessibility

✅ **Features:**
- Full keyboard navigation (Tab, Enter, Escape)
- ARIA labels on all interactive elements
- Color contrast WCAG AA compliance
- Focus indicators on all buttons
- Error messages announced to screen readers
- Mobile-friendly touch targets (min 44x44px)
- Semantic HTML structure

✅ **Localization:**
- Currency formatting using Intl.NumberFormat
- Date formatting with browser locale
- Number formatting with locale support

## Responsive Breakpoints

- **Mobile**: ≤ 640px (1 column, collapsed map)
- **Tablet**: 641px – 1024px (2 columns, map on top)
- **Desktop**: > 1024px (3-column layout, full map)

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Code splitting with Vite
- Lazy loading for components
- Image optimization
- CSS minification
- Tree shaking of unused dependencies
- Caching with proper HTTP headers

## Deployment

### Netlify

```bash
npm run build
netlify deploy --prod --dir=dist
```

### Vercel

```bash
npm run build
vercel deploy --prod
```

### Docker

Create `Dockerfile`:
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
docker build -t sprout-ai-frontend .
docker run -p 80:80 sprout-ai-frontend
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_BASE_URL` | Yes | Backend API base URL (e.g., http://localhost:8000) |
| `VITE_MAPBOX_TOKEN` | No | Mapbox GL JS token for maps |
| `VITE_API_TOKEN` | No | Optional Bearer token for API authentication |

## Testing

### Unit Tests

```bash
npm run test
```

### Test Coverage

```bash
npm run test -- --coverage
```

### E2E Testing (Skeleton)

Add Playwright or Cypress for end-to-end tests:

```bash
npm install -D @playwright/test
npx playwright install
npm run test:e2e
```

## Troubleshooting

### API Connection Issues

1. Verify backend is running on `http://localhost:8000`
2. Check `VITE_API_BASE_URL` in `.env.local`
3. Ensure CORS is enabled on backend
4. Check browser console for network errors

### Styling Issues

1. Clear node_modules and reinstall: `rm -rf node_modules && npm install`
2. Rebuild Tailwind: `npm run build`
3. Verify tailwind.config.js syntax

### Build Errors

1. Check Node version: `node --version` (should be 18+)
2. Clear Vite cache: `rm -rf dist && npm run build`
3. Check for TypeScript errors: `npx tsc --noEmit`

## Development Tips

- Use React DevTools extension for debugging
- Use Tailwind CSS IntelliSense extension in VS Code
- Enable Framer Motion DevTools for animation debugging
- Use `npm run test -- --watch` for TDD workflow
- Check `src/lib/constants.js` for design tokens

## Contributing

1. Create a feature branch
2. Make changes following the existing code style
3. Add/update tests
4. Ensure `npm run test` passes
5. Create a pull request

## License

MIT License - See LICENSE file

## Support

For issues and questions:
- GitHub Issues: [Create issue](https://github.com/MaxMakau/SPROUT-AI-market-intelligence/issues)
- Email: support@sproutai.com

## Changelog

### v1.0.0 (2024-12-04)
- Initial release
- Dashboard with KPI metrics
- Logistics recommendation engine UI
- Market exploration with pricing
- Price trend charts
- Responsive mobile-first design
- Full accessibility support
- Comprehensive test suite

---

**Made with 🌾 for African Farmers**
