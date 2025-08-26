# Frontend Module Guide
Last Updated: 2025-08-25 00:00:00 UTC

## Quick Reference

```bash
# Start React development server
cd frontend && npm start

# Run frontend tests once
cd frontend && npm test -- --watchAll=false

# Build production assets
cd frontend && npm run build
```

## Project Layout

```
frontend/
├── src/
│   ├── components/    # React components
│   ├── services/      # API clients
│   └── App.tsx        # Application root
└── public/
```

## Development Notes

- Bootstrapped with Create React App and TypeScript.
- Use functional components and hooks.
- API requests go through `src/services/api.ts`.
- Keep UI state in React Query or component hooks.

### Example Component

```tsx
import React from 'react';
import { apiClient } from './services/api';

export function PingButton() {
  const [msg, setMsg] = React.useState('');
  const check = async () => {
    const res = await apiClient.get<{ message: string }>('/ping');
    setMsg(res.message);
  };
  return <button onClick={check}>Ping {msg}</button>;
}
```

---
*Architecture details in `.claude/modules/frontend/architecture.md`*
