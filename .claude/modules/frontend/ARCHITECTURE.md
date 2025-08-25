# Frontend Architecture
Last Updated: 2025-08-25 00:00:00 UTC

The frontend is a React + TypeScript application generated via Create React App.

## Folder Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI elements
│   ├── services/         # API clients and helpers
│   ├── App.tsx           # Application root
│   ├── index.tsx         # Entry point
│   └── setupTests.ts     # Jest configuration
├── public/               # Static assets
└── package.json          # Project metadata
```

## State Management

- Local component state using React hooks.
- Remote data fetched via functions in `services/api.ts`.
- React Query or SWR can be introduced for caching.

## Build Pipeline

- `npm start` launches the dev server on port 3000 with hot reload.
- `npm run build` outputs static files to `build/` for serving via the backend.

---
*Refer to `.claude/modules/frontend/guide.md` for day-to-day commands.*
