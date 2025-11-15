# Mids Hero Web - Frontend

Modern Next.js 14 frontend for Mids Hero Web build planner.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.x (strict mode)
- **Styling**: Tailwind CSS 3.x
- **Components**: shadcn/ui
- **Testing**: Vitest + React Testing Library

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- npm or yarn

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Open http://localhost:3000

### Testing

```bash
# Run tests
npm test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

### Build

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Homepage
│   ├── providers.tsx       # React context providers
│   └── globals.css         # Global styles
├── components/
│   ├── ui/                 # shadcn/ui components
│   └── layout/             # Layout components (TopNav, Footer)
│       └── __tests__/      # Component tests
├── lib/
│   └── utils.ts            # Utility functions
└── test/
    └── setup.ts            # Test configuration
```

## Design System

### Colors

MidsReborn-inspired dark theme:

- **Background**: `#000000` (pure black)
- **Panels**: `#1a1a1a`, `#222222`
- **Hero Blue**: `#0066FF`
- **Hero Cyan**: `#00CCFF`
- **Villain Red**: `#CC0000`
- **Accent Orange**: `#FF9900`

See `app/globals.css` for full color palette.

### Components

Initial shadcn/ui components installed:
- Button
- Dialog
- Select
- Tabs
- Tooltip

## Next Steps

- Epic 1.2: State Management Setup (TanStack Query + Zustand)
- Epic 1.3: Layout Shell + Navigation
- Epic 1.4: API Client Integration

## References

- [Architecture](../docs/frontend/architecture.md)
- [Epic Breakdown](../docs/frontend/epic-breakdown.md)
- [MidsReborn UI Analysis](../docs/frontend/analysis/MIDSREBORN-UI-ANALYSIS-epic-1.1.md)
